---
name: "verify"
description: "Verify reproduced figures against published evidence while preserving approved definition substitutions, required chart types, data encodings, palettes, default title styling, English plot text, and computation provenance; quantify differences and issue evidence-backed AI repair challenges for confirmed mismatches. Use only after figures have been reproduced and before /reprospec:rework. Do not use for source acquisition, initial execution, or final repair decisions."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.12.0"
---

## User Input

Use invocation arguments to select specific reproduced figure IDs. If no
targets are supplied, verify all figures currently marked `reproduced`.

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
- Target figures exist.
- The manifest records those figures as `reproduced`.
- `spec_lock.json` and the manifest Detail validation record match the current
  `spec.md` and frozen evidence-pack SHA-256 for every target figure.
- Each target figure has `run_validation.status: passed`, and its recorded
  run-record hash still matches `logs/run_record.json`.
- Each target run record identifies the locked specification and evidence
  hashes, sets `report_reread_for_requirements` to `false`, and contains one
  completed entry for every runbook `Sxx` step.
- Published figures or source evidence are available at the best obtainable
  resolution.
- For re-verification after rework, any existing `rework_challenge.json` for the
  target figure is available and identifies the prior acceptance check.

## Goal

Determine whether each local output preserves the required chart type and data
encoding, uses `matplotlib_notebook_default` for titles, centers visible
titles, uses English plot text, and satisfies the mandatory source-derived
palette contract, then determine how closely its data matches the published
figure. Source title fonts and detailed visual styling are not acceptance
targets. Use exact published values first, vector evidence second, and raster
pixel extraction third. For every confirmed mismatch, issue an evidence-backed
AI repair challenge to `/reprospec:rework`; never ask the user to resolve a
machine verification mismatch.

## Execution Steps

1. Resolve target figure IDs or select all reproduced figures.
2. Extract the published figure at the highest available resolution.
3. Record exact printed values when available.
4. Extract vector coordinates when the PDF provides vector graphics.
5. Calibrate axes and digitize raster pixels when direct values are unavailable.
6. Save calibration data, extracted values, masks, and overlay images under
   `pixel_evidence/`.
7. Compare the overall and per-panel chart types and data-to-mark encoding.
   A stacked bar chart must remain stacked bars, a line chart must remain
   lines, a scatter plot must remain points, and every other type must remain
   faithful to the source.
8. Verify that titles, axes, ticks, legends, annotations, and panel labels are
   English unless the specification records an explicit language exception.
9. Verify the title-style policy from the run record, rendering code, and title
   objects. Overall and panel titles must resolve family, size, and weight from
   `matplotlib.rcParamsDefault` under `matplotlib_notebook_default`; a
   source-derived title font override is a defect. Then verify that visible
   overall and per-panel titles are centered.
10. Verify the mandatory palette contract. Use exact vector colors when
    available; otherwise compare the recorded representative raster samples,
    mark mapping, color-space conversion, and acceptance tolerance. Mark
    `not_applicable` only when evidence shows no color-dependent encoding. A
    mismatch or unverifiable palette prevents a `matched` result. Save palette
    evidence under `pixel_evidence/`. Do not require matching figure size,
    source fonts, margins, lines, markers, grids, spines, legends, annotations,
    backgrounds, or other fine visual details.
11. Confirm that local values were computed independently from approved real
    data and that no published or digitized expected value entered the local
    data pipeline, code, coordinates, annotations, labels, or outputs. Record
    `verification.computation_provenance` as
    `computed_from_approved_real_data` only when the run records, data lineage,
    and code support that conclusion. Otherwise record
    `copied_published_value` or `blocked`.
12. Verify that the run record did not reopen the report to discover
    requirements: `report_reread_for_requirements` must be `false`, all
    `reread_events` must be empty, and every `Sxx` step must have a completed
    execution entry with its command, input, output, validation, and handoff.
    A missing step, a changed hash, or a report reread event is a blocking
    provenance defect.
