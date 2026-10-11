---
name: "plan"
description: "Inspect user-provided data, confirm source origin and reliability, align it exactly with explicit master definitions or approved definition substitutes, map remaining gaps, and produce the data acquisition plan. Use only after /reprospec:detail. Do not use for final locking, execution, verification, or delivery; do not complete this stage while the integrity gate is unresolved."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.3.0"
---

## User Input

Use invocation arguments to optionally focus the review on specific data
sources, constraints, or figure IDs. If no targets are supplied, review every
user-provided dataset and the entire reproduction workspace.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `selection_confirmed`, `user_confirmed` is true, and `selection` is
  `publication_period` or `through_today`. Exact dates remain pending for
  `/reprospec:analyse`.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false.
- If any Init requirement is missing, relaxed, or unresolved, stop and return
  to `/reprospec:init`. Never continue by using a publication value or by
  bypassing the `supplement_data` or `skip` decision.
- The master outline and per-figure specifications exist.
- Figure dependencies are listed in the manifest.
- `data_integrity.json` and `data_integrity.md` exist from `/reprospec:init`.

## Goal

Determine what data is already available, what can be acquired, what can be
derived, and what cannot be reproduced. Make impacts and tradeoffs explicit
before the final specification is locked. Align each source only to an explicit
master definition or to the replacement definition of an approved `SUB-*`;
never validate an undefined paper term against an inferred interpretation.

## Execution Steps

1. Inventory local files, private datasets, notebooks, API credentials, and
   access instructions without exposing secret values.
2. Run `scripts/inspect_data.py` for every user-provided data file. Pass each
   path explicitly with `--path`; include files that have no user description.
3. Review the structural report for readability, schema, row count, duplicate
   rows, empty cells, parse errors, and format limitations.
4. For every source with unknown origin, ask how and when the data was
   obtained and from which system or provider. Wait for the answer before
   asking the next question.
5. For every source with unknown reliability, ask what evidence supports its
   reliability and which quality problems are known. Wait for the answer
   before proceeding.
6. Align each source against the master contract on fields, keys, units,
   sample, period, frequency, coverage, missing values, and transformations.
   Record `definition_basis` as `source_explicit` or
   `approved_substitution`.
7. If an item can only be aligned to an `underspecified` or `conflicting`
   original definition, stop and return to `/reprospec:outline` for a user
   decision. Do not infer the definition or mark the item `aligned`.
8. For `approved_substitution`, require the `SUB-*` to exist in
   `definition_policy.substitutions`, be user-approved, and reference the exact
   replacement `D-*` and explicit replacement definition used by the source.
9. Write accepted answers into `data_integrity.json`,
   `data_integrity.md`, `master_spec.md`, and the affected figure
   specifications.
10. Set `data_integrity.json.status` to `complete` only when every item is
   present, inspected, has a confirmed origin and reliability, is exactly
   `aligned`, has no unresolved quality risk, and is confirmed by the user.
11. Identify external source candidates such as public data, TuShare, or another
   approved API.
12. Update `data_gaps.csv` for every missing or uncertain master field and link
   it to the relevant `DATA-*` integrity item.
13. Map each gap to affected figures and the exact IDs they depend on.
14. Present concrete options, costs, risks, fallback behavior, and affected
   figures.
15. Confirm that no published or digitized expected value is being used as a
    data source, implementation input, missing-value fill, or derivation
    substitute.
16. Mark unresolved dependencies without creating a separate question file.
17. Update the manifest with the plan and data-integrity status.

## References

Read [references/planning-rules.md](references/planning-rules.md) for source
priority, tradeoff rules, and the data-gap contract.

## Decision Protocol

When origin, reliability, definition alignment, or a fallback choice
materially affects feasibility:

Present each question separately as rendered Markdown outside a code fence,
using a `**Decision Required | <topic>**` label and a context block. Do not
combine questions.

For option-based questions:

