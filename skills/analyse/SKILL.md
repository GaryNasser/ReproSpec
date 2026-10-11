---
name: "analyse"
description: "Perform the final data-integrity and definition-alignment gate across the master outline, approved definition substitutions, per-figure specifications, data plan, user decisions, and feasibility, then lock the specification version. Use only after /reprospec:plan. Do not lock while any source or replacement definition is uninspected, unapproved, incomplete, or not exactly aligned. Do not use for code execution, pixel comparison, or rework."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.4.0"
---

## User Input

Use invocation arguments to optionally focus the final check on specific
master IDs, figures, or unresolved issues. If no focus is supplied, check the
entire specification set.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy` records the
  Init-confirmed mode and remains pending until this stage records and
  confirms the exact reproduction window.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false.
- If an Init policy field is missing or relaxed, stop and return to
  `/reprospec:init`. An exact window that is not final-confirmed is resolved in
  this stage by the decision protocol. Never continue by using a publication
  value or by bypassing the `supplement_data` or `skip` decision.
- `master_spec.md` exists.
- Every included figure has `spec.md`.
- `source_evidence.status` is `frozen`, and every included figure has a frozen
  evidence pack whose current SHA-256 matches `source_evidence.items`.
- Every figure specification has passed
  `/reprospec:detail/scripts/validate_spec.py`, records the evidence hash, and
  contains a self-contained execution runbook with a checked No-Reread
  Checklist.
- `data_gaps.csv` reflects the data plan.
- `data_integrity.json` and `data_integrity.md` reflect the plan review.
- The user has resolved material acquisition choices.

## Goal

Check that the master outline, detailed figure contracts, available data, and
user decisions form one consistent and executable specification. Confirm that
every figure can be executed from its `spec.md`, frozen evidence pack, and
approved source data without reopening the report. Then lock the version used
by reproduction. Before locking, preserve the time-range mode already confirmed
at Init unless the user explicitly changes it, then resolve and obtain final
user confirmation for the exact start date, end date, timezone, and basis. Also
require every non-explicit data definition to be replaced by an approved
`SUB-*` whose replacement `D-*` has an explicit, source-backed, testable
definition.

## Execution Steps

1. Read `data_integrity.json` and verify that every user-provided source has a
   completed preliminary inspection.
2. Confirm the origin and acquisition evidence of every source with the user,
   then ask a separate reliability question and wait for the answer.
3. Perform the final definition alignment against every included figure:
   fields, keys, units, currency, sample, period, frequency, coverage, missing
   values, outliers, joins, aggregations, and transformations.
4. For every required definition, require either `definition_status: explicit`
   or an approved `SUB-*` that references a replacement `D-*` and explicit
   operational definition. If a definition remains `underspecified` or
   `conflicting`, including a missing definition, return to
   `/reprospec:outline`; do not infer it here.
5. For every source, require `definition_basis` to be `source_explicit` or
   `approved_substitution`. For the latter, verify the same approved `SUB-*`
   and replacement definition are recorded in the manifest, master
   specification, figure data contract, and data-integrity item.
6. If any item is not exactly `aligned`, set the integrity status to
   `in_progress` or `blocked`, explain the data-quality impact to the user, and
   ask one resolution question. Do not proceed to locking.
7. Write accepted corrections into `data_integrity.json`,
   `data_integrity.md`, `master_spec.md`, and affected figure specifications.
8. Set `data_integrity.json.status` to `complete` only after every item is
   present, inspected, confirmed, and exactly aligned to an explicit definition
   or approved replacement.
9. Read `time_range_policy`. If `status` is not `confirmed` or the exact dates,
   timezone, or basis are missing, present the `Reproduction Time Range`
   final-window decision and wait. Preserve the Init-selected mode unless the
   user explicitly changes it; do not ask the user to choose the mode again.
   Record exactly one selection: `publication_period` or `through_today`, and
   record the reason and confirmation time for any explicit change.
10. Record the exact start date, end date, timezone, source or calculation
   basis, confirmation time, and any source-specific availability limit. Set
   `time_range_policy.status` to `confirmed`. Update the master specification,
   affected figure specifications, and data coverage checks before locking.
11. Verify `source_evidence.status: frozen`. Recompute each evidence-pack hash
    and reject any pack that changed after Outline.
12. Verify that every figure's recorded evidence hash matches its frozen pack
    and that its specification hash still matches the successful Detail
    validation record.
13. Check that every figure specification is self-contained: no report reread
    for execution requirements, no unresolved placeholders, at least one valid
    `E###` chain, a contiguous runbook, every `Sxx` field complete, explicit
    failure actions, and a fully checked No-Reread Checklist.
14. Check completeness of the master outline, figure specifications, and
    definition-substitution records.
15. Check consistency of IDs, units, samples, formulas, periods, and source
    choices against the confirmed reproduction time range.
16. Check feasibility against available, acquirable, or approved fallback data
    for the confirmed time range.
17. Check computation integrity: expected published values may appear only in
    comparison contracts; they must not be implementation inputs, data
    substitutes, hard-coded constants, missing-value fills, plot coordinates,
    annotations, labels, or output values.
18. Check traceability from every figure requirement to an explicit master ID
    or approved replacement `D-*` and its `SUB-*`.
19. Run `scripts/lock_spec.py` only when no blocking issue remains. The script
    independently re-checks the data-integrity, definition-substitution,
    source-evidence-freeze, and self-contained-specification gates.
