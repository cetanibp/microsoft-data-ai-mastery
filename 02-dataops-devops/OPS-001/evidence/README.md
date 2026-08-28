# OPS-001 evidence index

## Source and validation

| Evidence | Result | Link or identifier |
|---|---|---|
| Initial CI implementation | Merged | [PR #27](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/27), commit `b4954b00ac2881992262e2a42a1f508c8319224a` |
| Controlled unsafe commit | Blocked | `70da70b8e1f85622cdd9866045f4e00fd0de9894` |
| Unsafe PR validation | Failed as expected | [Run 33126491709](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33126491709) |
| Unsafe branch validation | Failed as expected | [Run 33126488739](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33126488739) |
| Safe recovery validation | Passed | [Run 33126673807](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33126673807) |
| Promotion automation | Merged | [PR #28](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/28), commit `423061366ff20b068a2648a197cf70acb98069e5` |
| Test OIDC preflight | Passed, no deployment | [Run 33211882400](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33211882400) |

## Forward promotion

| Evidence | Value |
|---|---|
| Release PR | [#29](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/29) |
| Approved commit | `42e22d4b220a13f5d06c0b4cd89401bc6e53f178` |
| Required validation | [Run 33213533680](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33213533680), passed |
| Deployment workflow | [Run 33214204525](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33214204525), passed |
| Fabric deployment ID | `eee1c50a-8178-44a6-84d9-5f30171fb4d8` |
| Fabric operation ID | `75b71a9b-1409-462b-964d-ddbe25d3e0b7`, `Succeeded` |
| Evidence artifact | `fabric-test-deploy-33214204525` |
| Artifact digest | `sha256:3c32a3f8107f5c8316cf5a2024d004da18b472d9fa2632030fc4c012ca869ff8` |
| Test verification | Test/validation/95/false, contract `1.1.0`, PASS |

## Rollback

| Evidence | Value |
|---|---|
| Revert PR | [#30](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/30) |
| Approved recovery commit | `da36f30498c3e586ea652034c9590ee264b779da` |
| Required validation | [Run 33214954854](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33214954854), passed |
| Recovery workflow | [Run 33216209623](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33216209623), passed |
| Fabric deployment ID | `555b5b15-024c-4c88-bdc7-5cbc9cf42c99` |
| Fabric operation ID | `c478dcfc-d662-45ab-9ba6-3a93afa82652`, `Succeeded` |
| Evidence artifact | `fabric-test-deploy-33216209623` |
| Artifact digest | `sha256:c6ac4df44ca0a00e5e1d9bcc1662efba3fee1883d4523d2692b20ac15ea8f39e` |
| Test verification | Test/validation/95/false, contract `1.0.0`, PASS |

## Production authorization

| Evidence | Result |
|---|---|
| Initial gate test | [Run 33216802825](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33216802825); preflight passed but reviewer rule was not enforced; no deployment |
| Corrected approval test | [Run 33217616794](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33217616794); `cetanibp` approved `production` |
| Evidence artifact | `fabric-production-preflight-33217616794` |
| Artifact digest | `sha256:12e6af369c9dcada5a6562ffc3c403fc2442409930598a5959ab1619ebeefa2c` |
| Production deployment | Not performed |

Tokens, secrets, and credential values are intentionally absent from this index.

