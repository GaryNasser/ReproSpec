# Verification Rules

## Purpose

Define evidence priority, pixel extraction, numerical comparison, attribution,
and limitation handling for reproduced figures.

## Inputs

- the reproduced figure and specification;
- the locked definition substitutions and replacement definitions;
- the published figure at the best obtainable resolution;
- printed values, vector evidence, or raster pixel evidence.

## Evidence Priority

For quantitative comparison, use:

1. Exact values printed in text, tables, or appendices.
2. Vector coordinates extracted from the PDF.
3. Raster pixel extraction with uncertainty.

Source-derived palette evidence is a separate mandatory acceptance input
whenever color encodes data, not a lower-priority similarity signal.

Printed values and values digitized from the published figure are expected
comparison artifacts only. They may be stored in `pixel_evidence/` or the
comparison report, but they must never be copied into the local data pipeline,
implementation code, intermediate data, plot coordinates, annotations, labels,
or output values.

Compare values only within the user-confirmed reproduction time range. When the
selection is `through_today`, report the publication-period baseline and the
extended period separately; do not describe extended values as matching the
original paper or report.

## Pixel Extraction

1. Extract the published figure at the highest available resolution.
2. Identify panel boundaries and axes.
3. Determine axis transformations.
4. Anchor tick labels and grid lines.
5. Calibrate pixel-to-data mappings.
6. Separate series by color, marker, line style, legend, or manual masks.
7. Digitize visible points and flag occluded values.
8. Estimate uncertainty.
9. Save extracted values, calibration metadata, masks, and overlays.

## Comparison

Compare:

- point-level absolute and relative error;
- series-level RMSE, MAE, correlation, or rank agreement;
- aggregate differences;
- visual overlay as supporting evidence.

Define tolerances before comparison.

The local result must be computed independently from approved real data. A
comparison is invalid if agreement was achieved by hard-coding, copying,
backfilling, interpolating, digitizing, or otherwise injecting the published
value into the local output. In that case, do not classify the figure as
`matched`; record the violation and use `mismatched`, `partial`, or `blocked`
as appropriate.

Before evaluating numerical agreement, verify the execution record against the
locked runbook:

- the run record's specification and evidence SHA-256 values match
  `spec_lock.json`;
- `report_reread_for_requirements` is `false`;
- `reread_events` is empty;
- every `Sxx` step has one completed entry with the command or function,
  parameters, input, output, validation result, failure action, and handoff;
- every required step validation passes;
- no step was skipped, merged, or silently reordered.

A changed hash, report reread event, missing step, or failed required step
blocks provenance. Do not infer a pass from a correct-looking rendered image.

Source-derived palette colors are rendering metadata, not quantitative values.
Their use in style code is governed by the mandatory palette contract and does
not authorize copying source values into data, coordinates, annotations,
labels, or outputs.

For substituted data, verify that the pipeline used the approved replacement
`D-*` and `SUB-*` exactly. A difference attributable to the substitute's
documented semantic or coverage deviation is not an implementation defect and
must not trigger tuning toward the published value. Record it as a limitation
or approved substitution effect.

## AI Repair Challenge

For every confirmed, actionable mismatch, issue one evidence-backed AI challenge
to `/reprospec:rework`. The challenge is not a question for the user. It is a
structured request that forces rework to explain the cause and make the minimum
evidence-supported correction.

Create the challenge from `assets/rework-challenge-template.json` at
`figures/<figure-id>/rework_challenge.json`. A challenge is valid only when:

- the mismatch is confirmed by numerical, structural, or rendering evidence;
- the evidence identifies the affected figure, panel, series, or contract;
- the observed values, errors, tolerances, and evidence paths are recorded;
- one main AI-facing question asks for the minimum causal correction;
- an objective acceptance check can be rerun after reproduction;
- the response schema requires cause type, causal evidence, rejected
  alternatives, affected lineage or code, minimum change, a falsification test,
  expected effect, and acceptance check; and
- the correction is prohibited from using published values as inputs,
  constants, fills, coordinates, annotations, or output values.

Do not issue a challenge for a subjective visual impression, an unquantified
guess, or a mismatch whose expected evidence cannot be established. Use
`partial` or `blocked` and `limitations.md` instead.

Challenge statuses are:

- `issued`: verification has produced an unanswered challenge.
- `answered`: rework has supplied a complete evidence-backed response and may
  edit the affected artifacts.
- `resolved`: re-verification passed the challenge's recorded acceptance check.
- `blocked`: three rework attempts failed, or the required evidence cannot
  support an honest automatic repair.

When a challenge exists for a deviation, reuse it instead of creating a
duplicate. On failed re-verification, return it to `issued`, increment the
attempt, add the new comparison evidence, and retain the previous responses.
After three failed attempts, mark it `blocked`. Do not invoke
`/reprospec:adjust`; report that manual human review is available after the
automatic loop stops.

The challenge cannot authorize overfitting. Rework must identify a real cause
and change real inputs, formulas, joins, transformations, or implementation
logic. It may not tune parameters or alter validation rules merely to make the
published values match.

## Chart Type Verification

Compare the published and local chart type for the overall figure and each
panel. Verify the data-to-mark mapping, including:

- stacked, grouped, or overlapping bars;
- lines, steps, areas, points, or bars;
- scatter, bubble, or line relationships;
- histograms, box plots, violin plots, heatmaps, contours, pies, or donuts;
- axes and other encodings that define the chart type.

A chart type or encoding mismatch cannot be `matched`. Examples include:

- stacked bars changed to grouped bars or a line chart;
- line series changed to points or bars;
- scatter points changed to connected lines;
- a heatmap changed to bars or a table.

