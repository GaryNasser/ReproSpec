# Execution Runbook Standard

## Purpose

Define the minimum depth required for a figure specification to be executable
without rereading the paper or report.

## Self-Contained Specification Test

A specification passes only when a new agent can build the figure from:

1. `spec.md`;
2. `evidence/<figure-id>.md`;
3. approved source data and documented fallbacks.

The agent must not need the report, a prior conversation, an unrecorded
decision, or the detail-stage agent's working memory.

If a fact is needed only to verify the final result, place it in the comparison
contract. If it is needed to compute, transform, select, label, encode, render,
or export anything, place it in the executable specification.

## Evidence Freeze Rules

- Every report-derived executable requirement cites one or more `E###` IDs.
- Quote or transcribe the exact source fact once into the evidence pack.
- Distinguish executable facts from `comparison_only` printed values.
- Record page, caption, table, figure, panel, appendix, or supplementary
  evidence for every fact.
- If evidence is missing, return to `/reprospec:outline`. Do not fill the gap
  from memory or by reopening the report during Detail or Reproduce.
- Record the evidence-pack SHA-256 in `spec.md`. A changed evidence pack
  invalidates the specification until Detail revises and revalidates it.

## Runbook Granularity

Use one step for one understandable operation. Split a step when any of these
changes:

- input artifact or schema;
- source filter or row grain;
- join or aggregation boundary;
- formula or unit;
- output artifact;
- validation method;
- failure action.

Typical figures need separate steps for:

1. acquiring or loading each required source;
2. validating and normalizing each source;
3. joining or aligning keys and time ranges;
4. deriving each analytical field or filter;
5. aggregating to the plotted grain;
6. constructing each panel or data-driven annotation;
7. rendering the complete figure;
8. exporting required formats;
9. running structural, numerical, and rendering checks.

Do not combine several sources, joins, formulas, panels, or outputs into one
step if their failures or validations differ.

## Required Step Contract

Every `Sxx` step must specify all of these fields:

- `Depends on`: exact prior step IDs or `none`.
- `Input`: exact path, source, or upstream artifact and expected schema.
- `Operation`: one precise action, including filter order, join type, grouping,
  sort, window, and aggregation method when applicable.
- `Formula or logic`: executable formula, pseudocode, or precise rule. If not
  applicable, write `not_applicable` and explain why.
- `Parameters`: exact values, or a rule that resolves to an exact value. Include
  timezone, units, date conventions, constants, and source provenance.
- `Code entrypoint`: planned code path and function or class, such as
  `src/build_panel_a.py::build_panel_a`, and the command to run it.
- `Output`: exact path, format, schema, row grain, and required fields.
- `Validation`: an objective check with expected count, range, equality,
  schema, hash, or rendered property.
- `Failure action`: whether to stop, return to a named stage, or mark the
  figure blocked. Do not write "investigate" without a decision rule.
- `Handoff`: the exact artifact or state consumed by the next step.

## Precision Requirements

### Data Operations

State:

- exact columns and dtypes;
- key columns and expected join cardinality;
- row grain before and after each operation;
- date parsing format, timezone, inclusive or exclusive boundaries;
- missing-value treatment and reason;
- outlier and revision treatment when material;
- unit conversion multiplier and target unit;
- sort order for ordered plots;
- grouping keys, aggregation function, and weighting formula;
- rounding stage and precision.

### Calculations

Write formulas in a directly implementable form. Name every input, output,
window, lag, weight, denominator, and fallback branch. Do not use phrases such
as "compute the relevant metric".

### Rendering

State exact visible text, panel mapping, series order, axis encoding, scale,
limits, tick formatter, legend order, annotation value rules, color mapping, and
output path. Record whether a value is data-driven or a fixed rendering fact.

### Validation

Every step needs a check that can fail. Examples:

- expected row count or accepted range;
- uniqueness of a key;
- null count or rate;
- sum or total reconciliation;
- exact schema and dtype check;
- output file existence and hash;
- expected panel count, series count, or title text;
- numerical comparison against comparison-only evidence.

## Prohibited Specification Language

Do not leave these as executable instructions:

- `clean the data`;
- `handle appropriately`;
- `normalize as needed`;
- `standard treatment`;
- `reasonable default`;
- `use a suitable source`;
- `adjust if necessary`;
- `similar to the report`;
- `TBD`, `TODO`, or unresolved placeholders.

Replace them with the exact rule, parameter, branch, threshold, or explicit
decision reference.

## Reviewer Test

For each step, ask:

1. Can another agent identify the exact input?
2. Can it perform the same operation with the same result?
3. Are all parameters and formulas known?
4. Is the output path and schema known?
5. Is there a check that will fail on the wrong result?
6. Is the next step's input unambiguous?
7. Does the step avoid any need to reread the report?

Any `no` means the specification is incomplete.
