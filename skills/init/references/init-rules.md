# Init Rules

## Purpose

Define how the Init stage selects one paper and creates one isolated workspace.

## Inputs

- the current directory and its source files;
- user-provided scope guidance;
- any existing candidate selection.

## Input Selection

- Scan the current directory before creating any workspace.
- Ignore generated directories and version-control internals.
- Treat PDF, DOCX, Markdown, notebook, and report exports as paper candidates.
- Do not choose a paper when multiple candidates are plausible.
- When multiple candidates exist, show the user a numbered list and include the
  path and SHA-256 hash when the file is available locally.

## Workspace

Create exactly one directory:

```text
work/<paper-id>/
```

The ID must contain lowercase ASCII letters, digits, dots, underscores, or
hyphens. Prefer a short action-oriented value such as `001-paper-title`.

## Source Inventory

Record:

- selected paper path or URL;
- paper hash when available;
- source datasets supplied by the user;
- notebooks, scripts, and notes;
- approved data sources and APIs;
- missing inputs that are immediately apparent.

Never record credentials.

## Computation Source Policy

Establish this policy when the workspace is created:

- Numbers in the selected paper or report are comparison and verification
  targets only.
- Reproduction data, generated values, and plot coordinates must come from
  approved real data through traceable computation.
- Never copy, hard-code, backfill, interpolate, or digitize a publication value
  into source data, implementation code, annotations, labels, or outputs.
- A publication number is not an acceptable fallback for missing data.

Record the policy in `reproduction_manifest.json` under
`computation_policy`, with `status: enforced`.

## Definition Substitution Policy

Initialize `definition_policy` in `reproduction_manifest.json` with:

- `status: enforced`;
- `undefined_data_action: negotiate_explicit_substitute`;
- `decision_required: false`;
- an empty `substitutions` list.

This policy applies from `/reprospec:outline` onward. When a required term,
metric, sample, period, unit, or transformation has no explicit operational
definition, the affected item must not be inferred silently. Record the gap,
ask the user, and replace it with an approved `SUB-*` contract whose replacement
definition is explicit, source-backed, and traceable.

A substitute must preserve the analytical role of the original item and state
its known deviation. It must never be selected or tuned merely because it makes
the reproduced values resemble values printed in the paper or report.

Initialize `source_evidence` with `status: pending`, an `evidence` directory,
an empty `items` list, and a null `updated_at`. `/reprospec:outline` must freeze
one complete evidence pack per data-driven figure before `/reprospec:detail`
creates its executable specification.

## Reproduction Time Range

Ask for the time-range mode immediately after paper selection and before
inspecting, inventorying, copying, or acquiring input data or running
`init_workspace.py`, because the answer changes which input data must be
acquired, inspected, and aligned. Do not choose a time range silently and do
not create the workspace before the user answers.

The user must choose exactly one mode:

- `publication_period`: reproduce the paper or report's original period;
- `through_today`: extend the period through the confirmed current date.

The initial manifest record must include:

- `status: selection_confirmed`;
- `selection`;
- `user_confirmed: true`;
- `confirmed_at`;
- `decision_required: false`;
- an explicit `timezone`;
- the selection basis.

Exact `start_date` and `end_date` may remain null in Init. `/reprospec:analyse`
must resolve both ISO dates, define the final basis, change `status` to
`confirmed`, and re-confirm the final window with the user before locking or
reproduction.

For `through_today`, the final `end_date` means the latest available observation
as of the confirmed date, not an unverified assumption that every source has
data for the calendar date. Record any source-specific latest date. Reopen the
analysis gate if the user later wants a different end date.

## Missing Data Decisions

During Init, identify whether every candidate figure or claim has an approved
underlying data source. A publication value alone does not establish a
reproducible data source.

When an affected item is found:

1. Add it to `data_gaps.csv` with the required definition and missing source.
2. Present `**Decision Required | Missing Data**` with exactly two actions:
   `supplement_data` and `skip`.
3. Recommend `supplement_data` when the item is required for the agreed
   reproduction scope.
4. Set `data_plan.status` to `decision_required`, set
   `data_plan.decision_required` to true, and clear `workflow.next_stage` while
   the decision is pending.
5. Wait for the user's decision before advancing the affected item.
6. Record the selected action in `data_plan.decision`, clear
   `data_plan.decision_required`, set an appropriate post-decision
   `data_plan.status`, and restore the appropriate next stage.

If the user skips the item, record the affected figure or claim and reason in
`excluded_figures` or the relevant limitation record. Do not silently replace
missing data with the published value. If the user supplies data, it must still
pass the normal data-integrity review.

## Unspecified Data

When a user-provided dataset has no explicit origin, definition, or reliability
description, record that it requires integrity review during `/reprospec:plan`.
Do not infer its provenance, reliability, or definition from filenames alone.

## Manifest

Use `reproduction_manifest.json` as the shared state between all ReproSpec
skills. Initialize the workflow stage, next stage, master specification,
figures, computation policy, data plan, rework, adjustments, organization,
audit, and delivery sections.

## Output Contract

Produce exactly one `work/<paper-id>/` workspace with the required directories,
`master_spec.md`, `data_gaps.csv`, `data_integrity.json`,
`data_integrity.md`, `data_inventory.csv`, `data_catalog.csv`,
`data_organization.json`, `data_organization.md`, `audit_report.md`,
`reproduction_manifest.json`, `rework_log.md`, and `adjustment_log.md`.

## Failure Handling

When multiple papers are plausible, stop before creating the workspace, report
the candidates, and ask one selection question.

When the reproduction time-range mode has not been answered, stop before
creating the workspace. Do not default to the paper period or to today.

When the required source data is absent, unreliable, or represented only by a
publication value, stop the affected item and request a `supplement_data` or
`skip` decision. Never continue by copying the publication value.

When a required definition is absent or ambiguous, stop the affected item and
require an approved substitution or an explicit skip. Do not continue with a
silently inferred definition.
