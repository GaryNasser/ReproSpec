---
name: "organize"
description: "Consolidate large raw-source collections into canonical datasets that preserve approved definition substitutions, source mappings, and all values needed for later reproduction, audit, and reuse. Use after /reprospec:rework and /reprospec:adjust, before /reprospec:audit. Discuss and obtain explicit approval before disposing of raw sources. Do not use for generic compression, lossy summarization, repair, or final packaging."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.5.0"
---

## User Input

Use invocation arguments to select source corpora, raw-source paths, dataset
IDs, figure IDs, or organization scope. If no scope is supplied, organize every
raw source and intermediate artifact that the final reproduction still needs
to read or process.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `confirmed`, `selection` is `publication_period` or `through_today`,
  `user_confirmed` is true, and exact ISO start and end dates, timezone, and
  basis are recorded.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false.
- If the Init policy is missing or relaxed, stop and return to
  `/reprospec:init`. If `time_range_policy.status` is not `confirmed` or the
  exact window is invalid, stop and return to `/reprospec:analyse`. Never
  continue by using a publication value or by bypassing the `supplement_data`
  or `skip` decision.
- No included figure is `draft` or `stale`.
- Verification results, rework and adjustment decisions, run records, and
  data-integrity records are available.
- Extraction code, queries, prompts, OCR or parsing versions, mappings, and
  source locators are available for every raw-source type.
- The raw sources are not currently required by an unresolved repair.
- The selected paper, published evidence, and files needed to audit the
  extraction are treated as evidence rather than disposable raw input.
- No expected published value has been copied, digitized, interpolated, or
  backfilled into a canonical dataset.
- No original data has been moved, overwritten, or deleted for this
  organization round.

## Goal

Replace a large, expensive-to-reprocess collection of raw sources with one or
more canonical datasets under `work/<paper-id>/data/organized/`. Typical inputs
are PDFs, text files, OCR output, HTML, spreadsheets, tables, and intermediate
extracts; typical outputs are JSON, Parquet, CSV, SQLite, or another suitable
loadable format.

The checkpoint is reached only when later reproduction can load the canonical
dataset without parsing the raw PDFs or text again. This is not generic
compression or lossy summarization. Every canonical dataset must be:

- complete for the values, fields, relationships, and source evidence required
  by the final figures, audit, and intended reuse;
- explicit about the replacement definition and `SUB-*` origin of every field
  derived from an approved substitution;
- loadable and understandable without hidden project knowledge;
- traceable to the exact raw sources and extraction operations that produced
  each important record or field;
- reproducible through recorded extraction code, parameters, model versions,
  and validation evidence.

Raw content that is not needed for figure values, audit, or reuse may be
omitted only when that scope decision is explicit and verified. Never discard
a value or source link that is still required.

Do not move, overwrite, or delete original data until the user has reviewed
the exact source paths, dependencies, verification evidence, consequences, and
recovery options, and has explicitly approved that disposition.

## Execution Steps

1. Resolve the organization scope.
2. Run `scripts/inventory_data.py` to record raw and intermediate files, sizes,
   hashes, scope, and duplicate relationships.
3. Identify how each raw-source type is converted into records: parser, OCR,
   query, model, prompts, versions, parameters, and page, paragraph, table,
   cell, or record locators.
4. Define the canonical schema, dataset boundaries, keys, units, coverage, and
   what the canonical dataset must contain for the final figures and audit.
   Preserve the replacement `D-*`, linked `SUB-*`, explicit definition, source
   field, and known deviation for every substituted field.
5. Assign stable dataset IDs such as `DATA-001`. Organize datasets by meaning
   and reuse contract rather than by original filenames or processing order.
6. Create one directory per canonical dataset under
   `data/organized/<dataset-id>/`. Include `data.<ext>`, `schema.json`,
   `metadata.json`, and `checksums.sha256`. Add a row-level source map when the
   metadata alone cannot show where each important record came from.
7. Preserve every required value, field relationship, unit, qualifier, and
   source locator. Preserve definition-substitution metadata and do not replace
   an approved substitute with a later inferred interpretation. Do not sample,
   aggregate, filter, summarize, or apply a
   lossy transformation merely to reduce size. Any required transformation
   must be explicit, reproducible, and validated.
8. Verify the canonical data against the raw sources and existing reproduction
   outputs for schema, keys, row count, units, coverage, missingness, required
   aggregates, and source-locator resolution.
9. Load and test the canonical dataset without reading the raw PDFs or text.
   Confirm that another analyst can interpret it from the schema, metadata,
   source map, and reuse notes.
10. Fill `data_catalog.csv` with stable identifiers, canonical paths, source
    hashes, organized hashes, source maps, figure links, audit links, schema,
    metadata, definition substitutions, and reuse status.
