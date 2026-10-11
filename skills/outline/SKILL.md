---
name: "outline"
description: "Read the complete selected paper or report, classify figures, freeze a complete per-figure source-evidence pack, extract the paper-level data outline, and negotiate explicit definition substitutes. Use only after /reprospec:init. Do not use for per-figure execution specifications, data acquisition, execution, or verification."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.4.0"
---

## User Input

Use invocation arguments only as optional scope guidance. If no paper ID is
provided, resolve the selected paper from the manifest.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `selection_confirmed`, `user_confirmed` is true, and `selection` is
  `publication_period` or `through_today`. Exact dates remain pending for
  `/reprospec:analyse`.
- If any Init requirement is missing, relaxed, or unresolved, stop and return
  to `/reprospec:init`. Never continue by using a publication value or by
  bypassing the `supplement_data` or `skip` decision.
- `work/<paper-id>/reproduction_manifest.json` exists.
- The selected paper is locked.
- `/reprospec:init` is recorded as complete.

## Goal

Create the paper-level master outline before any figure is reproduced. This
stage defines broad data definitions and processing rules, not figure-specific
plotting instructions. For every required term, metric, sample, period, unit,
and transformation, determine whether the source states an explicit
operational definition. If not, negotiate an approved substitute with an
explicit, testable definition before dependent figures may advance. Also freeze
one complete evidence pack per included figure so later stages do not need to
reread the report to discover requirements.

## Execution Steps

1. Read the entire paper and all available supporting material.
2. Include abstract, main text, methodology, captions, footnotes, appendices,
   supplementary material, and data-source statements.
3. Build a figure, panel, table, and quantitative-claim inventory.
4. Classify each image as `data_driven` or `excluded_schematic`.
5. Exclude images that communicate meaning without requiring plotted or
   tabulated data. Record excluded figures in `excluded_figures` with their
   source location and exclusion reason.
6. Create one `evidence/<figure-id>.md` from
   `assets/figure-evidence-template.md` for every included figure. Complete
   every heading with page-level source evidence, exact panel and chart facts,
   axes, labels, series, annotations, definitions, palette evidence, and
   comparison-only values.
7. Do not leave a reproduction requirement only in the report. If the evidence
   pack cannot be completed, present the unresolved evidence as a decision and
   wait. Run `scripts/finalize_evidence.py`; do not advance unless every
   evidence pack is `frozen`.
8. Fill `master_spec.md` from `assets/master-spec-template.md`.
9. Assign stable IDs: `D-*`, `T-*`, `S-*`, `Q-*`, `L-*`, and `SUB-*`.
10. Assess every required data definition as `explicit`, `missing`,
   `underspecified`, or `conflicting`. A definition is explicit only when the
   source states enough of the metric meaning, universe, period, frequency,
   unit, formula, and transformation to reproduce it without guessing.
11. For every non-explicit item, present one `Definition Substitution` decision,
   propose source-backed replacement candidates, and wait for the user's
   answer. Never infer the definition from common practice, a field name, or
   the published result.
12. Record each approved replacement as `SUB-NNN` with the original `D-*`, a
    new replacement `D-*`, its explicit operational definition, functional
    rationale, source, unit, period, frequency, universe, transformation,
    known deviation, limitations, affected figures, linked `Q-*`, and user
    approval. Update the stable data contract and data-gap register.
13. Write each accepted answer directly into `master_spec.md`, the affected
    evidence pack, and the decision table.
14. If the user cannot answer, mark the field `unresolved` and pause only
   dependent work.
15. Update `definition_policy.decision_required` and
    `definition_policy.substitutions`. Set `decision_required` to false only
    after every required definition is explicit or covered by an approved
    substitute or an explicit skip.
16. Run `scripts/finalize_evidence.py` again after any evidence-pack revision.
17. Update the manifest workflow stage, included figure inventory, excluded
    figure inventory, source-evidence status, and unresolved count.

