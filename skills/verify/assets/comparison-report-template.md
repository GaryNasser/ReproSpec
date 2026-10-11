# Comparison Report: {{FIGURE_ID}}

## Identity

- Figure: `{{FIGURE_TITLE}}`
- Status:
- Master specification version:
- Result: `matched | partial | mismatched | blocked`
- Chart type and encoding result: `matched | mismatched | blocked`
- Title style result: `default | not default | blocked`
- Title alignment result: `centered | not centered | blocked`
- Plot text language result: `compliant | approved exception | noncompliant | blocked`
- Result rationale:
- Local computation provenance: `computed_from_approved_real_data | copied_published_value | blocked`
- Specification SHA-256:
- Evidence-pack SHA-256:
- Runbook coverage: `complete | incomplete | blocked`
- Report reread for requirements: `false | true | blocked`
- Palette result: `matched | mismatched | blocked | not_applicable`
- Palette evidence:
- Primary result attribution: `data | implementation | mixed | unknown | none`
- Palette failure attribution:

## Compared Artifacts

| Artifact | Path | Provenance |
| --- | --- | --- |
| Published figure |  |  |
| Printed values |  |  |
| Pixel-extracted data |  |  |
| Local data |  |  |
| Local output |  |  |
| Reference implementation output |  |  |

## Numerical Comparison

| Series or Point | Expected | Actual | Absolute Error | Relative Error | Within Tolerance |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Chart Type Comparison

| Panel | Published Type and Encoding | Local Type and Encoding | Match | Evidence |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Locked Runbook Coverage

| Specification Step | Run Record Entry | Command or Function | Input | Output | Validation | Result |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

The specification and evidence hashes must match `spec_lock.json`.
`report_reread_for_requirements` must be `false`, `reread_events` must be
empty, and every `Sxx` step must have one completed, validated entry.

## Plot Text Language

| Expected | Actual | Result | Evidence |
| --- | --- | --- | --- |
| English unless the specification records an explicit exception |  |  |  |

## Title Alignment

| Panel | Expected | Actual | Result | Evidence |
| --- | --- | --- | --- | --- |
| Overall | Centered |  |  |  |
|  | Centered |  |  |  |

## Default Title Style

| Scope | Expected Policy | Resolved Family, Size, and Weight | Source Font Matching | Result | Evidence |
| --- | --- | --- | --- | --- | --- |
| Overall | `matplotlib_notebook_default` from `figure.*` defaults |  | `false` |  |  |
| Panel | `matplotlib_notebook_default` from `axes.*` defaults |  | `false` |  |  |

## Palette Comparison (Required)

| Scope | Reference Color | Local Color | Color Difference | Tolerance | Result | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

## AI Repair Challenge

- Challenge ID:
- Status: `issued | answered | resolved | blocked`
- Attempt:
- Confirmed deviation:
- Quantified evidence:
- Evidence paths:
- AI-facing question:
- Acceptance check:
- Prohibited shortcuts: Do not use published values as inputs, constants, fills,
  coordinates, annotations, labels, or output values.

## Rework Handoff

| Required response field | Expected evidence or decision |
| --- | --- |
| Cause type | `data`, `outline`, `detail`, `implementation`, `style`, `pixel`, or `impossible` |
| Causal evidence |  |
| Rejected alternatives |  |
| Affected lineage or code |  |
| Minimum change |  |
| Falsification test |  |
| Expected effect |  |
| Acceptance check |  |

## Cross-Checks

| Check | Result | Evidence | Interpretation |
| --- | --- | --- | --- |
| Pixel data with local implementation |  |  |  |
| Local data with local implementation |  |  |  |
| Local data with reference implementation |  |  |  |

## Attribution

Explain the required result using data, chart type and encoding, implementation
evidence, or mandatory palette evidence. Reference master IDs and exact code,
data, or palette-sampling artifacts.

## Required Changes and Optional Improvements

| Type | Artifact | Current Rule | Proposed Rule | Affected Figures |
| --- | --- | --- | --- | --- |
| `<required data/chart type/encoding or palette>` |  |  |  |  |

## Remaining Uncertainty

Record measurement error, missing values, source revisions, and unresolved
implementation choices.