11. Write `data_organization.json` and `data_organization.md` with the raw
    source inventory, canonical dataset map, extraction methods, provenance,
    verification results, and source-disposition decision.
12. If any raw source is proposed for deletion, movement, or overwrite,
    present a source-disposition decision and wait for explicit approval.
13. Apply only approved source-disposition actions. Retaining raw sources is a
    valid outcome and does not block completion.
14. Update the manifest organization status, decision, source count, canonical
    formats, dataset count, and paths. Set the next stage to `audit` only when
    every canonical dataset passes the coverage, audit, and reuse checks.

## References

Read [references/organization-rules.md](references/organization-rules.md) for
raw-to-canonical design, source maps, coverage validation, audit handoff,
source disposition, and the output contract.

## Decision Protocol

When original-source disposal requires approval:

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | Source Data Disposition**` label, a context block, an
options table, and a recommended option.

1. List the exact original paths, hashes, and current size.
2. State which canonical dataset replaces each source and where it is stored.
3. Explain how source-to-canonical coverage and value equivalence were
   verified.
4. Identify extraction steps, source locators, affected figures, audit links,
   reuse contracts, and legal or retention requirements.
5. Explain what would be lost and whether the action is reversible.
6. Recommend preserving the original sources unless the user has a concrete
   reason to remove or move them.
7. Ask exactly one disposition question for the listed group and wait.

Do not combine unrelated source groups with different retention requirements.
Do not modify original data before the user answers.
Never include the selected paper itself or other required audit evidence in a
raw-data disposal group.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 10/12 | ORGANIZE**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Raw sources inventoried | `<count>` |
| Canonical datasets | `<count>` |
| Canonical formats | `<json|parquet|csv|...>` |
| Source-linked records | `<count>` |
| Audit-linked datasets | `<count>` |
| Reuse-ready datasets | `<count>` |
| Source disposition | `<retain|move|delete|mixed>` |

**Artifacts**

- `work/<paper-id>/data/organized/`
- `work/<paper-id>/data_organization.json`
- `work/<paper-id>/data_catalog.csv`
- `work/<paper-id>/data_organization.md`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:audit`
>
> **Reason:** The canonical datasets contain the required reproduction values and can be traced to their raw sources without repeating raw extraction.
```

If a required value is absent, a source link cannot be established, the
canonical data cannot be loaded without raw processing, or the
source-disposition decision is unresolved, use `Status: blocked` and do not
identify `/reprospec:audit` as the next action.

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Canonical data must preserve the exact
  user-confirmed reproduction time range.
- Treat the canonical dataset as the reproducible data checkpoint, not merely
  a smaller copy of the raw corpus.
- Do not repeat PDF, OCR, text, or spreadsheet extraction downstream when the
  canonical dataset already provides the required data.
- Do not use lossy sampling, aggregation, filtering, summarization, or
  compression merely to reduce file size or file count.
- Do not build canonical values from expected numbers in the paper or report.
  They are comparison targets, not source records.
- Every canonical dataset must have a stable dataset ID, schema, metadata,
  checksums, source links, and catalog entry.
- Every substituted field must retain its `SUB-*`, replacement `D-*`, explicit
  definition, source field, and known deviation in the schema or metadata.
- Preserve page, paragraph, table, cell, or record locators for important
  extracted values when they are needed to audit the extraction.
- Preserve source hashes and lineage after any approved original removal.
- Never dispose of a raw source without explicit user approval.
- Treat silence, non-response, implied consent, and ambiguous approval as
  refusal to dispose.
- Never delete or overwrite a path outside the approved workspace root.
- Never include the selected paper, audit evidence, or generated canonical
  datasets in an approved raw-source disposal.
- Never use wildcard or recursive deletion for an approved disposal.
- Keep canonical datasets usable without the original filenames, raw-source
  parsing pipeline, or temporary processing order.
- Never store credentials or secret values.
- Generated catalogs, metadata, records, and reports must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Every raw source is inventoried, hashed, and classified.
- [ ] Every canonical dataset has data, schema, metadata, checksums, and
      required source links.
- [ ] Every approved definition substitution remains explicit and traceable in
      the canonical schema, metadata, or source map.
- [ ] `data_catalog.csv` connects raw sources, extraction methods, canonical
      data, figures, and audits.
- [ ] No expected published value was copied or backfilled into canonical data.
- [ ] The canonical data loads and supports the final figures without reading
      the raw PDFs or text again.
- [ ] Coverage, source-location, audit, and reuse checks pass without relying
      on hidden knowledge.
- [ ] Every original has a recorded disposition; any move, overwrite, or
      deletion has explicit user approval.
- [ ] The manifest organization status and next stage are accurate.
- [ ] A completed organization identifies `/reprospec:audit` as the next stage.