## Plot Text Language Verification

Confirm that the rendered figure uses English for:

- titles, subtitles, and panel labels;
- axis labels, ticks, and category labels;
- series names, legends, and data labels;
- annotations, callouts, arrows, and colorbar labels.

English is the required default. A non-English element is compliant only when
the locked figure specification records an explicit user-requested language
exception for that element or figure. Preserve a copy of the evidence used to
verify the visible text when OCR or direct source text is available.

## Title Style and Alignment Verification

Verify `matplotlib_notebook_default` from the run record, rendering code, and
title objects. Overall titles must resolve family, size, and weight from
`matplotlib.rcParamsDefault` under the `figure.*` defaults; panel titles must
resolve the corresponding `axes.*` defaults. The properties must remain pinned
after any style or theme setup. A missing policy, a source-derived override, or
a title style changed by a global theme is a required defect.

Confirm that every visible overall title and panel title is centered over the
figure or panel it labels. Title alignment is a required rendering behavior;
a left- or right-aligned title is a defect.

Do not compare or gate on whether the title font resembles the published
figure. A title-font difference from the source is expected and must not
downgrade the result when the fixed default policy is satisfied.

## Palette Verification

Verify the mandatory source-derived palette contract whenever color encodes
data. Use exact vector color values when available. For raster sources, compare
the recorded representative regions, sampling method, normalization,
color-space conversion, extracted colors, and mark mapping, accounting for
antialiasing and compression.

Compare every mapped palette entry with the reference color. Record per-entry
differences using the specification's color difference metric and tolerance,
plus the maximum and mean differences when available. The `palette_outcome` is:

- `matched` when every required mapping is within tolerance;
- `mismatched` when any required mapping is outside tolerance;
- `blocked` when the palette or mapping cannot be verified; or
- `not_applicable` only when evidence shows no color-dependent encoding.

A `mismatched` or `blocked` palette prevents a `matched` result. A
`not_applicable` result must cite the visual or specification evidence.

Palette colors are rendering metadata. Extracted colors may be recorded as
style evidence, but they must not be treated as numeric data, coordinates,
annotations, labels, or output values.

Do not compare, require, or gate on figure size, aspect ratio, margins, source
fonts, typography other than the fixed title policy, line widths, markers,
grids, spines, legends, annotations, backgrounds, or other fine visual
details.

## Attribution

Use cross-checks:

| Observation | Likely cause |
| --- | --- |
| Extracted published data with local code matches the paper, local data does not | Data difference |
| Local data with reference code matches the paper, local code does not | Implementation difference |
| Required chart type or data encoding differs after data and code agree | Detail or implementation difference |
| Plot text is non-English without a recorded exception | Detail or implementation difference |
| Title does not use `matplotlib_notebook_default` or is source-matched | Detail or implementation difference |
| A visible overall or panel title is not centered | Detail or implementation difference |
| Agreement depends on a copied or hard-coded published value | Implementation violation; comparison invalid |
| Report was reread to discover a requirement | Provenance violation; return to Detail or Outline and revalidate |
| A locked runbook step is missing or unrecorded | Provenance violation; cannot be `matched` |
| Data and encoding match, but the required palette differs | Implementation or style difference; cannot be `matched` |
| Output follows an approved substitution but differs from the published term | Expected definition-substitution deviation; do not tune |
| Neither comparison matches | Mixed or unresolved |
| Both match within tolerance | Reproduction supported |

Palette outcome is a required result separate from the data outcome.

## Limitations

Create `limitations.md` when full reproduction or verification is impossible.
Do not mark the figure `verified`.

## Output Contract

Produce `comparison_report.md`, preserve pixel and palette evidence when used,
and update the figure result with a primary attribution, numerical outcome,
required chart-type and encoding outcome, default title-style outcome,
title-alignment outcome, plot-text language outcome, mandatory palette
outcome, runbook-coverage outcome, report-reread outcome, and
`verification.computation_provenance`. Set
`verification.title_style_outcome` to `default`, `not_default`, or `blocked`
and `verification.source_derived_title_font_matching` to `true` or `false`. Set
`verification.palette_outcome` to `matched`, `mismatched`, `blocked`, or
`not_applicable`, and record the comparison or `not_applicable` evidence in
`verification.palette_evidence`.

Set `verification.computation_provenance` to
`computed_from_approved_real_data` only when the reproduced values and
coordinates trace to approved real data and traceable computation. Use
`copied_published_value` for a detected violation and `blocked` when provenance
cannot be established. A figure with `copied_published_value` or `blocked`
provenance cannot be classified as `matched`.

For every confirmed actionable mismatch, write `rework_challenge.json` and set
`verification.rework_challenge` in the figure record to an object containing
the challenge `challenge_id`, `status`, `attempt`, `evidence_paths`, and
`acceptance_check`. The challenge must be `issued` when the workflow hands the
figure to `/reprospec:rework`. A challenge may be `resolved` only after the
recorded acceptance check passes. A challenge may be `blocked` only after three
failed attempts or unavailable required evidence. Do not create a user-facing
repair decision in this stage.

## Failure Handling

When evidence is insufficient, report the uncertainty, create `limitations.md`,
and use `partial` or `blocked` rather than claiming full verification. Treat
copied or hard-coded published values as a blocking computation-integrity
defect, not as acceptable agreement. Record the exact affected value, artifact,
and code or data location.

Do not issue an AI repair challenge when the expected evidence is unavailable
or the mismatch cannot be made actionable. Instead record the exact missing
evidence and keep the figure `partial` or `blocked`. A challenge that reaches
`blocked` must stop automatic retries and leave manual `/reprospec:adjust`
review as a separate human action.
