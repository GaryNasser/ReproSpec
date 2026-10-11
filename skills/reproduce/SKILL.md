---
name: "reproduce"
description: "Execute locked self-contained figure runbooks from specification and frozen evidence hashes, acquiring approved data only as directed and preserving replacement definitions, chart types, encodings, palettes, default title styling, adaptive canvas sizing, and PNG output. Stop and return to analysis if any locked hash changes, or to detail/outline when the runbook is insufficient. Use only after /reprospec:analyse or after an adjust or rework decision marks figures stale. Do not use for final verification or repair classification."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.10.0"
---

## User Input

Use invocation arguments to select specific figure IDs. If no figure IDs are
provided, process all locked figures whose status is `draft`, `stale`, or
explicitly requested by the user.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `confirmed`, `selection` is `publication_period` or `through_today`,
  `user_confirmed` is true, and the exact ISO start and end dates, timezone,
  and basis are recorded.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false. Every non-explicit source
  definition used by a target figure has an approved `SUB-*`.
- If the Init policy is missing or relaxed, stop and return to
  `/reprospec:init`. If `time_range_policy.status` is not `confirmed` or the
  exact window is invalid, stop and return to `/reprospec:analyse`. Never
  continue by using a publication value or by bypassing the `supplement_data`
  or `skip` decision.
- The manifest contains a locked master specification.
- The final time-range confirmation includes a valid `start_date` not later
  than `end_date`.
- `data_integrity.json.status` is `complete` and every item is exactly aligned.
- `source_evidence.status` is `frozen`.
- `spec_lock.json` exists and records the same current SHA-256 for each target
  `spec.md` and frozen evidence pack.
- Target figures are `draft`, `stale`, or explicitly requested by the user.
- Required data sources and fallbacks are approved and known.

## Goal

Execute one or more locked figure specifications and produce reproducible
artifacts that match the data, required chart type, and mandatory source-derived
palette contract. Palette matching must never change the chart type. Apply
`matplotlib_notebook_default` to visible overall and per-panel titles, keep them
centered, and let the implementation choose or automatically adjust the canvas
size; no fixed canvas dimensions are read from `spec.md`. Do not derive title
font properties from the source or require imitation of other fine visual
details. Use English plotted text by default. Never execute a figure whose
master specification is not locked.

Execute the numbered `Sxx` runbook exactly. The allowed report-derived inputs
are the locked `spec.md` and its frozen `evidence/<figure-id>.md` pack.
`/reprospec:reproduce` must not reopen the paper or report to discover,
reinterpret, or fill an execution requirement. If the runbook is insufficient,
stop and return to `/reprospec:detail`; if the evidence pack is incomplete,
return to `/reprospec:outline`.

## Execution Steps

1. Read `spec_lock.json` and verify the confirmed reproduction time range
   against the locked specification. Reproduce only within its exact start and
   end dates.
2. Recompute the SHA-256 of every target `spec.md` and frozen evidence pack.
   Compare them with `spec_lock.json`, the manifest Detail validation record,
   and the evidence hash written in the specification.
3. Re-check the approved source hashes, `definition_basis` values, and
   `SUB-*` replacement definitions against `data_integrity.json` and the
   locked master specification.
4. If any source changed, is missing, or no longer matches the confirmed
   explicit definition or approved replacement, stop immediately and return to
   `/reprospec:analyse`. If any specification or evidence hash differs from
   `spec_lock.json`, stop and return to `/reprospec:analyse` for relocking. Do
   not reproduce from unapproved data or fall back to an inferred paper-term
   definition.
5. Resolve the target figure IDs or select all locked figures.
6. Read only the target `spec.md`, its frozen evidence pack, and the approved
   source-data contract. Do not open the report to discover requirements.
7. If an input, field, formula, parameter, code entrypoint, validation,
   failure action, or handoff is missing or ambiguous, mark the figure
   `blocked` and return to `/reprospec:detail`. If the evidence pack lacks the
   required fact, return to `/reprospec:outline`. Do not improvise and do not
   reread the report.
8. Acquire approved data and store raw inputs immutably.
9. Record source, query, retrieval time, parameters, schema, row count, hash,
   `definition_basis`, and any `SUB-*` replacement definition used.
