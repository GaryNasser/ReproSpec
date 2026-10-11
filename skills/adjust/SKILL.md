---
name: "adjust"
description: "Turn a user-reported mismatch into an agreed, evidence-based correction, requiring an approved explicit definition substitute when the paper left a required definition unclear, and rechecking every affected figure. Use after /reprospec:rework and before organization, audit, or delivery. Do not use for unattended repair, speculative changes, or cosmetic tuning that the user has not approved."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.8.0"
---

## User Input

Use invocation arguments to select the figure or figures under manual review and
to provide the observed difference. If the observation is incomplete, ask for
the exact figure, panel, source location, expected result, and actual result
before changing files. If the user confirms that manual review found no
differences, record a completed no-change review instead of requiring a
finding.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `confirmed`, `selection` is `publication_period` or `through_today`,
  `user_confirmed` is true, and exact ISO start and end dates, timezone, and
  basis are recorded.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false.
- If the Init policy is missing or relaxed, stop and return to
  `/reprospec:init`. If `time_range_policy.status` is not `confirmed` or the
  exact window is invalid, stop and return to `/reprospec:analyse`. Never
  continue by using a publication value or by bypassing the `supplement_data`
  or `skip` decision.
- Automated verification reports and the rework assessment exist for the target
  figures.
- The published paper or report and local reproduction artifacts are available.
- The manifest contains all included figures and their known dependencies.
- The user has supplied a concrete finding or confirmed that manual review found
  no differences.

## Goal

Convert manual-review findings into agreed, traceable corrections. Apply only
the approved correction, verify the corrected figure, inspect every other
included figure for impact, and re-render and re-verify every figure that may
have changed. Distinguish confirmed impact from no impact rather than assuming
shared data or code is harmless. A clean manual review with no change is a
valid completion state. Published values remain comparison targets only; every
correction must preserve computation from approved real data.

## Execution Steps

1. Record the finding as `ADJ-NNN` with the target figure, panel or paper
   section, expected result, actual result, and the user's evidence.
   If manual review found no difference, record that result as a completed
   no-change adjustment and skip to step 11 without editing artifacts.
2. Reconcile the finding with the existing comparison report, specification,
   source evidence, data, code, logs, and rendered output.
3. Diagnose the root cause using `data`, `outline`, `detail`, `implementation`,
   `style`, `pixel`, or `impossible`. Separate the observed difference from any
   proposed explanation.
4. Present the diagnosis, evidence, affected scope, and concrete correction
   options. Recommend the smallest evidence-based correction and ask exactly
   one question. Do not edit any file until the user approves a correction.
5. Define the acceptance check for the corrected figure and the impact checks
   for the remaining figures before editing.
6. Apply the approved correction with provenance. If data must be completed,
   use an approved source or fallback; never invent, silently substitute, or
   fabricate missing values, and never copy or digitize a published value as a
   substitute. Record acquisition parameters and hashes.
7. If a master-level definition or report-derived rule changes, update the
   master specification, increment its version, update and re-freeze the
   affected evidence packs, revise affected figure runbooks, rerun
   `validate_spec.py`, rerun `lock_spec.py`, and mark all dependent figures
   `stale`.
8. Re-render and verify the corrected figure against the agreed acceptance
   check.
9. Build an impact matrix covering every included figure. Classify each as
   `affected`, `unaffected`, or `unknown` using master dependencies, data
   lineage, shared transformations, code imports or helpers, rendering
   utilities, and cross-figure references. Read
   [references/adjustment-rules.md](references/adjustment-rules.md) before
   completing the matrix.
10. Mark every `affected` and `unknown` figure `stale`, re-render it, and
    re-verify it or record the exact blocker. Do not omit a figure merely
    because its specification does not name the changed object directly.
11. Record the finding, decision, approved correction, changed artifacts,
    computation source, impact matrix, rerun results, verification outcomes,
    and residual risk in `adjustment_log.md` and
    `reproduction_manifest.json`. Use
    [assets/adjustment-record-template.md](assets/adjustment-record-template.md)
    for each record.
12. When no required correction remains and all impacted figures pass
    validation, pause at an explicit continuation decision. Ask whether to
    move to `/reprospec:organize` or continue with `/reprospec:adjust`. Do not
    select either path on the user's behalf or set `workflow.next_stage` until
    the user answers.

## References

Read [references/adjustment-rules.md](references/adjustment-rules.md) for the
interaction contract, correction rules, impact analysis, and artifact schema.

## Decision Protocol

