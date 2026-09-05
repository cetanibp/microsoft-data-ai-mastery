# Learning-gap review — September 5, 2026

## Decision and scope

The repository review identified a strong completed Fabric foundation and a lightly specified AI, governance, API, and capstone backlog. The user authorized adding all recommendations to issues and updating repository documents. The resulting change expands all 14 previously open issues and adds 10 work items: four principal builds, three delivery/review/maintenance follow-ups, and three optional advanced extensions.

This is a planning update. Phase 0 and Phase 1 remain complete; no implementation, independent review, new skill achievement, or production readiness is claimed. Existing scorecard values and historical evidence remain unchanged. GitHub issue state is authoritative after this dated snapshot.

## Recommendation coverage

| Recommendation | Tracked implementation/evidence | Priority and sequence |
|---|---|---|
| Retrieval alternatives, chunking, lifecycle, denied/unanswerable queries | [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13) | Next build, after minimum governance slice |
| Typed tools, bounded workflow, direct API versus authenticated MCP | [#14](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/14), [#15](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/15) | Read-only before consequential tools |
| Early evaluation, held-out cases, versioning, latency/cost and regression gates | [#16](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/16), [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13) | Dataset/rubric before tuning; agent gates as implementation matures |
| Exact-action approvals, revocation, state checks, replay prevention | [#17](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/17) | Required before consequential lab execution |
| Discoverable semantics, ownership, lineage, retention, access propagation | [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20) | Minimum corpus/policy slice early; full product later |
| API compatibility, pagination, throttling, delegated identity | [#21](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/21) | After implemented governed product |
| Azure infrastructure, hosted AI deployment and rollback | [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45) | Alongside AI baseline and delivery work |
| Star schema, historical dimensions, measures, semantic security and performance | [#46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46) | AI-ready data phase |
| Actual pipeline-to-monitor-to-agent events and governed alert routing | [#47](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47) | Producer slice before live diagnosis; final proof jointly with #15 |
| Explicit integrated capstone implementation | [#48](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/48) | After #23 plan and component contracts |
| Automated deployment validation, drift, selective deployment, state migration | [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) | Build on completed OPS-001; coordinate with #45 |
| Architecture conditions, ADR evidence gaps, level-4/5 reassessment | [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) | Initial Phase 1 review early; revisit at milestones |
| RTI CI, executable KQL regression, tracked bytecode cleanup | [#51](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/51) | Small maintenance increments |
| Restoration of data and control state; migration/cutover; measured recovery | [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23), [#24](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/24), [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) | Plan, implement, then rehearse on #48 deployment |
| Manual-versus-agent diagnosis and defensible cost/business claims | [#15](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/15), [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23), [#25](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/25) | Baseline protocol early; measured briefing later |
| CDC, deletes, key changes and source evolution | [#52](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/52) | Optional P2 extension |
| Spark/Delta layout and second-workload tuning | [#53](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/53) | Optional P2 extension |
| Companion-workload contention, dollar allocation and FinOps feedback | [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) | Optional P2 extension; #23 still owns baseline costs |
| Explicit evidence for advancement beyond level 3 | [Scorecard](../SKILLS.md), [working agreement](../CONTRIBUTING.md), [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) | Second scenario, independent troubleshooting, quantified tradeoffs, and handoff |

## New work items

| Issue | Outcome | Priority | Parent epic | Scope |
|---|---|---|---|---|
| [AI-002 / #45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45) | Deploy the AI application with reproducible Azure infrastructure | P1 | [#12](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12) | Required follow-up |
| [DATA-002 / #46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46) | Build an analytical data product and tested semantic model | P1 | [#18](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/18) | Required follow-up |
| [RTI-002 / #47](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47) | Connect operational pipelines to real-time monitoring and diagnosis | P1 | [#12](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12) | Required follow-up |
| [CAP-004 / #48](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/48) | Build and deploy the integrated enterprise capstone | P1 | [#22](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22) | Required follow-up |
| [OPS-003 / #49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) | Automate deployment verification, drift checks, and state migration | P1 | [#12](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12) | Required follow-up |
| [ARCH-004 / #50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) | Reassess architecture decisions and close evidence gaps | P1 | [#22](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22) | Required follow-up |
| [OPS-004 / #51](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/51) | Close repository hygiene and RTI regression coverage gaps | P1 | [#12](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12) | Required follow-up |
| [FAB-005 / #52](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/52) | Extend ingestion with CDC, deletes, and source evolution | P2 | [#22](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22) | Optional extension |
| [FAB-006 / #53](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/53) | Tune Spark and Delta layouts across a second workload | P2 | [#22](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22) | Optional extension |
| [FIN-001 / #54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) | Measure shared-capacity contention and operational FinOps | P2 | [#22](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22) | Optional extension |

All new items have area/type/priority/effort labels and one of the existing open milestones. No completed milestone or epic was reopened. Parent links and epic checklists establish issue-level traceability; GitHub Project board fields were not changed by this update.

## Execution sequence

1. **Minimum governance prerequisite:** in #19/#20, define approved corpus ownership, operational glossary, freshness, identity/classification, and allowed/denied retrieval access. Publish readiness evidence without waiting for either full issue to close.
2. **Next build: #13.** Start the #16 dataset, rubric, held-out cases, and thresholds before tuning retrieval. #45 may prepare the deployment skeleton against stable interfaces.
3. **Read-only agent:** #14 tool contracts, then #15 bounded diagnosis. #47 emits actual lab pipeline events before the final live diagnosis demonstration; #15 and #47 share that final integration gate, avoiding circular whole-issue prerequisites.
4. **Release and controls:** complete #16 regression enforcement, #17 execution authorization, #45 application delivery, #49 Fabric hardening, and #51 RTI regression maintenance.
5. **Governed analytical product:** complete #19/#20, build #46, then publish #21.
6. **Capstone:** #23 plan → #48 build/deploy → #24 restoration/cutover/review → #25 evidence-based presentations. Start #50's existing-evidence review earlier and complete reassessment as the integrated evidence becomes available.
7. **Optional depth:** select #52–#54 when they address the next material skill gap. They are not prerequisites for #13 or core capstone closure.

Keep no more than two issues in progress. Each implementation increment should produce reviewable evidence within two weeks; split oversized slices before starting. Milestone dates remain planning horizons, not reasons to delay ready work. Optional extensions may be moved to a later horizon if needed; core capstone completion and GitHub milestone closure are distinct when optional issues remain open.

## Evidence and review cadence

Issue completion requires acceptance evidence and a retrospective. Scores do not increase because scope was expanded. Level 4 requires transfer to a second materially different scenario, independently diagnosed failure/regression, and quantified alternatives. Level 5 additionally requires reusable standards, mentoring or handoff, and a defended decision with reviewer feedback.

A monthly ChatGPT review was scheduled separately for the first of each month around 8 a.m. America/Los_Angeles, starting October 1, 2026. It reads current repository evidence and recommends changes for review; it does not authorize automatic repository mutations. The existing monthly score reassessment and quarterly architecture-review cadence remain in force.

## Current learning references

Use the current supported product/SDK capabilities at implementation time; record preview, region, identity, and lab-access limitations. These references support learning choices, not claims of implemented capability:

- [Microsoft Foundry retrieval and grounding](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation)
- [Microsoft Foundry agent evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators)
- [Authenticated MCP tool integration](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/model-context-protocol)
- [Fabric infrastructure and deployment automation](https://learn.microsoft.com/en-us/fabric/cicd/tutorial-end-to-end-automation)
- [Direct Lake security integration](https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-security-integration)
