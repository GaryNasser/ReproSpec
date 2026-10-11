---
name: "rework"
description: "Answer evidence-backed AI repair challenges, apply only evidence-supported minimum corrections, preserve approved definition substitutions, repair required encoding and rendering defects, and mark dependent figures stale. Use after /reprospec:verify or when a previous repair needs another round. Do not use for initial reproduction, manual adjustment, data organization, audit, or delivery."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.10.0"
---

## User Input

Use invocation arguments to select specific figure IDs or challenge IDs. If no
targets are supplied, select all figures with an `issued` AI repair challenge.
Do not ask the user to diagnose the mismatch; answer the AI-facing challenge
using repository evidence.

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
- Verification reports exist.
- Each target figure has a verification result and attribution.
- Each target figure has a valid `rework_challenge.json` with status `issued`,
  quantified or structural evidence, one AI-facing question, required response
  fields, and a reproducible acceptance check.
- A target without an issued challenge cannot enter rework. Return to
  `/reprospec:verify` instead.
- Previous rework rounds and accepted limitations are available.

## Goal

Run bounded, traceable repair rounds. A rework invocation handles one round,
not an unlimited loop. Rework must first answer the challenge from
`/reprospec:verify` with evidence, identify the root cause and the minimum set
of artifacts to change, and perform a falsification test before editing.
Chart-type or encoding mismatches require repair; a palette mismatch or blocked
source-derived palette contract requires repair; a title that is not
`matplotlib_notebook_default` or that matches the source font requires repair;
non-English plot text without a recorded exception requires repair. Every
repair must preserve real computation from approved data; published values may
guide comparison but may never be copied or hard-coded into the pipeline.

## Execution Steps

1. Read the comparison report, `rework_challenge.json`, limitations, and
   previous rework rounds.
2. Resolve target figures or select all figures with an `issued` challenge.
3. Answer every required challenge field in the challenge JSON. Use concrete
   data lineage, code locations, logs, and comparison evidence. Classify the
   cause as data, outline, detail, implementation, style, pixel, or impossible.
4. Identify at least one falsification test that can distinguish the selected
   cause from plausible alternatives. Run it before changing artifacts. If the
   test contradicts the answer, revise the response instead of editing.
5. State the minimum correction, expected effect, and the exact acceptance
   check. The acceptance check must match the challenge and may not be relaxed
   to make the result pass.
6. Run `scripts/begin_rework.py` to validate the complete answer, increment the
   round, mark dependent figures `stale`, and record the challenge handoff.
7. Apply the minimum correction using approved data and traceable code. Never
   use a published value as an input, constant, fill, coordinate, annotation,
   label, or output.
8. If the master outline or a report-derived rule changes, update and re-freeze
   the affected evidence pack with `finalize_evidence.py`, update the affected
   specifications, rerun `validate_spec.py`, and rerun `lock_spec.py` so the
   new specification and evidence hashes replace the old lock.
9. Update `rework_log.md` with the challenge ID, answer, falsification result,
   changed artifacts, affected figures, and rerun targets.
10. If no evidence-supported answer exists, set the challenge status to
    `blocked`, do not edit artifacts, and stop automatic retries. Manual
    `/reprospec:adjust` review is a later human action, not an automatic step.

Do not reopen the report to discover a requirement and patch it directly into
code or the challenge response. The fact belongs in the frozen evidence pack;
the executable rule belongs in the validated runbook.

## References

Read [references/rework-rules.md](references/rework-rules.md) for classification,
challenge answering, falsification, invalidation, and stopping rules.

## Challenge Response Protocol

The `rework_challenge.json` is an AI-to-AI repair request. Do not convert it
into a user question or wait for a user-selected repair strategy.

1. Read the challenge question and its acceptance check.
2. Gather evidence from specifications, data lineage, code, logs, and rendered
   outputs.
3. Test plausible causes and record evidence for and against each one.
4. Select one primary cause or mark the challenge `blocked`.
5. Fill all required response fields before editing.
6. Run the recorded falsification test and acceptance check after the repair.

Do not ask the user to choose a cause, supply a correction, or approve an
automatic repair. If a human business decision is truly required, mark the
challenge `blocked` and defer it to the separate `/reprospec:adjust` stage.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 8/12 | REWORK**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Round | `<round>` |
| Challenge ID | `<challenge-id>` |
| Challenge status | `answered | blocked` |
| Root cause | `<classification>` |
| Falsification test | `<result>` |
| Changed artifacts | `<count>` |
| Changed specification or evidence hashes | `<count>` |
| Specifications revalidated and relocked | `<count>` |
| Stale figures | `<count>` |
| Required chart-type corrections | `<count>` |
| Required title-style corrections | `<count>` |
| Plot-language corrections | `<count>` |
| Required palette corrections | `<count>` |
| Accepted limitations | `<count>` |

