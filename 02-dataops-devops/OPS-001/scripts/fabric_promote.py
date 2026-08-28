#!/usr/bin/env python3
"""Preflight or promote content through a Microsoft Fabric deployment pipeline."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


API_ROOT = "https://api.fabric.microsoft.com/v1"
TERMINAL_SUCCESS = {"succeeded", "completed"}
TERMINAL_FAILURE = {"failed", "cancelled", "canceled"}


class FabricApiError(RuntimeError):
    """A sanitized Fabric API failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def request_json(
    method: str,
    url: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode("utf-8")
            payload = json.loads(raw) if raw.strip() else {}
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.status, payload, headers
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        try:
            details = json.loads(raw)
            message = details.get("message") or details.get("error", {}).get("message")
        except json.JSONDecodeError:
            message = None
        raise FabricApiError(
            f"Fabric API {method} request failed with HTTP {error.code}"
            + (f": {message}" if message else "")
        ) from error
    except urllib.error.URLError as error:
        raise FabricApiError(f"Fabric API {method} request could not be completed") from error


def resolve_stage(stages: list[dict[str, Any]], requested_name: str) -> dict[str, Any]:
    matches = [
        stage
        for stage in stages
        if str(stage.get("displayName", "")).casefold() == requested_name.casefold()
    ]
    if len(matches) != 1:
        raise FabricApiError(
            f"Expected one stage named '{requested_name}', found {len(matches)}"
        )
    return matches[0]


def stage_summary(stage: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": stage.get("id"),
        "name": stage.get("displayName"),
        "order": stage.get("order"),
        "workspace_id": stage.get("workspaceId"),
    }


def poll_operation(location: str, token: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        _, payload, headers = request_json("GET", location, token)
        status = str(payload.get("status", "")).casefold()
        if status in TERMINAL_SUCCESS:
            return payload
        if status in TERMINAL_FAILURE:
            raise FabricApiError(f"Fabric deployment ended with status '{status}'")
        retry_after = int(headers.get("retry-after", "10"))
        time.sleep(max(1, min(retry_after, 30)))
    raise FabricApiError(f"Fabric deployment did not finish within {timeout_seconds} seconds")


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-id", required=True)
    parser.add_argument("--source-stage", required=True)
    parser.add_argument("--target-stage", required=True)
    parser.add_argument("--target-workspace-id", required=True)
    parser.add_argument("--mode", choices=("preflight", "deploy"), default="preflight")
    parser.add_argument("--note", default="")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = os.environ.get("FABRIC_ACCESS_TOKEN", "")
    report: dict[str, Any] = {
        "status": "FAIL",
        "mode": args.mode,
        "pipeline_id": args.pipeline_id,
        "target_workspace_id": args.target_workspace_id,
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "github_run_url": (
            f"{os.environ.get('GITHUB_SERVER_URL')}/{os.environ.get('GITHUB_REPOSITORY')}"
            f"/actions/runs/{os.environ.get('GITHUB_RUN_ID')}"
        ),
        "started_at_utc": utc_now(),
    }

    try:
        if not token:
            raise FabricApiError("FABRIC_ACCESS_TOKEN is not set")

        _, stage_payload, _ = request_json(
            "GET", f"{API_ROOT}/deploymentPipelines/{args.pipeline_id}/stages", token
        )
        stages = stage_payload.get("value", [])
        source = resolve_stage(stages, args.source_stage)
        target = resolve_stage(stages, args.target_stage)

        source_order = int(source.get("order"))
        target_order = int(target.get("order"))
        if target_order != source_order + 1:
            raise FabricApiError("Source and target stages are not adjacent and forward-moving")
        if str(target.get("workspaceId", "")).casefold() != args.target_workspace_id.casefold():
            raise FabricApiError("Target stage workspace does not match FABRIC_TARGET_WORKSPACE_ID")

        request_json("GET", f"{API_ROOT}/workspaces/{args.target_workspace_id}", token)
        report.update({"source_stage": stage_summary(source), "target_stage": stage_summary(target)})

        if args.mode == "deploy":
            note = args.note.strip() or (
                f"GitHub Actions run {os.environ.get('GITHUB_RUN_ID')} at "
                f"commit {os.environ.get('GITHUB_SHA')}"
            )
            status_code, deployment, headers = request_json(
                "POST",
                f"{API_ROOT}/deploymentPipelines/{args.pipeline_id}/deploy",
                token,
                {
                    "sourceStageId": source["id"],
                    "targetStageId": target["id"],
                    "note": note[:1024],
                },
            )
            report["deployment_id"] = headers.get("deployment-id")
            report["operation_id"] = headers.get("x-ms-operation-id")
            report["initial_http_status"] = status_code
            if status_code == 202:
                location = headers.get("location")
                if not location:
                    raise FabricApiError("Fabric accepted deployment without an operation URL")
                operation = poll_operation(
                    urllib.parse.urljoin(API_ROOT + "/", location),
                    token,
                    args.timeout_seconds,
                )
                report["operation_status"] = operation.get("status")
            else:
                report["operation_status"] = deployment.get("status", "Succeeded")

        report["status"] = "PASS"
        report["completed_at_utc"] = utc_now()
        write_report(args.report, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except (FabricApiError, KeyError, TypeError, ValueError) as error:
        report["error"] = str(error)
        report["completed_at_utc"] = utc_now()
        write_report(args.report, report)
        print(json.dumps(report, indent=2, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
