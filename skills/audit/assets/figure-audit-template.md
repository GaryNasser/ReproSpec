# Figure Audit: {{FIGURE_ID}}

## Identity

- Figure: `{{FIGURE_TITLE}}`
- Figure status: `{{FIGURE_STATUS}}`
- Audit status: `{{AUDIT_STATUS}}`
- Master specification version: `{{MASTER_VERSION}}`
- Specification SHA-256:
- Frozen evidence pack:
- Evidence-pack SHA-256:
- Runbook coverage:
- Report reread for requirements:
- Final output: `{{OUTPUT_PATH}}`

## Lineage

`A -> B -> C -> ... -> {{OUTPUT_PATH}}`

State the data source and final image so the reader can see the complete path
before reading the steps.

For every approved definition substitution used by the figure, record
`SUB-*`, original `D-*`, replacement `D-*`, the explicit replacement
definition, the linked user decision, and the known deviation.

## A. {{STEP_A_TITLE}}

- Specification step: `{{SPEC_STEP}}`
- Master or data IDs: `{{MASTER_IDS}}`

### Input

State the exact source file, query, upstream output, or in-memory input.

### Operation

Describe the one operation performed and why it was required.

### Parameters and Code

Record exact parameters, filters, formulas, versions, and the code or command
path. Include the command when applicable.

### Output

State the exact output path, schema, shape, units, and hash when available.

### Evidence

Cite the artifact, log, run record, comparison evidence, or source location
that proves the operation occurred.

### Validation

State the check performed and its result.

### Handoff to Next Step

Explain exactly what the next step receives.

## B. {{STEP_B_TITLE}}

Repeat the required fields for input, operation, parameters and code, output,
evidence, validation, and handoff.

## C. {{STEP_C_TITLE}}

Continue adding sequential letters for every actual operation. Include the
rendering and export operations before the final output. The title-rendering
step must identify `matplotlib_notebook_default`, cite
`matplotlib.rcParamsDefault` as the source, and record the resolved family,
point size, and weight applied to overall and panel titles.

The palette-rendering step must identify the exact or sampled source colors,
the mark mapping, tolerance, and final `palette_outcome`. Record that palette
colors were used only as rendering metadata, not as data.

## Reader Test

Explain how a reader can reconstruct the figure from the listed source and
steps. Identify any unresolved question.

## Open Gaps

List missing evidence or uncertain lineage. If none, write `None`.
