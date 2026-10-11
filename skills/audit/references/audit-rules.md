# Audit Rules

## Purpose

Define the source-to-image traceability contract for the final figure audit.

## Inputs

- locked master and figure specifications;
- frozen per-figure evidence packs and `spec_lock.json`;
- data-integrity and provenance records;
- approved definition substitutions and replacement definitions;
- raw, interim, and processed data;
- canonical datasets, schemas, metadata, and source maps produced by
  `/reprospec:organize`;
- source code, commands, run records, and logs;
- rendered outputs, comparison reports, limitations, rework history, and
  adjustment history.
- data inventory, canonical data, catalog, and the approved organization
  record.

## Required Lineage

Document every operation that actually changed, selected, calculated, or
rendered data for the figure. Common categories include:

- source acquisition and retrieval parameters;
- the locked `Sxx` runbook and the one-to-one run-record entry for each step;
- definition assessment and, when required, the approved `SUB-*`, replacement
  `D-*`, user decision, and known deviation;
- reproduction time-range selection and its exact start date, end date,
  timezone, and basis;
- raw-file intake, PDF or text extraction, OCR, parsing, and validation;
- normalization and canonical-dataset construction;
- cleaning, normalization, unit conversion, and missing-value handling;
- joins, key alignment, filtering, sampling, and aggregation;
- derived variables, formulas, statistical fitting, and uncertainty handling;
- panel construction, adaptive canvas sizing and the actual size used, title
  style policy and resolved family, size, and weight actually applied, title
  alignment, axes, scales, palette extraction and mark mapping, palette
  verification outcome, plot text language and wording, rendering options
  actually used, and export;
- verification, rework, adjustment, and accepted limitations.

Do not add empty categories. Do not omit a category when that operation
occurred.

The title step must show that family, size, and weight came from
`matplotlib.rcParamsDefault`, were pinned after style or theme setup, and were
not inferred from the published figure. A documented title difference from the
source is not a gap when the fixed default policy was actually applied.

The palette lineage must identify the exact vector colors or raster sampling
regions, extraction method, normalization, color-space conversion, extracted
colors, mark mapping, acceptance tolerance, and final `palette_outcome`.
Palette colors are rendering metadata and must not be represented as numeric
data, coordinates, annotations, labels, or output values.

A canonical dataset is the normal data checkpoint for reproduction, but it
does not erase upstream lineage. If a figure reads a canonical dataset, the
audit must still document how the raw PDFs, text, or spreadsheets became that
dataset.

## Computation Integrity

For every numeric constant, input value, coordinate, annotation, label, and
output value, identify whether it was computed from approved data. Published
values and digitized expected values belong only in comparison evidence. If a
published expected value was copied, hard-coded, backfilled, interpolated,
digitized, or otherwise injected into data, code, axes, annotations, labels, or
outputs, mark the figure audit `blocked` and record the exact location.

Source-derived palette colors are an explicit rendering-metadata exception.
They may be recorded as style constants for the mandatory palette contract, but
they must not be treated as or substituted for data, coordinates, annotations,
labels, or output values.

Require the figure's `verification.computation_provenance` to be
`computed_from_approved_real_data`. A missing, `copied_published_value`, or
`blocked` provenance is a critical computation-integrity gap. Do not infer a
pass from numeric agreement with the publication.

For any source item whose definition was not explicit, the audit must document
the original term, the approved `SUB-*`, the replacement `D-*`, the explicit
operational definition, and the user approval. A lineage that silently
interprets the original term, uses a different replacement definition, or
depends on unpublished user choices blocks the audit.

## Runbook and No-Reread Integrity

Before accepting the lineage:

- compare the `spec.md` and frozen evidence-pack SHA-256 with `spec_lock.json`,
  the manifest, and the run record;
- require one completed run-record entry for every `Sxx` specification step;
- compare each step's command or function, parameters, input, output,
  validation, failure action, and handoff with the locked specification;
- require every required step validation to pass;
- require `report_reread_for_requirements: false` and an empty
  `reread_events` list;
- reject any lineage that discovered a requirement by reopening the report.

A changed hash, missing step, unreported rerun, or report reread event blocks
the figure audit and sets `runbook_coverage` to `blocked`.

## Step Contract

Use sequential uppercase labels `A`, `B`, `C`, and so on. Each step must state:

1. the exact input or source;
2. the operation and why it was required;
3. parameters, code, command, and versions;
4. the exact output and its schema or units;
5. evidence proving the operation and result;
6. validation and result;
7. what the next step receives.

One letter should represent one understandable operation. Split a step when
different parameters, datasets, code paths, or outputs are involved. Combine
operations only when they are inseparable and share the same evidence.

## Reader Test

An audit passes only when a reader unfamiliar with the project can answer, for
every step, all of these questions:

- What entered this step?
- What exactly happened?
- Which code or command performed it?
- What came out?
- Why is that result trustworthy?
- How does it lead to the final figure?

If any answer is missing, the audit is incomplete.

## Gap Handling

- Never invent a source, parameter, command, or transformation.
- Never accept a published expected value as proof that a numeric output was
  computed correctly.
- Never label a missing step as completed based only on plausible intent.
- Do not use tuning or post hoc adjustments to make the lineage appear exact.
- Record the missing item, affected figure and step, and available
  counter-evidence.
- Mark the figure audit `blocked` when a critical source-to-image link cannot
  be established.
- Mark the figure audit `blocked` when a produced value depends on a copied or
  hard-coded published value instead of approved source data.
- Mark the figure audit `blocked` when a figure depends on an inferred or
  unapproved definition substitute.
- A `partial` or `blocked` figure can still have a complete audit when the
  missing reproduction step or limitation is explicitly documented and
  evidenced.
- An original removed under an approved organization decision does not create a
  gap when its path, hash, provenance, affected steps, and replacement
  organized output are recorded and verified.

## Output Contract

Write one `audits/<figure-id>.md` per included figure and one
`audit_report.md` for the paper. Update `reproduction_manifest.json` so
`audit.status` is `complete` only when every included figure audit is complete.
Record each figure under `audit.figures[<figure-id>]` as:

```json
{
  "status": "complete",
  "path": "audits/F001.md",
  "computation_integrity": "passed",
  "runbook_coverage": "complete",
  "report_reread_for_requirements": false
}
```

Use `blocked` for that figure when a critical lineage step cannot be
established or computation provenance fails. Set `computation_integrity` to
`blocked` in the same entry. Also update `audit.updated_at`, set
`workflow.active_stage` to `audit`, and set `workflow.next_stage` to `deliver`
only when the overall audit is complete.

The delivery package must preserve the audit files under `audits/` outside the
rendered figure outputs.
