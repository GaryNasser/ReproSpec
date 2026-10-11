# Figure Specification: {{FIGURE_ID}}

## Identity

- Title: `{{FIGURE_TITLE}}`
- Paper ID: `{{PAPER_ID}}`
- Figure path: `{{FIGURE_ID}}_{{FIGURE_SLUG}}`
- Source page:
- Panel structure:
- Status: `draft`
- Master specification version:
- Master dependency IDs:
- Required reproduction window: `pending until Analyse confirmation`
- Source evidence pack: `{{SOURCE_EVIDENCE_PACK}}`
- Source SHA-256: `{{SOURCE_SHA256}}`
- Evidence pack SHA-256: `{{EVIDENCE_PACK_SHA256}}`
- Self-contained execution: `yes`
- Report reread for requirements: `prohibited`

## Published Claim

State the quantitative claim, comparison, or relationship shown by the figure.
Cite the `E###` evidence IDs that support the claim.

## Source Evidence Freeze

Use only the frozen evidence pack and the source-data contract to define this
figure. Do not infer a missing requirement from memory, common convention, or a
quick reread of the report. If any needed fact is absent, stop and return to
`/reprospec:outline`.

### Specification Evidence Map

| Specification Area | Evidence IDs | Exact Rule or Fact | Source Locator |
| --- | --- | --- | --- |
|  |  |  |  |

### Rejected or Resolved Ambiguities

| Issue | Decision or Limitation | Source Evidence | Status |
| --- | --- | --- | --- |
|  |  |  |  |

## Data Contract

| Field | Definition | Original Master ID | Master ID | Substitution ID | Replacement Definition | Known Deviation | Integrity ID | Unit | Frequency | Required Sample |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |

For every `SUB-*`, reference the replacement `D-*`, repeat its explicit
operational definition, retain the original `D-*`, and state the known
deviation. An `underspecified` or `conflicting` original definition must not
appear as an executable field.

### Input Artifact Contract

| Input ID | Required Path or Source | Format | Row Grain | Required Fields and dtypes | Units | Time Filter | Validation Before Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IN01 |  |  |  |  |  |  |  |

### Global Transformation Contract

- Time range and timezone:
- Entity universe and exclusions:
- Join keys and cardinality:
- Sort order:
- Missing-value rule:
- Outlier rule:
- Revision and vintage rule:
- Currency or unit conversion:
- Rounding rule:
- Published values policy: comparison only; never an executable input.

## Panel and Chart Contract

| Panel | Chart Type | X Encoding | Y Encoding | Series or Categories | Series Order | Legend and Labels | Required Annotations |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

### Forbidden Chart Changes

- State every chart-type or encoding change that is prohibited for this figure.

## Execution Runbook

Each step is an independent executable operation. Replace every placeholder
with explicit paths, schemas, formulas, parameters, and validation rules. A
later agent must be able to execute the steps in order without reading the
report.

### S01 {{STEP_1_NAME}}

- Depends on: `none`
- Input:
- Operation:
- Formula or logic:
- Parameters:
- Code entrypoint:
- Output:
- Validation:
- Failure action:
- Handoff:

### S02 {{STEP_2_NAME}}

- Depends on: `S01`
- Input:
- Operation:
- Formula or logic:
- Parameters:
- Code entrypoint:
- Output:
- Validation:
- Failure action:
- Handoff:

### S03 {{STEP_3_NAME}}

- Depends on: `S02`
- Input:
- Operation:
- Formula or logic:
- Parameters:
- Code entrypoint:
- Output:
- Validation:
- Failure action:
- Handoff:

Add `S04`, `S05`, and so on until every acquisition, normalization, join,
calculation, aggregation, rendering, export, and required validation operation
is explicit. Do not combine unrelated operations into one step.

## Rendering Contract

- Title style policy: `matplotlib_notebook_default`
- Title style source: `matplotlib.rcParamsDefault`
- Source-derived title font matching: prohibited
- Overall title text and alignment: centered
- Panel title text and alignment: centered
- Canvas sizing: automatic or content-driven; no fixed size is specified
- Published aspect ratio (reference only):
- Plot text language: English
- Language exception and evidence:
- Panel and plot-area layout:
- X axis labels, scales, limits, ticks, and formatter:
- Y axis labels, scales, limits, ticks, and formatter:
- Series order and style mapping:
- Legend position, entries, and order:
- Annotations, callouts, and data labels:
- Palette contract: `required / not_applicable / blocked`
- Palette evidence source:
- Palette extraction and mapping:
- Palette acceptance tolerance:
- Required formats: `png`
- Additional formats and reason:
- Known palette uncertainty and effect on verification:

## Artifact Contract

| Artifact ID | Producer Step | Exact Path | Format | Schema or Shape | Required | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| A01 | S01 |  |  |  | `yes` |  |

## Validation and Stop Conditions

| Check ID | Producer Step | Objective Check | Expected Result | Stop or Return Condition |
| --- | --- | --- | --- | --- |
| V01 | S01 |  |  |  |

## Comparison Contract

- Exact printed values available (comparison only; never an input):
- Evidence ID for each comparison value:
- Pixel extraction required:
- Primary metrics:
- Absolute tolerance:
- Relative tolerance:
- Shape or rank checks:
- Required comparison outputs:
- Prohibited shortcuts: Do not hard-code, backfill, interpolate, digitize, or
  copy published values into data, code, axes, annotations, labels, or output.

## Reproduction Results

- Output:
- Comparison status:
- Attribution:
- Remaining differences:
- Master-specification revisions required:

## No-Reread Checklist

- [ ] Every report-derived requirement in this specification cites an `E###`
      evidence ID.
- [ ] Every input, output, formula, parameter, and validation rule is explicit.
- [ ] No runbook step depends on an unstated report fact or conversational
      memory.
- [ ] No unresolved, placeholder, or discretionary instruction remains.
- [ ] Reproduction can proceed from this specification, the frozen evidence
      pack, and approved source data without rereading the report.
