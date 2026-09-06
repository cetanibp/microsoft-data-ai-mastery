# Local corpus preparation — step 6

## Outcome and evidence

Implemented a Python standard-library loader and two deterministic chunking strategies for the three selected Northstar documents. [Local evidence](../evidence/local-chunk-preparation.json) records a successful run on Python 3.12.13 and 13 passing contract tests.

| Strategy | Chunks | Smallest | Largest | Total characters across chunks |
|---|---:|---:|---:|---:|
| Markdown sections | 24 | 20 | 1,230 | 8,783 |
| Fixed windows: 800 characters, 120 overlap | 15 | 135 | 800 | 10,223 |

Sizes are Unicode characters, not model tokens. Fixed windows duplicate 1,440 characters through overlap. Section chunks can be small heading-only regions or long tables; two exceed 800 characters. These are preparation measurements, not retrieval or answer-quality scores. No winner is selected.

## What a chunk is

A chunk is a passage that a search system can retrieve individually. Sending every document for every question consumes context and mixes relevant with irrelevant material. Chunking gives retrieval a smaller unit to select. These documents are small, so chunking here is principally a learning experiment, not evidence that whole-document retrieval would fail.

The loader reads only the files selected in the manifest, verifies their Git blob hashes, and then prepares both passage sets. It does not follow links, load the glossary or evaluation dataset, fetch network content, create embeddings, query an index or call a model.

## Strategies implemented

**markdown_section:** split at Markdown ATX headings outside fenced code blocks. Keep each section's exact text intact, including lists and tables within that section. Preserve the heading ancestry in metadata. The implementation supports the heading/fence forms used by these source files; it is not a complete CommonMark parser. It retains heading-only chunks as an explicit baseline limitation. There is no hard section size limit or model-token validation yet.

**fixed_window:** take up to 800 characters, then begin the next window 120 characters before the previous window ends. Overlap gives nearby passages some shared context. This deliberately simple baseline can split words, sentences, code blocks and table rows. Overlap does not guarantee that every condition and its exception are retrieved together.

The saved recovery samples make the difference concrete: the section chunk retains the complete Select a pattern table, while the first fixed window ends midway through the Metadata/configuration defect row. The full source remains covered across windows, but a single returned window may be incomplete. The quality-block row itself is intact in both saved examples.

## Lineage on each passage

Each JSONL record includes document identity and title, original pinned URL/commit/blob SHA, exact start/end character positions, section names and hierarchy, corpus/manifest versions, chunking configuration, and a deterministic chunk ID.

The chunk text is exactly the source substring between start_char (inclusive) and end_char (exclusive). Tests verify complete source coverage and exact reconstruction for section chunks. Fixed-window coverage includes overlap and should not be reconstructed by naive concatenation.

chunk_id is a SHA-256 identifier derived from the manifest hash, document/source identity, strategy/configuration and offsets. Repeating the same input produces the same IDs. A source, manifest or fixed-window setting change creates different affected IDs.

Declared policy/classification fields are carried as metadata only. Every output is labeled offline_draft_study, runtime_eligible=false, authorization_verified=false and current_freshness_verified=false. The program has no approved/production-serving mode. Copying role names into a chunk does not enforce them.

## Reproduce locally

Use Python 3.10 or later; no pip install, Azure resources or credentials are required. Run these commands from the repository root on this PR branch. The source files must match the manifest hashes byte-for-byte; use a checkout preserving Git's LF content if line-ending conversion changes the files. Never edit expected hashes merely to suppress a mismatch.

```bash
python -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -v
python 04-foundry-ai-engineering/AI-001/runtime/prepare_corpus.py --repo-root . --allow-draft-local
```

The second command creates three files under AI-001/generated: markdown_section.jsonl, fixed_window.jsonl and summary.json. JSONL means one JSON record per line. Generated files and Python bytecode are ignored by the AI-001 .gitignore; the small reviewed evidence report is committed separately.

The loader requires the explicit local-study flag because the manifest remains a draft. This authorizes only local preparation of the selected synthetic lab documents, not serving them to users or bypassing future access controls. It also refuses a manifest claiming runtime_ready=true. Document/policy approval and all runtime gates remain open.

All input verification and both chunk sets are computed before writing outputs. Existing generated output filenames are never overwritten. To repeat a CLI run, first move the previous generated directory to a separate local comparison location, then run again. A filesystem failure during writing can leave partial local output; the program exits unsuccessfully, and that output must not be treated as a completed run.

## What the tests establish

The 13 tests cover explicit draft-local mode, refusal of live readiness, changed or missing sources, duplicate document IDs, escaping paths/symlinks, unpinned citation URLs, full content coverage, source lineage, stable and strategy-specific IDs, Unicode/overlap boundaries, headings inside fenced code, and preservation of the recovery table and State section.

This is local executable evidence. It does not verify current Git branch freshness, document approval, user identity, ACLs, revocation, embeddings, retrieval relevance, model answers or cloud deployment. The Git blob check verifies local file contents against the manifest; the loader does not independently contact GitHub to prove commit membership. The initial source membership and hashes were read from the pinned GitHub revision when preparing the manifest.

No reserved evaluation questions were used. The 30-question dataset and rubric remain unchanged. Changing chunk sizes later is a development experiment and must preserve input/configuration versions.

## Learning resources

Read [Microsoft: Chunk large documents for RAG](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents), especially Common chunking techniques and Content overlap considerations. It describes fixed-size and structure-based approaches and why overlap can help. Our 800/120 character settings are a small Northstar experiment, not a Microsoft standard or a proven optimum. Resource checked September 6, 2026.

## Your checkpoint

Compare the saved markdown_section and fixed_window samples in the [evidence JSON](../evidence/local-chunk-preparation.json). Find text, source_sections and source_url. Ask which context a future retriever must return to explain a recovery decision completely.

Next: implement a local keyword-retrieval baseline over both chunk sets and inspect development-question evidence matches. Vector/hybrid retrieval and model answers follow after the local contract is understood. An actual retrieval/answer application must enforce approval, freshness and user/workload authorization; this local-study program is not that application.