13. For substituted data, confirm the pipeline used the approved replacement
    `D-*`, explicit replacement definition, and known deviation. Do not treat a
    difference caused by an approved substitute as an implementation defect or
    ask rework to tune the substitute toward the published value.
14. Compare expected and actual series with `scripts/summarize_series.py`.
    Preserve the expected input, actual input, comparison output, error
    metrics, tolerance, and exact evidence paths. A subjective visual
    impression is not a confirmed mismatch.
15. Classify the result as `matched`, `partial`, `mismatched`, or `blocked`.
16. When a required series, point, chart encoding, or rendering contract has a
    confirmed mismatch that can be acted on, create or update
    `rework_challenge.json` for that figure from
    `assets/rework-challenge-template.json`. Set its status to `issued`, include
    the quantified deviation and exact evidence, ask one AI-facing question,
    and define the acceptance check. Do not ask the user a repair question and
    do not invoke `/reprospec:adjust`.
17. On re-verification, apply the challenge's recorded acceptance check. If
    the mismatch is resolved, set the challenge status to `resolved` and record
    the resolution evidence. If it persists, set the status back to `issued`,
    increment the attempt, refresh the evidence, and require another rework
    response. After three unresolved attempts for the same challenge, set the
    status to `blocked`; do not create an infinite loop.
18. Produce `comparison_report.md` from the skill template, including the AI
    challenge and rework handoff.
19. Attribute required result differences to data, outline, detail,
    implementation, style, pixel, mixed, or unknown. Report palette outcome as
    a required result, never as optional guidance.
20. Create `limitations.md` when a figure cannot be fully verified. Record an
    approved definition deviation as a documented limitation when it explains
    a persistent difference from the published figure.
21. Update the figure status, computation provenance, runbook coverage,
    challenge state, and
    report consistency in the manifest, then report the results to the user.

## References

Read [references/verification-rules.md](references/verification-rules.md) for
evidence priority, pixel extraction, comparison, AI challenge, and attribution
rules. Use [assets/rework-challenge-template.json](assets/rework-challenge-template.json)
for every confirmed mismatch that is handed to `/reprospec:rework`.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 7/12 | VERIFY**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Figures checked | `<count>` |
| Matched | `<count>` |
| Within tolerance | `<count>` |
| Mismatched | `<count>` |
| Chart type matches | `<count>` |
| Chart type mismatches | `<count>` |
| Title-style mismatches | `<count>` |
| Title-alignment mismatches | `<count>` |
| Plot-language exceptions | `<count>` |
| Palette mismatches | `<count>` |
| Palette-blocked figures | `<count>` |
| Complete runbook coverage | `<count>` |
| Missing runbook steps | `<count>` |
| Report reread events | `0` |
| AI challenges issued | `<count>` |
| AI challenges resolved | `<count>` |
| AI challenges blocked | `<count>` |
| Attribution categories | `<count>` |

**Artifacts**

- `work/<paper-id>/figures/<figure-id>/comparison_report.md`
- `work/<paper-id>/figures/<figure-id>/pixel_evidence/`
- `work/<paper-id>/figures/<figure-id>/rework_challenge.json`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:rework`
>
> **Reason:** Machine verification is complete and the findings are ready for bounded automatic repair.
```

When no challenge is issued or reopened and all figures are matched, resolved,
or explicitly partial, replace the `Next` block with:

```markdown
> **Next**
>
> `/reprospec:adjust`
>
> **Reason:** Automatic verification and any challenge-driven rework are complete; unresolved human findings may now enter manual adjustment.
```

When a challenge reaches `blocked` after three attempts, use `Status: blocked`,
do not issue another automatic challenge, and identify manual `/reprospec:adjust`
review as an available human action. Do not run `/reprospec:adjust`
automatically and do not ask the user to diagnose the mismatch.

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Verify against the exact user-confirmed
  reproduction time range.
- Never use visual similarity alone as proof.
- Chart type and data encoding are mandatory. A type mismatch cannot be
  classified as `matched`.
