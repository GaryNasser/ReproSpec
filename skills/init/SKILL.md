---
name: "init"
description: "Initialize a ReproSpec workspace by selecting one paper, asking for the reproduction time range before inspecting input data, establishing the computation-source policy, and enabling a definition-substitution policy that requires an approved, explicitly defined replacement whenever the paper leaves a required data definition unclear. Use only when explicitly starting or restarting a ReproSpec workflow. Do not use for later specification, execution, verification, or delivery stages."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.4.0"
---

## User Input

Use invocation arguments only as optional scope guidance. If no paper is
specified, identify candidates from the current directory.

## Pre-Execution Checks

- Run from the workspace root that contains the paper and source data.
- Do not create or reuse `work/<paper-id>/` until one paper is selected.
- Treat `.git`, `work/`, `figure-output/`, caches, credentials, and generated
  reproduction artifacts as non-candidates.

## Goal

Create one isolated reproduction workspace for exactly one paper or research
report. Do not infer the paper when multiple candidates are plausible.

Establish the computation-source policy at the start of the workflow: numbers
shown in the paper or report may be retained only as future comparison
artifacts. They must never be used as source data, plotting values, code
constants, missing-value fills, interpolations, digitized coordinates,
annotations, labels, or output values. Reproduction values must come from
approved real data and traceable computation. When the underlying data is
missing or unreliable, explain the gap and ask the user to choose whether to
supplement the data or skip the affected figure or claim.

Also enable the definition-substitution policy. When a required term, metric,
sample, period, unit, or transformation has no explicit operational definition
in the paper or report, no downstream stage may silently infer it. The gap must
be negotiated with the user and replaced by an approved substitute whose
definition is explicit and testable. The replacement must preserve the
analytical role, not be selected to match published values.

Immediately after paper selection and before inspecting or acquiring input
data or creating the reproduction workspace, ask the user to choose the
reproduction time range: reproduce the paper or report period, or extend
through today. Record the selected mode in the manifest before
`/reprospec:outline`. Exact start and end dates must be resolved by
`/reprospec:analyse` before the specification is locked.

## Execution Steps

1. Scan the current directory for candidate papers or reports.
2. Identify candidate papers and available access instructions. If multiple
   papers remain plausible, present the `Paper Selection` decision and stop.
   Do not inspect, inventory, copy, or acquire input datasets yet.
3. Immediately after exactly one paper is selected, present the
   `Reproduction Time Range` decision and wait. The answer determines which
   input data must be acquired and inspected, so do not examine or modify input
   datasets before the user answers.
4. Derive a short lowercase paper ID, such as `001-paper-title`.
5. Run `scripts/init_workspace.py` with the selected time range to create
   `work/<paper-id>/`.
6. Build the initial computation-source inventory. Identify any figure or claim
   that can currently be drawn only from numbers in the publication rather
   than from an approved underlying dataset. Record it as a data gap; never
   treat the publication value as a reproduction input.
7. Flag user-provided data that has no explicit origin, definition, or
   reliability description for integrity review. Do not infer those properties.
8. If an init-time data gap requires a decision, stop and present the
   `Missing Data Decision` protocol. Do not describe the affected item as
   reproducible. Set `data_plan.status` to `decision_required`, set
   `data_plan.decision_required` to true, and leave `workflow.next_stage` unset
   until the user chooses.
9. Summarize the available source inventory in the manifest and report any
   obvious missing paper or data files.
10. Confirm that the manifest points to exactly one source paper and records the
   computation-source policy, the definition-substitution policy, and the
   Init-confirmed time-range mode.

## Required Outputs

```text
work/<paper-id>/
|-- master_spec.md
|-- data_gaps.csv
|-- data_integrity.json
|-- data_integrity.md
|-- data_inventory.csv
|-- data_catalog.csv
|-- data_organization.json
|-- data_organization.md
|-- audit_report.md
|-- reproduction_manifest.json
|-- rework_log.md
|-- adjustment_log.md
|-- audits/
|-- evidence/
|-- figures/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- organized/
`-- logs/
```

## References

Read [references/init-rules.md](references/init-rules.md) before selecting a
paper or creating the workspace.

## Decision Protocol

When more than one paper is plausible:

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | Paper Selection**` label, a context block, an options
table, and a recommended option.

1. List candidates with path, title if available, file type, and hash.
2. Explain the impact of selecting each candidate.
3. Ask exactly one selection question and wait.

Do not create a workspace until the user selects a paper.

### Reproduction Time Range