## References

Read [references/outline-rules.md](references/outline-rules.md) for the required
extraction taxonomy and question protocol.

## Decision Protocol

### Definition Substitution

When a required definition is missing or ambiguous, present the decision as
rendered Markdown outside a code fence with the label
`**Decision Required | Definition Substitution**`.

1. Identify the original term or `D-*`, source location, and the exact missing
   or conflicting facets.
2. Explain the affected figures and why an inferred definition would make the
   reproduction untraceable.
3. Offer explicit replacement candidates when suitable approved data exists,
   and allow the user to provide their own operational definition.
4. Require the replacement to state its source field, universe, period,
   frequency, unit, formula or transformation, missing-value handling when
   material, functional relationship to the original item, and known
   deviation.
5. Recommend the candidate that best preserves the analytical role and has the
   strongest explicit definition and provenance. Never recommend a candidate
   because it is more likely to match a published value.
6. Ask exactly one question. Wait for approval before dependent specifications
   use the replacement. If no acceptable substitute exists, offer skipping the
   affected figure or claim and record the limitation.

### Other Source Gaps

When the source is insufficient to determine a material rule:

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | <topic>**` label, a context block, an options table,
and a recommended option.

1. State the issue and source location.
2. Quote the relevant source text or caption.
3. Explain what cannot be determined and the affected figures.
4. Present concrete options and the recommended option.
5. Ask exactly one question in the terminal and wait.

Do not create a separate clarification or ambiguity file.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 2/12 | OUTLINE**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Data-driven figures | `<count>` |
| Excluded schematics | `<count>` |
| Evidence packs frozen | `<count>` |
| Missing evidence items | `<count>` |
| Fields | `<count>` |
| Transformations | `<count>` |
| Definition substitutions | `<count>` |
| Unresolved definitions | `<count>` |
| Decisions confirmed | `<count>` |
| Unresolved | `<count>` |

**Artifacts**

- `work/<paper-id>/master_spec.md`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:detail`
>
> **Reason:** The paper-level outline is ready for per-figure expansion.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Preserve the Init-selected time-range
  mode, leave exact dates for `/reprospec:analyse`, and never change either
  silently.
- Scan the full document before writing the outline.
- Freeze one complete evidence pack per included figure before Detail begins.
  The pack must contain every source fact needed to build the specification.
- Do not leave a required fact only in the report or in conversational memory.
  Later stages must be able to work from the evidence pack and `spec.md`.
- Run `scripts/finalize_evidence.py` after creating or revising evidence packs.
  Do not complete Outline while any evidence pack is draft, blocked, or
  incomplete.
- Only data-driven figures enter the reproduction workflow.
- Do not create reproduction directories for excluded schematic figures.
- Record every exclusion with a source location and reason.
- Preserve source references for every extracted rule.
- Do not silently infer a missing or ambiguous definition. Require an approved
  `SUB-*` replacement or an explicit skip for every non-explicit required
  definition.
- A replacement definition must be operational and complete enough to
  reproduce; incomplete candidates remain blocked.
- Never choose or tune a substitute to match published values. The substitute
  must preserve the analytical role and document its known deviation.
- Ask one question at a time.
- Write accepted answers directly into the master specification.
- Generated documentation must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The complete document and supporting material were scanned.
- [ ] Every image is classified as included or excluded.
- [ ] Every included figure has one complete `evidence/<figure-id>.md`.
- [ ] Every evidence pack is frozen with a source hash and no unresolved
      reproduction fact.
- [ ] `master_spec.md` contains the paper-level data contract.
- [ ] Every required definition is `explicit` or covered by an approved `SUB-*`
      replacement or explicit skip.
- [ ] Every substitution records its replacement definition, provenance,
      functional rationale, known deviation, affected figures, and user
      approval.
- [ ] All material decisions are recorded in the specification.
- [ ] The completion report identifies `/reprospec:detail` as the next stage.