- Plot text must be English unless the specification records an explicit
  language exception. Non-English plot text without that exception is a
  required defect.
- Visible overall and per-panel titles must be centered. Incorrect title
  alignment is a required defect.
- Overall and panel titles must follow `matplotlib_notebook_default`. Missing,
  overridden, or source-derived title font properties are required defects.
- Do not compare, require, or gate on source title font similarity. Verify the
  fixed default title policy separately from optional visual similarity.
- Palette matching is mandatory whenever color encodes data. A mismatch,
  missing mapping, or unverifiable palette prevents `matched`.
- `not_applicable` requires explicit evidence that the figure has no
  color-dependent encoding. Figure size, source fonts, and other fine visual
  details are not acceptance targets.
- Preserve pixel uncertainty.
- Keep published values distinct from extracted estimates.
- Treat published and extracted values as comparison artifacts only. If local
  agreement depends on copying or hard-coding them, the comparison is invalid.
- Never tune a substitute or infer a different definition to improve
  agreement. Verify against the locked `SUB-*` replacement definition exactly.
- Never mark computation provenance as `computed_from_approved_real_data` when
  a run record, intermediate artifact, code path, coordinate, annotation, or
  output depends on a published or digitized expected value.
- Do not mark computation provenance as `computed_from_approved_real_data` when
  the run record has a changed specification or evidence hash, a missing
  runbook step, or a report reread event.
- Source-derived palette colors are rendering metadata, not quantitative
  values. Their use in style code does not violate computation provenance when
  the mandatory palette contract is followed.
- A confirmed actionable mismatch must produce an AI-facing
  `rework_challenge.json`; it must not produce a user-facing repair question.
- The challenge must contain quantified or structural evidence, one main
  question, required structured response fields, and a reproducible acceptance
  check. Rework must answer it with evidence before editing.
- Do not use the challenge to request a post hoc fit. The answer must identify
  a real data, specification, implementation, style, or pixel cause and may not
  use published values as inputs or constants.
- Keep challenge statuses limited to `issued`, `answered`, `resolved`, and
  `blocked`. After three unresolved attempts, stop automatic retries.
- Do not invoke or modify `/reprospec:adjust`. Manual adjustment remains a
  separate human-controlled stage after automatic repair is exhausted.
- Do not modify the master specification in this stage.
- Generated verification reports must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Published values, vector coordinates, or pixel evidence are preserved.
- [ ] Overall and per-panel chart types and data encodings are verified.
- [ ] Plot text language is verified against the English default or a recorded
      exception.
- [ ] Overall and panel titles are verified against
      `matplotlib_notebook_default`, with no source-derived font matching.
- [ ] Visible overall and per-panel title alignment is verified as centered.
- [ ] Palette outcome is verified as `matched`, evidenced `not_applicable`, or
      a blocking `mismatched`/`blocked` result.
- [ ] Numerical differences and tolerances are quantified.
- [ ] Local values were independently computed from approved real data, with
      no published value copied or hard-coded into the pipeline.
- [ ] Every target run record matches the locked specification and evidence
      hashes and contains completed entries for every `Sxx` runbook step.
- [ ] No report reread event or missing runbook execution entry was found.
- [ ] Every substituted input used its locked `SUB-*` replacement definition,
      and any known deviation remained an explicit limitation rather than an
      invitation to tune the result.
- [ ] Every figure records a verified computation provenance of
      `computed_from_approved_real_data`, `copied_published_value`, or
      `blocked`.
- [ ] Every mismatch has a primary attribution.
- [ ] Every confirmed actionable mismatch has an evidence-backed
      `rework_challenge.json` with an AI-facing question and acceptance check.
- [ ] Existing challenges are marked `resolved` only after the same acceptance
      check passes, or `blocked` after three failed rework attempts.
- [ ] No machine mismatch was converted into a user repair question and no
      automatic `/reprospec:adjust` invocation was made.
- [ ] Each partial or blocked figure has `limitations.md`.
- [ ] The completion report identifies `/reprospec:rework` as the next stage.