1. Present `**Recommended:** Option <letter> - <reason>` before the table.
2. Use an options table with `Option`, `Answer`, and `Implication` columns.
3. End with: "You can reply with the option letter, accept the recommendation
   by replying `yes` or `recommended`, or provide your own answer."

For short-answer questions, present
`**Suggested:** <answer> - <reason>` and end with: "You can accept the
suggestion by replying `yes` or `suggested`, or provide your own answer."

1. State the dataset, inspection evidence, and unresolved requirement.
2. Ask one provenance question: how, when, and from which system or provider
   was the data obtained? Wait for the answer.
3. Ask one reliability question: what evidence supports reliability, and what
   quality problems are known? Wait for the answer.
4. Explain any definition mismatch, quality risk, affected figures, and
   consequences of proceeding without resolution.
5. List available, acquirable, derivable, and unavailable options.
6. Recommend one option and ask exactly one resolution question.

Do not mark the integrity gate complete while any origin, reliability, or
definition-alignment item remains unresolved.

### Definition Substitution

When a source can only be aligned by interpreting an item that the paper or
report did not define:

1. Do not ask the user to diagnose the source in this stage and do not invent a
   definition.
2. Record the definition gap, the affected `D-*` and figures, and the observed
   source fields.
3. Return to `/reprospec:outline` and present the `Definition Substitution`
   decision with explicit replacement candidates and their provenance.
4. Resume Plan only after `definition_policy.substitutions` contains an
   approved `SUB-*` with a replacement `D-*` and explicit operational
   definition.
5. Re-run the alignment against that replacement definition. Set
   `definition_basis` to `approved_substitution` and record the `SUB-*`.

The integrity gate remains incomplete until the substitution is approved and
the source is exactly aligned to it.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 4/12 | PLAN**

**Status:** `completed`
**Integrity Gate:** `complete`

**Summary**

| Item | Result |
| --- | ---: |
| Available | `<count>` |
| Acquirable | `<count>` |
| Derivable | `<count>` |
| Unavailable | `<count>` |
| Definition substitutions | `<count>` |
| Affected figures | `<count>` |
| User decisions | `<count>` |

**Artifacts**

- `work/<paper-id>/data_gaps.csv`
- `work/<paper-id>/data_integrity.json`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:analyse`
>
> **Reason:** Data availability and fallback decisions are ready for the final check.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Preserve the Init-selected time-range
  mode, leave exact dates for `/reprospec:analyse`, and never change either
  silently.
- Never store secrets in tracked files or reports.
- Do not silently substitute a different source or sample.
- Do not infer a missing paper definition. Align data only to an explicit
  master definition or an approved replacement `SUB-*`.
- A `SUB-*` must be user-approved and include the exact replacement `D-*`,
  source, unit, period, universe, transformation, and known deviation.
- Do not treat expected published values as data or use them to complete a
  gap. Only approved real data and documented derivations may fill gaps.
- Do not hide data gaps.
- Never infer provenance or reliability from filenames alone.
- Never mark data integrity `complete` while a definition mismatch,
  unconfirmed origin, unknown reliability, or user confirmation is missing.
- Do not advance to `/reprospec:analyse` while the integrity gate is incomplete.
- Only ask about decisions that materially affect figures or feasibility.
- Generated plans must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] Local and external data availability was inventoried.
- [ ] Every user-provided dataset was structurally inspected.
- [ ] Origin and reliability were confirmed with the user.
- [ ] Every required data definition is exactly aligned.
- [ ] Every non-explicit definition is backed by an approved `SUB-*` and the
      integrity item records its replacement definition.
- [ ] `data_integrity.json` is `complete` with no blocking issue.
- [ ] Every material gap maps to affected figures and master IDs.
- [ ] No published value was used as a data source or missing-data substitute.
- [ ] Acquisition choices, fallbacks, and tradeoffs are recorded.
- [ ] `data_gaps.csv` and the manifest reflect the plan.
- [ ] The completion report identifies `/reprospec:analyse` as the next stage.