20. Write `spec_lock.json` with version, timestamp, figure count, per-figure
    specification and evidence hashes, runbook step counts, data-integrity
    status, substitution records, and the confirmed reproduction time range.

## References

Read [references/analysis-rules.md](references/analysis-rules.md) for the final
gate, blocking rules, and lock artifact contract.

## Decision Protocol

### Reproduction Time Range

When `time_range_policy` is not confirmed, present a rendered Markdown decision
card with the label `**Decision Required | Reproduction Time Range**`.

1. Show the Init-selected mode, the paper or report period, and the current
   confirmed date.
2. Explain that the mode was already selected before input inspection and that
   this stage is now finalizing the exact input window.
3. Propose the exact ISO start date, end date, timezone, and source or
   calculation basis. For `through_today`, distinguish the confirmation date
   from the latest available observation date for each source.
4. Ask the user to confirm this exact window, or explicitly state that they
   want to change the Init-selected mode. If changing, explain the new input
   requirements and obtain the replacement mode before proposing dates.
5. Ask exactly one question and wait.

After confirmation, write the result into `time_range_policy` and
`master_spec.md`. Do not run `scripts/lock_spec.py` before this record is
complete.

### Integrity Decisions

When origin, reliability, definition alignment, or a blocking inconsistency
remains:

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | <topic>**` label, a context block, an options table,
and a recommended option.

1. Quote the source evidence and conflicting requirements with their locations.
2. If provenance is missing, ask one origin question and wait.
3. If reliability is missing, ask one reliability question and wait.
4. Explain the affected figures, data-quality risk, and lock consequence.
5. State explicitly that reproduction cannot start until the issue is resolved.
6. Present concrete resolution options and recommend one.
7. Ask exactly one resolution question and wait.

Write the answer into the integrity report and relevant specification before
repeating the final check.

### Undefined Data

If a required definition is still missing after Plan, do not invent it and do
not ask the user to choose an arbitrary interpretation here. Return to
`/reprospec:outline`, present the `Definition Substitution` decision, and
record the approved `SUB-*` before re-running the final check.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 5/12 | ANALYSE**

**Status:** `completed`
**Integrity Gate:** `complete`

**Summary**

| Check | Result |
| --- | --- |
| Master version | `<version>` |
| Figures | `<count>` |
| Time range | `<publication_period / through_today>` |
| End date | `<YYYY-MM-DD>` |
| Completeness | `PASS` |
| Consistency | `PASS` |
| Feasibility | `PASS` |
| Traceability | `PASS` |
| Definition substitutions | `<count>` |
| Unresolved definitions | `<count>` |
| Evidence packs frozen | `<count>` |
| Self-contained specifications | `<count>` |
| Runbook steps locked | `<count>` |
| Report reread requirements | `0` |
| Blocking issues | `<count>` |

**Artifacts**

- `work/<paper-id>/data_integrity.json`
- `work/<paper-id>/spec_lock.json`

> **Next**
>
> `/reprospec:reproduce`
>
> **Reason:** The final specification is locked and ready for execution.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Init owns the time-range mode; this
  stage owns the exact-window final confirmation.
- Do not lock a specification with an unresolved blocking issue.
- Do not lock while any evidence pack is missing, changed after freezing, or
  lacks a matching specification hash.
- Do not lock a figure whose runbook is incomplete, contains placeholders or
  vague instructions, or requires rereading the report to discover a
  requirement.
- Do not ask for the time-range mode again unless the user explicitly wants to
  change the Init-selected mode.
- Do not lock or start reproduction before the exact start date, end date,
  timezone, and basis are confirmed and recorded as
  `time_range_policy.status: confirmed`.
- Do not lock while any required definition is `missing`, `underspecified`, or
  `conflicting`, any `SUB-*` is unapproved or incomplete, or a source is
  aligned to a definition other than the approved replacement.
- Never lock or advance to `/reprospec:reproduce` when origin, reliability,
  definition alignment, or user confirmation is incomplete.
- Do not create code in this stage.
- Do not lock when a published value is being used as data, an implementation
  input, a hard-coded constant, a missing-data substitute, or an output value.
- Do not change the master specification silently after locking.
- Generated check reports must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] Completeness, consistency, feasibility, and traceability were checked.
- [ ] Every source passed the final data-definition alignment.
- [ ] Every non-explicit definition has an approved, complete `SUB-*` whose
      replacement definition matches the master, figure, and integrity records.
- [ ] Every data-integrity item records `definition_basis` as `source_explicit`
      or `approved_substitution`.
- [ ] Every included figure has a frozen evidence pack whose current hash
      matches `source_evidence.items`.
- [ ] Every figure specification passes the self-contained runbook gate, with
      complete `Sxx` fields and a checked No-Reread Checklist.
- [ ] Every specification hash still matches the successful Detail validation
      record.
- [ ] Computation integrity passed: no expected published value is used as an
      implementation input or data substitute.
- [ ] The Init-selected mode was preserved unless the user explicitly changed
      it, and the exact start date, end date, timezone, and basis were
      final-confirmed by the user before locking.
- [ ] `data_integrity.json` is `complete` with no unresolved item.
- [ ] No blocking issue remains.
- [ ] The master specification and figure contracts are locked.
- [ ] `spec_lock.json` records the locked version, figure count, per-figure
      specification and evidence hashes, and runbook step counts.
- [ ] The completion report identifies `/reprospec:reproduce` as the next stage.
