# Detail Rules

## Purpose

Define the detailed, traceable specification contract for every included
data-driven figure.

## Inputs

- the locked or draft master outline;
- one frozen `evidence/<figure-id>.md` pack per target figure with a matching
  SHA-256;
- the included and excluded figure inventories;
- available source data and acquisition constraints.

Do not reopen the paper or report in this stage to discover requirements. The
evidence pack and master outline are the complete report-derived inputs.

## Figure Unit

Process only figures classified as `data_driven` by `/reprospec:outline`.
Schematic, conceptual, workflow, architecture, and qualitative illustration
figures are excluded and do not receive directories.

Treat each included main figure, appendix figure, panel group, or chart-like
table as a separate reproduction unit.

Use:

```text
figures/F001_short-title/
|-- spec.md
|-- data/
|-- src/
|-- output/
|-- logs/
|-- pixel_evidence/
|-- comparison_report.md
`-- limitations.md
```

Create `comparison_report.md` only when verification begins. Create
`limitations.md` only when a limitation exists.

## Required Specification

Record:

- figure identity, source page, and panels;
- claim or purpose;
- master version and dependency IDs;
- the source-evidence path and SHA-256;
- a specification evidence map from every executable contract area to the
  exact `E###` rows that support it;
- fields, keys, sample, period, frequency, units, currency, and linked
  `DATA-*` integrity IDs;
- for every non-explicit source definition, the approved `SUB-*`, replacement
  `D-*`, explicit replacement definition, functional rationale, and known
  deviation;
- joins, aggregation order, formulas, normalization, and smoothing;
- missing-value, outlier, and revision handling;
- axes, scales, limits, ticks, labels, series order, and required annotations;
- plot text language, requiring English by default and an explicit exception
  before using another language;
- panel layout and an adaptive canvas-sizing policy that does not prescribe a
  fixed figure size or output pixel dimensions;
- the fixed `matplotlib_notebook_default` title-style policy, sourced from
  `matplotlib.rcParamsDefault` and independent of source-image typography;
- a mandatory source-derived palette contract or an evidenced
  `not_applicable` result;
- numbered steps using `S01`, `S02`, and so on;
- for each step, `Depends on`, `Input`, `Operation`, `Formula or logic`,
  `Parameters`, `Code entrypoint`, `Output`, `Validation`, `Failure action`,
  and `Handoff`;
- provenance and acquisition requirements;
- acceptance tolerances;
- required output formats, defaulting to PNG only unless the user or a
  documented downstream requirement explicitly asks for another format;
- output paths;
- unresolved dependencies.

Every step must have input, action, output, and validation.

## Evidence Freeze Contract

`/reprospec:outline` freezes one evidence pack per included figure. Detail
must:

1. read that pack before writing or revising the figure specification;
2. cite an `E###` ID for every report-derived executable fact;
3. copy the exact rule or fact into the specification instead of relying on
   the reader to infer it from the report;
4. record the evidence path and SHA-256 in `spec.md`;
5. keep all exact published numbers in the comparison contract only;
6. stop and return to `/reprospec:outline` if any required fact is absent.

If the evidence pack changes, the old specification is invalid. Re-read the
new pack, update the specification, and rerun
`scripts/validate_spec.py`; the recorded evidence hash must match the new
freeze.

## Execution Runbook Contract

The specification is an implementation contract, not a summary of the report.
Read `references/execution-runbook-standard.md` and apply its self-contained
test, step granularity, required fields, precision requirements, prohibited
language, and reviewer test.

Use one step per understandable operation. Split a step whenever the input
artifact, schema, filter, row grain, join or aggregation boundary, formula,
unit, output artifact, validation method, or failure action changes. Typical
figures require separate steps for source intake, normalization, key
alignment, derivation, aggregation, panel construction, rendering, export, and
structural or numerical validation.

Every step must be executable without access to the report, an earlier
conversation, or the detail agent's memory. A later agent must be able to
identify the exact input, repeat the same operation, inspect the exact output,
and run a check that can fail.

## Definition Substitution Contract

Before adding processing steps, resolve every data dependency through one of:

