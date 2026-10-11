# Reproduction Rules

## Purpose

Define provenance, execution, artifact, and failure requirements for locked
figure reproduction.

## Inputs

- the locked master and figure specifications;
- the frozen `evidence/<figure-id>.md` pack and its locked SHA-256;
- the user-confirmed reproduction time range;
- approved data sources and fallbacks;
- approved definition substitutions and their replacement fields;
- a complete, exactly aligned `data_integrity.json`;
- the target figure IDs.

## Preconditions

- The master specification is locked.
- The data-integrity gate is `complete` with no unresolved item.
- The definition-substitution gate is complete, with
  `definition_policy.decision_required: false` and an approved `SUB-*` for
  every non-explicit required definition.
- The target figure specification is complete.
- `source_evidence.status` is `frozen`.
- `spec_lock.json` records the same current SHA-256 for the target `spec.md`
  and frozen evidence pack.
- The Detail validation record is `passed` and matches both hashes.
- Approved data sources and fallbacks are known.
- The user has confirmed `publication_period` or `through_today`, with exact
  ISO start and end dates, timezone, and basis recorded in the manifest.

## Data Provenance

For every acquired dataset record:

- source URL or local path;
- query or request parameters;
- retrieval time;
- provider version and data vintage;
- schema and row count;
- SHA-256 hash;
- definition basis and linked `SUB-*` when a replacement definition is used;
- transformation code path.

Keep raw data immutable. Create interim and processed data from code.

## Execution

- Use only `spec.md`, the frozen evidence pack, approved data sources, and
  approved fallbacks to discover execution requirements. Do not reopen the
  paper or report for that purpose.
- Execute steps in the exact dependency order defined by `spec.md`.
- For every `Sxx` step record the step ID, command or function, parameters,
  input path or hash, output path or hash, validation result, failure action,
  and handoff. Do not skip, merge, or silently reorder a step.
- If any required field is missing or ambiguous, mark the figure `blocked` and
  return to `/reprospec:detail`. If the frozen evidence pack lacks the required
  fact, return to `/reprospec:outline`. Do not improvise or reread the report.
- Restrict acquisition, filters, joins, aggregations, and outputs to the
  confirmed reproduction time range. For `through_today`, use only data
  available on or before the confirmed end date.
- Compute every plotted value and coordinate from approved real data. Paper or
  report numbers are comparison targets only; never hard-code, copy, backfill,
  interpolate, or digitize them into source data, intermediate data, code
  constants, plot coordinates, annotations, labels, or output values.
- Execute only explicit definitions or approved replacement fields. Never
  reinterpret an original term that remains `underspecified` or `conflicting`.
- Record the `SUB-*`, replacement `D-*`, replacement definition, and known
  deviation in the run record when substituted data is used.
- Source-derived palette colors are rendering metadata, not quantitative
  values. They may be applied as style constants under the mandatory palette
  contract, but they must not enter data, coordinates, annotations, labels, or
  output values.
- Preserve the required chart type and data-to-mark encoding for every panel.
  Style changes must never convert a stacked bar chart into another chart type,
  a line chart into bars or points, a scatter plot into a line chart, or any
  other type into a different representation.
- Keep code under the figure `src/` directory.
- Write logs under `logs/`.
- Write the canonical execution record to `logs/run_record.json`.
- Write intermediate contracts under `data/`.
- Write rendered PNG files under `output/`. Generate PDF, SVG, EPS, JPEG, TIFF,
  or another format only when `spec.md` explicitly requires it.
- Do not enforce a fixed canvas size or output dimensions from `spec.md`.
  Choose or automatically adjust the canvas from the source aspect ratio,
  panel layout, text, and content. A general `figsize=(12, 5)` fallback may be
  used only as a non-binding recommendation.
- Apply the `matplotlib_notebook_default` title policy after all plotting
  imports, styles, and theme setup. Resolve the default title family, size, and
  weight from `matplotlib.rcParamsDefault`, using `figure.*` defaults for an
  overall title and `axes.*` defaults for panel titles. Resolve the concrete
  default font face selected by the default family and fallback chain, and pin
  the resolved properties on the title text.
- Never measure, infer, or override title font properties from the published
  figure. If a title does not fit, adjust layout, margins, canvas sizing, or
  safe line wrapping instead of changing its family or size.
