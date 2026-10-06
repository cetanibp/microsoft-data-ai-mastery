#!/usr/bin/env bash
set -euo pipefail
: "${SEARCH_ENDPOINT:?Set SEARCH_ENDPOINT to the lab search endpoint}"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export LAB_SPEC="$(cygpath -m "$script_dir/development-retrieval-batch-03.json")"
lab_root="${LAB_ROOT:-$HOME/NorthstarLab}"
mkdir -p "$lab_root"
lab_dir="$(mktemp -d "$lab_root/clarification-batch-XXXXXX")"
export LAB_OUTPUT="$(cygpath -m "$lab_dir")"
python - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ["LAB_OUTPUT"])
spec = json.loads(Path(os.environ["LAB_SPEC"]).read_text(encoding="utf-8"))
(out / "spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=True), encoding="utf-8")
for c in spec["cases"]:
    request = dict(spec["query_settings"], search=c["question"])
    (out / (c["case_id"] + ".request.json")).write_text(json.dumps(request, ensure_ascii=True), encoding="utf-8")
(out / "jobs.txt").write_text("\n".join(c["case_id"] for c in spec["cases"]) + "\n", encoding="ascii", newline="\n")
PY
while IFS= read -r case_id; do
  case_id="${case_id%  MSYS_NO_PATHCONV=1 az rest --method post \
    --url "${SEARCH_ENDPOINT%/}/indexes/northstar-ops-markdown-h2-v1/docs/search?api-version=2026-04-01" \
    --resource "https://search.azure.com" --headers "Content-Type=application/json" \
    --body "@${LAB_OUTPUT}/${case_id}.request.json" --output json > "$lab_dir/$case_id.raw.json"
done < "$lab_dir/jobs.txt"
python - <<'PY'
import json, os
from pathlib import Path
from datetime import datetime, timezone
out = Path(os.environ["LAB_OUTPUT"])
spec = json.loads((out / "spec.json").read_text(encoding="utf-8"))
results = []
for c in spec["cases"]:
    raw = (out / (c["case_id"] + ".raw.json")).read_bytes()
    try:
        decoded = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        decoded = raw.decode("cp1252")
        encoding = "cp1252"
    response = json.loads(decoded)
    docs = response["value"]
    assert all(d.get("runtime_eligible") is False for d in docs), "Unexpected eligibility"
    (out / (c["case_id"] + ".normalized.json")).write_text(json.dumps(response, indent=2, ensure_ascii=True), encoding="utf-8")
    evidence = []
    for e in c["required_evidence"]:
        match = next(((i,d) for i,d in enumerate(docs,1) if d.get("document_id")==e["document_id"] and d.get("heading_h2")==e["heading_h2"]), None)
        evidence.append(dict(e, rank=match[0] if match else None, text=match[1]["text"] if match else None))
    results.append(dict(case_id=c["case_id"], variant=c["variant"], question=c["question"],
        response_encoding=encoding, match_count=response.get("@odata.count"),
        required_evidence=evidence, all_required_chunks_in_top5=all(e["rank"] is not None for e in evidence),
        all_returned_runtime_eligible_false=True,
        ranking=[dict(rank=i,document_id=d["document_id"],heading_h2=d.get("heading_h2"),score=d.get("@search.score")) for i,d in enumerate(docs,1)]))
summary = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(), local_directory=str(out),
    evaluation_scope="retrieval_only", azure_configuration_changed=False, results=results)
(out / "batch-summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=True))
PY
\r'}"
  MSYS_NO_PATHCONV=1 az rest --method post \
    --url "${SEARCH_ENDPOINT%/}/indexes/northstar-ops-markdown-h2-v1/docs/search?api-version=2026-04-01" \
    --resource "https://search.azure.com" --headers "Content-Type=application/json" \
    --body "@${LAB_OUTPUT}/${case_id}.request.json" --output json > "$lab_dir/$case_id.raw.json"
done < "$lab_dir/jobs.txt"
python - <<'PY'
import json, os
from pathlib import Path
from datetime import datetime, timezone
out = Path(os.environ["LAB_OUTPUT"])
spec = json.loads((out / "spec.json").read_text(encoding="utf-8"))
results = []
for c in spec["cases"]:
    raw = (out / (c["case_id"] + ".raw.json")).read_bytes()
    try:
        decoded = raw.decode("utf-8-sig")
        encoding = "utf-8-sig"
    except UnicodeDecodeError:
        decoded = raw.decode("cp1252")
        encoding = "cp1252"
    response = json.loads(decoded)
    docs = response["value"]
    assert all(d.get("runtime_eligible") is False for d in docs), "Unexpected eligibility"
    (out / (c["case_id"] + ".normalized.json")).write_text(json.dumps(response, indent=2, ensure_ascii=True), encoding="utf-8")
    evidence = []
    for e in c["required_evidence"]:
        match = next(((i,d) for i,d in enumerate(docs,1) if d.get("document_id")==e["document_id"] and d.get("heading_h2")==e["heading_h2"]), None)
        evidence.append(dict(e, rank=match[0] if match else None, text=match[1]["text"] if match else None))
    results.append(dict(case_id=c["case_id"], variant=c["variant"], question=c["question"],
        response_encoding=encoding, match_count=response.get("@odata.count"),
        required_evidence=evidence, all_required_chunks_in_top5=all(e["rank"] is not None for e in evidence),
        all_returned_runtime_eligible_false=True,
        ranking=[dict(rank=i,document_id=d["document_id"],heading_h2=d.get("heading_h2"),score=d.get("@search.score")) for i,d in enumerate(docs,1)]))
summary = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(), local_directory=str(out),
    evaluation_scope="retrieval_only", azure_configuration_changed=False, results=results)
(out / "batch-summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=True),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=True))
PY