- an `explicit` master definition; or
- an approved `SUB-*` whose replacement `D-*` has an explicit operational
  definition.

Never carry an `underspecified` or `conflicting` original `D-*` into a figure
specification. The data contract must reference the replacement `D-*` and
`SUB-*`, retain the original `D-*` for traceability, repeat the explicit
replacement definition, and record the known semantic or coverage deviation.
Processing steps operate on the replacement field, not on a guessed
interpretation of the original term.

If a required substitution is missing, unapproved, or incomplete, stop the
affected figure and return to `/reprospec:outline`. Do not create a
figure-local definition, infer a common meaning, or select a substitute because
it is more likely to reproduce a published value.

## Published Values Are Comparison-Only

Paper or report numbers are expected comparison targets, not source data or
implementation inputs. Never specify a processing step that copies,
hard-codes, backfills, interpolates, digitizes, or otherwise injects a
published value into source data, intermediate data, code constants, plot
coordinates, annotations, labels, or output values. Every reproduced value
must come from approved real data through a traceable transformation.

If a required value has no approved source, record the dependency as
`unavailable` or `blocked`; do not reconstruct it from prose, tables, or the
published image. Verified extracted values may appear only in the comparison
contract and verification evidence.

Source-derived palette colors are rendering metadata, not quantitative
published values. They may be recorded and applied as style constants under
the mandatory palette contract, but they must not enter data, coordinates,
annotations, labels, or output values.

## Chart Type Contract

Determine and record the chart type from the published figure before specifying
implementation details. Use the actual visual grammar, such as:

```text
stacked bar, grouped bar, simple bar, line, step line, scatter,
area, histogram, box plot, violin plot, heatmap, contour, pie,
donut, sankey, network, or another explicit type
```

For multi-panel figures, record the type separately for each panel. The
specification must also record the required data-to-mark mapping, such as
stacking, grouping, series order, mark position, and axis encoding.

Chart type is a hard requirement. Do not change:

- a stacked bar chart into a grouped bar, line, area, or pie chart;
- a line chart into bars, points, or an area chart;
- a scatter plot into a line chart;
- a heatmap into a table or bar chart; or
- any other chart type into a different representation.

Fine visual styling can vary when evidence is incomplete, but the chart type
and encoding must remain faithful to the source.

## Plot Text Language

Use English for every visible plot text element by default:

- title, subtitle, and panel labels;
- axis labels, tick labels, and category labels;
- series names, legend entries, and data labels;
- annotations, callouts, arrows, and colorbar labels.

Translate the source text into English while preserving symbols, units,
acronyms, proper names, and numeric values. Do not silently retain a non-English
label. Use another language only when the user explicitly requests it, and
record the exception and evidence in the rendering contract.

## Title Style and Alignment

Center every visible title and subtitle over the figure or panel it labels.
Apply this requirement to both overall and per-panel titles, and preserve
centering after layout adjustments.

Use `matplotlib_notebook_default` for every overall and per-panel title. Resolve
the default title family, size, and weight from `matplotlib.rcParamsDefault` in
a clean Matplotlib context after any notebook, style, or plotting-library
initialization. Use `figure.*` title defaults for an overall figure title and
`axes.*` title defaults for panel titles. Resolve the concrete default font face
selected by the default font-family and sans-serif fallback chain, not only the
generic `sans-serif` alias. Pin the resolved properties on the title text so a
global theme, `seaborn`, or a later `rcParams` change cannot alter only the
title style.

Do not measure, infer, or tune title family, size, or weight from the published
image. A title-font difference from the source is not a defect. If a title does
not fit, adjust layout, margins, canvas sizing, or safe line wrapping; never
shrink the title font or switch families to force a visual match.

## Canvas Sizing and Palette Contract

Do not write a fixed canvas size, output pixel dimensions, or a required
`figsize` into a figure specification. The rendering implementation may choose
or automatically adjust the canvas using the published aspect ratio, panel
layout, text, data content, and user constraints. A `figsize=(12, 5)` value may
be offered outside individual figure specifications as a non-binding general
starting recommendation, but it is not part of the specification and changing
it requires no exception or supporting evidence.