The adjustment cannot proceed without an agreed correction.

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | <topic>**` label, a context block, an options table,
and a recommended option.

1. State the exact observed difference and source location.
2. Show the evidence that supports or contradicts the finding.
3. Explain which figures or data definitions may be affected.
4. Present the correction options with evidence, cost, and impact.
5. Recommend one option and ask exactly one question. Wait for the user before
   editing data, specifications, or implementation.

If the required source or decision is unavailable, keep the adjustment
`blocked`; do not fill the gap with a guessed value.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 9/12 | ADJUST**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Findings reviewed | `<count>` |
| Corrections approved | `<count>` |
| Corrections applied | `<count>` |
| Changed artifacts | `<count>` |
| Revalidated specifications | `<count>` |
| Relocked figures | `<count>` |
| Figures affected | `<count>` |
| Figures unaffected | `<count>` |
| Impact unknown | `<count>` |
| Figures re-verified | `<count>` |
| Residual blockers | `<count>` |

**Artifacts**

- `work/<paper-id>/adjustment_log.md`
- `work/<paper-id>/reproduction_manifest.json`
- `work/<paper-id>/figures/<figure-id>/output/`

> **Choose Next Action**
>
> - Move to the next stage: `/reprospec:organize`
> - Continue adjusting: `/reprospec:adjust <new finding or scope>`
>
> **Reason:** This adjustment round is complete; the next action requires the user's choice.
```

Always ask this continuation question after a completed adjustment round. The
two commands are the only valid choices: `/reprospec:organize` moves forward
without another adjustment, while `/reprospec:adjust` starts another adjustment
request and requires a new finding or scope if one was not supplied. Wait for
the answer before changing `workflow.next_stage`.

For `partial` or `blocked`, keep the same card, report the specific unresolved
user decision, missing source, or failed figure validation, and do not present
`/reprospec:organize` as an available path until the blocking work is resolved
or the user explicitly accepts the documented limitation.

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Corrections must preserve the exact
  user-confirmed reproduction time range.
- Do not change data, specifications, or implementation before the user
  approves a correction.
- Never fabricate missing data or silently substitute an unapproved source.
- Do not reopen the report to fill a missing runbook fact. Return the fact to
  `/reprospec:outline`, update and re-freeze the evidence pack, then revise and
  validate the affected specification.
- If a finding reveals a missing or ambiguous definition, do not infer it or
  tune toward the published value. Negotiate an approved `SUB-*` with an
  explicit replacement definition, increment the master version, and mark all
  dependent figures stale.
- Never copy, hard-code, backfill, interpolate, digitize, or inject a published
  expected value into data, code, axes, annotations, labels, or outputs.
- Keep the correction minimal and directly traceable to the finding.
- Preserve required chart types, data encodings, source-derived palettes,
  `matplotlib_notebook_default` title styling, centered titles, and English
  plot text unless the approved finding explicitly changes the specification.
- Assess every included figure after a correction. A shared object may be
  unaffected, but that conclusion must be recorded with supporting evidence.
- Treat `unknown` impact as requiring a rerun or an explicit user-accepted
  limitation; never treat it as `unaffected`.
- After every completed adjustment round, pause and ask whether to move to
  `/reprospec:organize` or continue with `/reprospec:adjust`. Provide those two
  commands and wait for the user's choice.
- If a shared definition changes, never update only one figure's specification.
- A new or changed definition substitute must update
  `definition_policy.substitutions`, the master specification, the affected
  figure data contracts, and the data-integrity record consistently.
- Any changed evidence pack or figure specification invalidates its old lock.
  Re-freeze, rerun `validate_spec.py`, and rerun `lock_spec.py` before
  reproduction.
- Do not tune data, parameters, or styling solely to force visual agreement.
- Generated adjustment records must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Every finding is recorded with source evidence and an exact target.
- [ ] The user approved each applied correction before the change.
- [ ] Missing data was filled only from an approved source and provenance was
      recorded.
- [ ] Every newly discovered definition gap has an approved, complete `SUB-*`
      before any dependent figure is rerun.
- [ ] The correction did not use a published expected value as a data or output
      substitute.
- [ ] The manifest record states
      `computation_source: computed_from_approved_real_data`.
- [ ] Each corrected figure passes the agreed acceptance check.
- [ ] When a correction is applied, every included figure has an explicit
      impact classification.
- [ ] Every `affected` or `unknown` figure was rerun and verified, blocked with
      evidence, or explicitly accepted by the user.
- [ ] Master-version and stale-figure propagation are correct after shared
      definition changes.
- [ ] Every changed evidence pack and specification was re-frozen, revalidated,
      and relocked before reproduction.
- [ ] `adjustment_log.md` and `reproduction_manifest.json` contain the complete
      adjustment record.
- [ ] When the adjustment round is complete, the completion report asks the
      user to choose between `/reprospec:organize` and `/reprospec:adjust`.
- [ ] `workflow.next_stage` remains unset until the user selects a continuation
      path; `/reprospec:organize` is not presented when required work remains
      unresolved.