- Center visible overall and per-panel titles after layout adjustments.
- Use English for titles, axis labels, tick labels, series names, legends,
  annotations, callouts, colorbars, and panel labels. Use another language only
  when `spec.md` records an explicit user request.
- Apply the mandatory palette contract recorded in the rendering contract.
  Prefer exact vector colors. For raster sources, use the recorded sampling
  regions, normalization, extracted colors, color-space conversion, mark
  mapping, and acceptance tolerance.
- If the palette contract is `not_applicable`, require the specification
  evidence that no color-dependent encoding exists. If the palette is `blocked`
  or cannot be applied to every required mark, mark the figure `blocked`; do
  not substitute arbitrary colors.
- Palette colors are rendering metadata. Sampled color constants may appear in
  plotting code, but they must never be used as numeric data, coordinates,
  annotations, labels, or output values.
- Typography other than the fixed title policy, line styles, marker styles,
  grids, spines, legends, annotations, layouts, and other fine visual details
  need not be imitated.
- Store environment metadata and command history.
- Record each processing step's command, parameters, input and output paths,
  and hashes so `/reprospec:audit` can reconstruct the lineage.
- Update the manifest to `reproduced` only after all required outputs exist.
- Run `scripts/validate_run_record.py` after execution. It must confirm that
  the specification and evidence hashes still match the lock, every `Sxx` step
  has a completed entry, all required step validations pass, and no report
  reread event exists. Record the run-record hash in the manifest.
- Do not mark a figure `reproduced` if run-record validation fails.

Each `runbook_steps` entry uses these fields:

```json
{
  "spec_step": "S01",
  "status": "completed",
  "command": "python src/build.py --step load",
  "parameters": "Exact parameters used",
  "inputs": ["data/raw/source.csv"],
  "outputs": ["data/interim/loaded.parquet"],
  "validation": "Exact validation performed",
  "failure_action": "Stop and mark blocked",
  "handoff": "Artifact consumed by the next step",
  "result": "passed"
}
```

Use `not_applicable` with a reason rather than leaving a required field empty.
- Re-check every source hash and definition before execution.
- Recompute the specification and evidence-pack hashes before execution. Any
  mismatch with `spec_lock.json` stops reproduction and requires
  `/reprospec:analyse` to revalidate and relock the specification.
- Re-check that the confirmed time range still matches the locked
  specification. If it does not, stop and return to `/reprospec:analyse`.
- Stop and return to analysis when a source changed or is no longer aligned.
- Stop and return to analysis when an approved replacement definition changed,
  is missing, or does not match the locked `SUB-*`.

## Output Contract

Each target figure retains immutable raw inputs, implementation code, logs,
environment metadata, intermediate data, a complete per-step run record, and
rendered output with provenance. The run record records the locked
specification path and hash, evidence-pack path and hash,
`report_reread_for_requirements: false`, and an empty `reread_events` list.
The rendered output must use the required chart type, data encoding, and
`matplotlib_notebook_default` centered title style. Canvas size is adaptive or
content-driven; no fixed size is read from the specification, and
`figsize=(12, 5)` is only a non-binding general fallback. The source-derived
palette contract is mandatory unless the figure is evidenced as
`not_applicable`. Source font matching and other fine visual imitation are not
required. Record the resolved overall and panel title family, point size, and
weight in the run record. Plot text must be English unless the specification
records an explicit language exception. PNG is the default and required
baseline output; additional formats must be documented in the specification.

No output may be produced from a source that failed the data-integrity gate.

## Failure Handling

When execution cannot proceed:

- mark only the affected figure `blocked`;
- write the exact blocker and evidence;
- do not substitute unapproved data;
- do not substitute a guessed definition for an `underspecified` or
  `conflicting` paper term;
- do not use a published expected value to complete missing data or satisfy an
  output check;
- do not silently substitute the paper period for `through_today` or extend
  `through_today` beyond the confirmed end date;
- do not change the locked specification.
- do not reread the report to fill a missing runbook step;
- return to `/reprospec:detail` when the specification is incomplete or its
  hash changed after validation;
- return to `/reprospec:outline` when the frozen evidence pack is incomplete;
- return to `/reprospec:analyse` when either locked hash changed and the
  specification must be revalidated and relocked.