10. Execute the numbered `Sxx` steps in dependency order. For every step,
    record its step ID, command or function, parameters, input path or hash,
    output path or hash, validation result, failure action, and handoff in the
    run record. Do not skip, merge, or reorder dependent steps.
11. Implement the required chart type and data-to-mark encoding for every
    panel. Compute every value and coordinate from approved real data;
    published numbers are comparison targets only and must never be hard-coded
    or copied into the pipeline.
12. Choose or automatically compute a canvas size from the source aspect ratio,
   panel layout, text, and content. Do not read or enforce a fixed size from
   `spec.md`. A general `figsize=(12, 5)` fallback may be used only as a
   non-binding recommendation.
13. Apply the `matplotlib_notebook_default` title contract after all imports,
   styles, and theme setup. Resolve title family, size, and weight from
   `matplotlib.rcParamsDefault`, using `figure.*` defaults for an overall title
   and `axes.*` defaults for panel titles. Resolve the concrete default font
   face selected by the default family and fallback chain, not only the generic
   `sans-serif` alias. Pin the resolved properties on the title text, then
   center visible overall and per-panel titles after layout adjustments. Never
   infer or override title properties from the source figure.
14. Render titles, axes, ticks, legends, annotations, and panel labels in
    English. Use another language only when `spec.md` records an explicit
    user-requested exception.
15. Apply the mandatory source-derived palette contract. Use exact vector
    colors when available; otherwise use the recorded raster samples and map
    them to the required series, categories, panels, and colorbars. If the
    palette is `not_applicable`, require the recorded evidence. If the contract
    is `blocked` or cannot be applied, mark the figure `blocked`; do not choose
    replacement colors. Palette matching must not change the required chart
    type. Typography other than the mandatory default title style and other
    fine visual details need not be imitated.
16. Save code under the figure's `src/` directory.
17. Save the rendered figure as PNG under `output/`. Generate another format
    only when `spec.md` explicitly requires it.
18. Save run logs, environment metadata, intermediate data, and the complete
    per-step run record at `logs/run_record.json`. Set
    `report_reread_for_requirements` to `false` and leave `reread_events`
    empty.
19. Verify that every `Sxx` step has a completed run-record entry and that every
    required validation passed. Do not mark the figure reproduced if any step
    is missing or failed. Run
    `python scripts/validate_run_record.py --workspace <workspace> --paper-id <paper-id>`.
    The validator compares the run record with the locked specification and
    evidence hashes, requires every `Sxx` step, rejects reread events, and
    records the run-record hash in the manifest.
20. Update the figure status to `reproduced`.
21. If an approved source cannot be accessed or the pipeline fails, mark only
    that figure `blocked` and explain the exact blocker.

## References

Read [references/reproduction-rules.md](references/reproduction-rules.md) for
artifact, provenance, execution, and failure rules. Run
[scripts/validate_run_record.py](scripts/validate_run_record.py) after
execution and before marking figures reproduced.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 6/12 | REPRODUCE**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Targets | `<count>` |
| Time range | `<publication_period / through_today>` |
| End date | `<YYYY-MM-DD>` |
| Completed | `<count>` |
| Failed | `<count>` |
| Outputs | `<count>` |
| Data sources | `<count>` |
| Runbook steps executed | `<count>` |
| Runbook steps missing | `0` |
| Report reread events | `0` |
| Returned to Detail or Outline | `<count>` |
| Chart type mismatches | `<count>` |
| Title-style mismatches | `<count>` |
| Plot-language exceptions | `<count>` |
| Palette contract failures | `<count>` |
| Additional output formats | `<count>` |

**Artifacts**

