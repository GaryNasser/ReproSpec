# Data Organization Rules

## Purpose

Define how ReproSpec replaces a large, expensive-to-reprocess raw-source
collection with canonical, auditable, reusable datasets. The objective is not
generic compression; it is to make the canonical dataset the normal input for
later reproduction and audit.

## Inputs

- raw PDFs, text files, OCR output, HTML, spreadsheets, tables, and similar
  source collections;
- interim extracts, processed data, and figure-local data;
- master and figure specifications;
- data-integrity and provenance records;
- approved definition substitutions and replacement definitions;
- parsers, OCR models, queries, prompts, versions, run records, source hashes,
  code, and logs;
- verification, limitations, rework, adjustment, and audit requirements.

## Dataset Design

Use stable IDs such as `DATA-001`. Store each canonical dataset under:

```text
data/organized/<dataset-id>/
|-- data.json                 # Or data.parquet, data.csv, or another loadable format
|-- schema.json
|-- metadata.json
|-- source-map.jsonl          # Optional when row-level provenance is needed
`-- checksums.sha256
```

Choose the canonical format by access pattern:

- Parquet for large tabular or columnar datasets;
- JSON or JSONL for nested records and explicit source mappings;
- CSV for simple tabular data that does not need typed storage;
- SQLite or another documented format when relational queries are required.

The dataset boundary must follow meaning and reuse, not raw folder order. A
dataset may combine many source files only when the resulting schema, keys,
units, coverage, and per-record provenance remain explicit.

The canonical checkpoint is successful only when a downstream process can load
`data.<ext>` without parsing the original PDFs or text again.

Canonical values must come from approved source records, extraction code, and
documented transformations. Expected numbers printed in the paper or report
are comparison targets only and must not be copied, digitized, interpolated, or
backfilled into a canonical dataset.

Fields derived from an approved substitution must retain the original field,
replacement field, `SUB-*`, explicit replacement definition, source field,
functional rationale, and known deviation in the schema, metadata, or source
map. Organization must not erase the reason a field exists or replace it with a
later guessed interpretation.

## Audit-and-Reuse Invariants

A canonical dataset is complete for the documented scope only when:

- every value, field, relationship, qualifier, and aggregate required by the
  final figures, audit, or stated reuse case is present;
- every substituted field retains its approved definition contract and source
  mapping;
- schema, keys, units, coverage, and missing-value behavior are documented;
- raw source paths and hashes are recorded;
- extraction and transformation code, parameters, model versions, and prompts
  are traceable;
- important records and fields link to page, paragraph, table, cell, record,
  or other source locators;
- figure IDs and audit steps are linked;
- a new analyst can load and interpret it without raw-source knowledge;
- a clean load test succeeds without reading the original raw files;
- checksums verify after writing.

Do not sample, aggregate, filter, summarize, or apply lossy transformations
merely to reduce size or file count. If a required reduction is part of the
analytical result, it must be reproducible and documented.

Raw text or source content outside the declared scope may be omitted only when
the scope, coverage, and verification evidence show that it is not required by
the final figures, audit, or intended reuse.

## Source Map Contract

Record enough information to answer where an important canonical value came
from:

- canonical dataset ID and record or field;
- raw source path and SHA-256;
- page, paragraph, table, cell, section, line, timestamp, or record locator;
- extraction method, code path, version, parameters, and prompt or query when
  applicable;
- validation that connects the raw location to the canonical value.

Metadata may contain the source map for small datasets. Use
`source-map.jsonl` or another documented file when row-level mappings would
make metadata unwieldy. `metadata.json` must point to that file.

Validate the source map before any approved raw-source disposal. After a
source is removed, the recorded path, hash, extractor version, and locator
remain the historical provenance for the canonical record.

For example, a PDF corpus may become one Parquet dataset while
`source-map.jsonl` records a row such as:

```json
{
  "record_id": "OBS-1042",
  "source_path": "workspace/inputs/reports/2024.pdf",
  "source_sha256": "<sha256>",
  "locator": "page=17; table=3; row=8; column=value",
  "extractor": "scripts/extract_report_table.py",
  "version": "<commit-or-version>",
  "validation": "table total matched report total"
}
```

## Catalog Contract

`data_catalog.csv` is the index for discovery and reuse. Each row must identify:

- dataset ID, title, role, canonical format, and organized path;
- row and column counts;
- schema and metadata paths;
- raw source paths and hashes;
- source-map path;
- organized checksum;
- related figures and audit steps;
- linked definition substitutions and replacement fields;
- reuse status and last verification.

## Audit Handoff

For every dataset, the organization record must state which audit steps can use
it, how raw sources were converted into canonical records, which source
locators are preserved, and where extraction and transformation code is
implemented.

An audit must still document the upstream steps from raw acquisition through
extraction, OCR, parsing, normalization, and canonicalization. Loading a
canonical dataset is a checkpoint, not a reason to omit how that dataset was
created.

## Source Disposition Approval

No original-source deletion, overwrite, move, or irreversible transformation is
allowed before explicit user approval.

The selected paper, published evidence, and artifacts required to audit an
extraction are evidence. Do not treat them as ordinary disposable raw input,
even when they are stored beside the raw corpus.

Before asking, show:

- exact source paths and hashes;
- the canonical replacement dataset and formats;
- source coverage and value-equivalence verification results;
- extraction steps and source-locator coverage;
- affected figures, audit links, and reuse contracts;
- retention or legal requirements;
- what becomes unavailable and whether the action is reversible.

Ask one question per source group. If approval is missing or ambiguous, retain
the original. Retention is a valid outcome.

## Safe Source Changes

After approval:

1. resolve each target to an absolute path;
2. verify it is inside the approved workspace root;
3. verify it is not the selected paper, audit evidence, an extraction input
   still required for verification, or a generated canonical dataset;
4. confirm it exactly matches the approved list;
5. verify the canonical replacement, source map, coverage, and checksums;
6. change only those exact paths;
7. record the action and result.

Never use a wildcard, unresolved variable, or recursive directory delete.
Never remove inventory, catalog, schema, metadata, code, logs, or audit
evidence.

## Manifest Contract

Update `reproduction_manifest.json`:

```json
{
  "organization": {
    "status": "complete",
    "inventory": "data_inventory.csv",
    "catalog": "data_catalog.csv",
    "report": "data_organization.md",
    "record": "data_organization.json",
    "organized_path": "data/organized",
    "raw_source_count": 1200,
    "dataset_count": 3,
    "canonical_formats": ["parquet", "json"],
    "canonical_checkpoint": true,
    "source_disposition": "retain|move|delete|mixed",
    "user_decision": "<recorded user response>",
    "user_approved": false,
    "include_raw_in_delivery": false,
    "updated_at": "<timestamp>"
  }
}
```

Set `user_approved` to `true` only after a recorded user decision when source
disposition is `move`, `delete`, or `mixed`; leave it `false` for `retain`. A
`retain` decision is valid without approval and does not block completion. Set
the overall status to `complete` only when every dataset passes the
audit-and-reuse checks.

## Output Contract

Produce:

- `data_inventory.csv`;
- `data_catalog.csv`;
- `data_organization.json`;
- `data_organization.md`;
- `data/organized/<dataset-id>/` with canonical data, schema, metadata,
  checksums, and required source maps.

Set `workflow.next_stage` to `audit` only when organization is complete.