Palette matching is mandatory whenever color encodes data. Record exact vector
colors when available. For raster sources, sample representative regions and
record the regions, method, normalization, extracted colors, mapping to series
or marks, color-space conversion, and acceptance tolerance. Apply the mapped
colors consistently across panels and colorbars.

Raster-level color sampling is a mandatory requirement, not an optional step.
When the source figure is a raster image (including a scanned or rasterized
page of a report), the palette contract must be produced by sampling pixels
from the raster, not by transcribing qualitative color names (for example
"deep blue" or "gray") from the legend alone. For each color-dependent series
or mark, record all of: the sampling method (for example "median RGB of the
most-saturated pixels per hue family"), the source page or image region, the
exact sampled RGB and hexadecimal value, the color space, the mapping from
series/mark to sampled color, and the acceptance tolerance. A qualitative
legend transcription may be used only to identify which series a sampled color
belongs to, never as a substitute for the sampled color values. If raster
sampling cannot be performed (for example the raster is missing or illegible),
mark the palette contract `blocked` rather than recording invented or
qualitative-only colors.

Palette colors are rendering metadata. Their sampled values may be recorded as
style constants, but they must never be treated as or substituted for numeric
data, coordinates, annotations, labels, or output values.

Mark the palette `not_applicable` only when visual and specification evidence
shows that the figure has no color-dependent encoding. If representative colors
cannot be extracted or a required color mapping cannot be established, mark the
palette contract `blocked`; do not invent colors or claim palette agreement.
Palette mismatch or failure blocks a `matched` result.

Do not require or expect imitation of non-title typography, margins, line
widths, dash patterns, marker styles, transparency, grid, spines, legend,
annotations, backgrounds, or other fine visual details.

Record palette uncertainty separately. Source resolution, compression,
antialiasing, or overlap may widen the acceptance tolerance, but it does not
make palette matching optional. If uncertainty is too large to establish the
required mapping and tolerance, mark the palette and figure verification
`blocked`.

## Output Format

Produce PNG by default. Do not generate PDF, SVG, EPS, JPEG, TIFF, or other
formats unless:

- the user explicitly requests them;
- the publication or delivery requirement explicitly requires them; or
- another documented downstream requirement cannot use PNG.

Record every additional format and the reason in the rendering contract.

## Preflight

Check time, universe, frequency, units, fields, transformations, selection,
missing-data policy, granularity, and provenance against the master outline.

Check every executable statement against the frozen evidence pack. If the
master outline or evidence pack is insufficient, revise the shared record and
re-freeze it; do not add a figure-only override.

Run:

```text
python scripts/validate_spec.py --workspace <workspace> --paper-id <paper-id>
```

The validator checks the evidence path and hashes, required headings,
`E###` references, contiguous runbook steps, every required step field,
prohibited vague language, placeholders, the no-reread declarations, and the
No-Reread Checklist. It records the specification hash and successful
validation in the manifest.

## Status

Use exactly one status:

- `draft`
- `blocked`
- `partial`
- `reproduced`
- `stale`
- `verified`

## Output Contract

Each included figure receives one directory with `spec.md`, exact master
dependencies, numbered processing steps, a rendering contract with the
required chart type and encoding, `matplotlib_notebook_default` and centered
overall and panel titles, an adaptive canvas-sizing policy without fixed
dimensions, a mandatory palette contract or evidenced `not_applicable` result,
provenance requirements, and acceptance tolerances. The rendering contract
requires English plot text unless an explicit language exception is recorded.
The specification also contains the frozen evidence path and SHA-256, an
`E###` evidence map, a contiguous self-contained runbook, an artifact
contract, validation and stop conditions, and a fully checked No-Reread
Checklist.

## Failure Handling

If a rule cannot be determined from the frozen evidence pack or master outline,
do not reread the report and do not invent a figure-local rule. Return to
`/reprospec:outline`, resolve or add the missing evidence, re-freeze the pack,
and rerun Detail. If the missing rule is a data definition, require an approved
`SUB-*` in the master outline.