**Artifacts**

- `work/<paper-id>/rework_log.md`
- `work/<paper-id>/figures/<figure-id>/rework_challenge.json`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:reproduce <figure-ids>`
>
> **Reason:** The next repair round changes only the affected inputs or implementation.
```

When no repair is required and every figure is verified or explicitly partial,
replace the completion card's `Next` block with:

```markdown
> **Next**
>
> `/reprospec:adjust`
>
> **Reason:** Automated verification and bounded repair are complete; the figures are ready for human review.
```

When a challenge cannot be answered honestly, use `Status: blocked`, set the
challenge status to `blocked`, and identify manual `/reprospec:adjust` review as
an available human action. Do not ask the user to solve the automatic challenge.

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Repairs must preserve the exact
  user-confirmed reproduction time range.
- Multiple rework rounds are expected and must be recorded.
- A valid `issued` challenge is mandatory before any artifact may change.
- Do not reopen the report to discover or fill an execution requirement.
- Any changed evidence pack, specification, or runbook requires re-freezing,
  Detail validation, and a new lock before reproduction.
- Answer the challenge with evidence before editing. A plausible explanation
  without a causal test is not a valid answer.
- Do not ask the user to identify the cause, choose a repair path, or approve
  an automatic correction. The AI challenge is resolved inside the
  `verify -> rework -> reproduce -> verify` loop.
- Do not run `/reprospec:adjust` automatically. It remains a separate
  human-controlled stage after automatic repair is blocked or exhausted.
- Do not rerun verified figures unless a dependency changed.
- Do not invent a new master definition in a figure-only file.
- Never change or reinterpret an approved `SUB-*` automatically. If the
  challenge requires a new or different definition, block the challenge and
  return the issue to human definition negotiation before any repair.
- Do not exceed three unexplained rounds with the same root cause.
- Do not use unjustified, post hoc, or non-reproducible processing solely to
  force exact agreement with the published result. Every change must follow
  from the classified root cause and available evidence. If exact agreement
  cannot be achieved honestly, disclose the remaining mismatch and accepted
  limitation to the user instead of overfitting.
- Never copy, hard-code, backfill, interpolate, digitize, or inject a published
  expected value into data, code, axes, annotations, labels, or outputs.
- Repair a title that does not use `matplotlib_notebook_default` or that derives
  font properties from the source. Repair the title policy through `detail` or
  `implementation`; a difference from the source title font is not a defect.
- Repair palette mismatches and blocked palette contracts using the recorded
  source evidence, mapping, color-space conversion, and tolerance. A palette
  mismatch cannot remain `matched`; do not substitute arbitrary colors.
- Figure size, source fonts, other typography, lines, markers, grids, spines,
  legends, annotations, layouts, and other fine visual details need not be
  corrected to match the source.
- Do not add arbitrary cosmetic changes solely to improve a pixel score. The
  source figure, extracted colors, specification, and user instruction are the
  required evidence.
- Always repair a wrong chart type, grouping, stacking, mark, or data encoding;
  palette matching must never justify changing the chart type.
- Always repair non-English plot text unless the locked specification records
  an explicit language exception.
- Generated rework records must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Exactly one bounded rework round is recorded.
- [ ] Every target figure had an `issued` challenge before editing.
- [ ] Every required challenge response field is complete and evidence-backed.
- [ ] The correction preserves the locked definition or replacement contract;
      any need for a new definition is blocked rather than inferred.
- [ ] At least one falsification test was run and its result recorded.
- [ ] The primary root cause and minimum changed artifacts are explicit.
- [ ] All dependent figures are marked `stale`.
- [ ] Every changed specification or evidence pack was re-frozen, revalidated,
      and relocked before reproduction.
- [ ] The rework log identifies the rerun targets.
- [ ] Chart-type and encoding mismatches are repaired.
- [ ] Missing or source-derived title styling is repaired to
      `matplotlib_notebook_default`.
- [ ] No repair used a published expected value as data or a hard-coded output
      substitute.
- [ ] Unauthorized non-English plot text is repaired, while approved language
      exceptions remain explicit.
- [ ] Palette mismatches or blocked palette contracts are repaired to
      `matched` or evidenced `not_applicable`.
- [ ] Any unresolved mismatch or overfitting risk that prevents honest exact
      agreement is disclosed to the user.
- [ ] No user-facing repair question was asked and `/reprospec:adjust` was not
      invoked automatically.
- [ ] The completion report identifies the correct next stage.
