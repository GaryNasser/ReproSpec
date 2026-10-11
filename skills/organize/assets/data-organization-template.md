# Data Organization Report: {{PAPER_ID}}

## Identity

- Paper ID: `{{PAPER_ID}}`
- Status: `{{STATUS}}`
- Updated at: `{{UPDATED_AT}}`

## Organization Map

Describe the raw-source corpus, canonical directory model, dataset IDs, and how
downstream reproduction can use the canonical data without repeating raw
extraction.

## Raw Source Inventory

| Source Group | Source Type | Files | Total Size | SHA-256 Coverage | Status |
| --- | --- | ---: | ---: | ---: | --- |
|  |  |  |  |  |  |

## Canonical Outputs

| Dataset ID | Canonical Format | Records | Schema | Source Map | Figures | Reuse Status |
| --- | --- | ---: | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## Dataset Catalog

Summarize the catalog and state exactly what a later stage loads instead of
the raw PDFs, text, or spreadsheets.

## Provenance

For each dataset, describe:

- raw source paths and hashes;
- extraction, OCR, parsing, normalization, and canonicalization methods;
- code, query, prompt, model, and version;
- page, paragraph, table, cell, or record locators;
- transformations and relevant audit steps.

## Coverage and Loss Audit

State what must be preserved for the final figures, audit, and reuse. List any
raw content intentionally omitted, why it is outside the required scope, and
what evidence proves that no required value was lost.

## Audit and Reuse Verification

| Check | Dataset Scope | Result | Evidence |
| --- | --- | --- | --- |
|  |  |  |  |

The verification must include:

- required-value and field coverage;
- source-locator resolution;
- value and aggregate equivalence against the raw sources;
- a clean load test that does not read the raw corpus;
- a reader test using only schema, metadata, source map, and code.

## Source Disposition Decision

- User decision (required for move, overwrite, or delete):
- User-confirmed at:
- Approved source groups:
- Exact paths:
- Recoverability:
- Evidence or data lost:

## Applied Actions

| Path | SHA-256 | Action | Result | Timestamp |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Remaining Source Data

List the retained raw sources and where each canonical dataset replaced or
supplemented it.

## Audit Handoff

State how `/reprospec:audit` can trace every canonical dataset back through
raw acquisition, extraction, OCR, parsing, normalization, and canonicalization
to the final figures. Disclose every unresolved gap.