Ask this immediately after selecting one paper and before inspecting input
data or running `scripts/init_workspace.py`.

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | Reproduction Time Range**` label, a context block, an
options table, and a recommended option.

1. Show the paper or report source and the current local date and timezone.
2. Explain that the choice affects the input period and every downstream
   acquisition, filter, aggregation, figure, and comparison.
3. Offer exactly these choices:
   - `publication_period`: use the paper or report's original period;
   - `through_today`: extend through today's latest available observations.
4. Recommend `publication_period` for a faithful baseline reproduction;
   recommend `through_today` only when the user explicitly wants a current
   extension and the required current inputs are available.
5. Ask exactly one question and wait.
6. Pass the selected mode and explicit timezone to
   `scripts/init_workspace.py`. Do not create the workspace without this
   answer.

The selected mode is recorded immediately. Exact start and end dates remain
pending until the paper period is extracted or `today` is resolved, and
`/reprospec:analyse` must confirm those dates before locking or reproduction.

### Missing Data Decision

Apply this protocol whenever a requested figure or result has no approved
underlying data and only a published number or digitized value is available.

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | Missing Data**` label, a context block, an options
table, and a recommended option.

1. Identify the affected figure, claim, and required data definition.
2. Explain why the publication value cannot be used as a reproduction input.
3. Offer exactly these two actions:
   - `supplement_data`: provide or obtain the approved real data and rerun the
     relevant stage.
   - `skip`: exclude the affected figure or claim and record the reason and
     limitation.
4. Recommend `supplement_data` when the figure is required for the stated
   reproduction goal.
5. Record the selected action in `data_plan.decision`, clear
   `data_plan.decision_required`, and set an appropriate post-decision
   `data_plan.status` only after the decision.
6. Ask exactly one decision question and wait.

Do not continue the affected reproduction while the decision is pending.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers. Generated
artifacts remain in English.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 1/12 | INIT**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | --- |
| Selected paper | `<paper-id>` |
| Source inventory | `<count>` files |
| Missing items | `<count>` |
| Computation policy | `enforced` |
| Time-range mode selected at Init | `<publication_period / through_today>` |
| Exact reproduction window | `pending Analyse confirmation` |
| Data gaps needing decision | `<count>` |

**Artifacts**

- `work/<paper-id>/reproduction_manifest.json`
- `work/<paper-id>/data_integrity.md`

> **Next**
>
> `/reprospec:outline`
>
> **Reason:** The paper is locked and the workspace is ready for full-document scanning.
```

If the user must select a paper, stop after the question and report the
selection blocker. If an init-time missing-data decision is pending, use
`Status: blocked`, report the affected data gap, and do not identify
`/reprospec:outline` as the next action. If the reproduction time range is
unanswered, do not create the workspace or identify `/reprospec:outline` as the
next action.

## Operating Constraints

- Create exactly one paper workspace per invocation.
- Never mix multiple papers.
- Never overwrite an existing workspace.
- Do not store credentials or secret values in artifacts.
- Never use a number from the paper or report as source data or a plotting
  input. Publication values are comparison-only.
- When real source data is missing or unreliable, stop the affected work and
  ask the user to supplement the data or skip the item. Do not reconstruct it
  from the publication.
- Do not let an undefined term, metric, sample, period, unit, or transformation
  pass as if it had an explicit definition. Require an approved `SUB-*`
  replacement with an explicit operational definition before reproduction.
- Never choose or tune a substitute to reproduce published numbers. A
  substitute is valid only when its definition is complete, approved by the
  user, and supported by an approved real-data source.
- Do not create the workspace before the user selects
  `publication_period` or `through_today`.
- Do not inspect, inventory, copy, or acquire input datasets before the
  time-range mode is answered, because that answer determines which inputs are
  relevant.
- Do not allow reproduction before `/reprospec:analyse` records the exact
  start date, end date, timezone, and basis with
  `time_range_policy.status: confirmed`.
- Generated files, paths, fields, and comments must be English.

## Done When

- [ ] Exactly one paper is selected.
- [ ] `work/<paper-id>/` and its manifest exist.
- [ ] The source inventory, unexplained data, and missing items are reported.
- [ ] The manifest records the computation-source policy as enforced.
- [ ] The manifest records the definition-substitution policy as enforced.
- [ ] The user selected `publication_period` or `through_today` immediately
      after paper selection and before input inspection or workspace creation,
      and the manifest records that choice.
- [ ] Exact time-range dates remain pending for `/reprospec:analyse` until
      confirmed.
- [ ] Every init-time data gap has a user decision to supplement or skip, or
      the workflow remains blocked.
- [ ] The data inventory, catalog, and organization record are initialized.
- [ ] The audit directory and report are initialized.
- [ ] The completion report identifies `/reprospec:outline` as the next stage.