- `work/<paper-id>/figures/<figure-id>/output/`
- `work/<paper-id>/figures/<figure-id>/logs/`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:verify <figure-ids>`
>
> **Reason:** The listed figures have rendered outputs ready for verification.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Use only the exact user-confirmed
  reproduction time range.
- Do not change the locked specification during execution.
- Never reproduce when the data-integrity gate is incomplete or a source hash
  or definition has changed.
- Never reproduce when a specification or evidence hash differs from
  `spec_lock.json`; return to `/reprospec:analyse` and relock.
- Never open the paper or report to discover, reinterpret, or fill a
  requirement during reproduction.
- If the locked runbook is insufficient, stop and return to
  `/reprospec:detail`; if the frozen evidence pack is incomplete, return to
  `/reprospec:outline`. Do not improvise a figure-local rule.
- Execute the `Sxx` runbook in dependency order and record every step. Do not
  skip, merge, or silently change a step.
- Run `scripts/validate_run_record.py` after execution. A failed validation
  blocks `reproduced` status and `/reprospec:verify`.
- Never interpret an `underspecified` or `conflicting` term at runtime. Execute
  only the explicit definition or the approved replacement `D-*` named by its
  `SUB-*`.
- Never reproduce outside the exact time range confirmed by the user. For
  `through_today`, do not move the end date forward without reopening
  `/reprospec:analyse`.
- Never overwrite raw source data.
- Never expose credentials in logs or artifacts.
- Never copy or hard-code published values into data, code, axes, annotations,
  labels, or output values. Reproduced values must be computed from approved
  real data.
- Source-derived palette colors are rendering metadata, not quantitative
  values. They may be applied as style constants under the mandatory palette
  contract.
- A rendered image alone does not make a figure verified.
- Preserve the required chart type and data encoding for every panel.
- Apply `matplotlib_notebook_default` after all style and theme setup. Resolve
  the default title family, size, and weight from `matplotlib.rcParamsDefault`
  and pin them on overall and panel title text.
- Never derive title font family, size, or weight from the published figure.
  Center visible overall and per-panel titles after layout adjustments.
- Do not read a fixed canvas size from `spec.md`. Choose or automatically
  adjust the canvas from the source aspect ratio, panel layout, text, and
  content. A general `figsize=(12, 5)` fallback is non-binding.
- Use English for all plotted text unless the locked specification records an
  explicit user-requested language exception.
- Apply the mandatory source-derived palette contract. Exact vector colors are
  preferred; otherwise use the recorded raster sampling, mapping, and tolerance.
  `not_applicable` requires evidence. A blocked palette prevents `reproduced`
  status; a mismatch detected during verification prevents `matched`.
  Typography other than the mandatory default title policy and other fine
  visual details need not be matched.
- Produce PNG by default and write additional formats only when the locked
  rendering contract explicitly requires them.
- Generated artifacts must use English file names and documentation.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] Every target specification and evidence-pack hash matches
      `spec_lock.json` and the Detail validation record.
- [ ] The paper or report was not reread to discover execution requirements.
- [ ] Every `Sxx` runbook step has a recorded command or function, input,
      parameters, output, validation result, failure action, and handoff.
- [ ] No runbook step is missing, skipped, merged, or silently reordered.
- [ ] `scripts/validate_run_record.py` passed for every target figure and
      recorded the run-record hash in the manifest.
- [ ] Approved data is stored immutably with provenance.
- [ ] Every output value and coordinate was computed from approved real data,
      with no published value copied or hard-coded into the pipeline.
- [ ] Every source still matches the confirmed integrity record.
- [ ] Every substituted input uses the approved replacement definition and
      records its `SUB-*`; no inferred original definition was used.
- [ ] Reproduction used the exact user-confirmed time range and end date.
- [ ] Each target figure has code, logs, intermediate data, and rendered output.
- [ ] Each output uses an adaptive or content-driven canvas size; no fixed
      canvas size is read from the figure specification.
- [ ] Every panel matches the required chart type and data encoding.
- [ ] Overall and panel titles use the resolved
      `matplotlib_notebook_default` family, size, and weight without
      source-derived font matching.
- [ ] Visible overall and per-panel titles are centered.
- [ ] All plotted text is English unless an explicit specification exception
      is recorded.
- [ ] Each figure has a PNG output; additional formats exist only when the
      specification explicitly requires them.
- [ ] The mandatory source-derived palette contract is applied, or
      `not_applicable` is supported by evidence.
- [ ] Figure statuses and failures are updated in the manifest.
- [ ] No locked specification was changed during execution.
- [ ] The completion report identifies specific figures for `/reprospec:verify`.
