---
name: "detail"
description: "Expand included data-driven figures into self-contained, step-by-step reproduction runbooks backed by frozen source-evidence packs, resolving every data dependency through an explicit source definition or approved definition substitute. Use only after /reprospec:outline. Do not create specifications for schematic or conceptual images. Do not use for data tradeoff planning, execution, verification, or repair."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.10.0"
---

## User Input

Use invocation arguments to optionally limit the stage to specific included
figure IDs. If no targets are supplied, process every included `data_driven`
figure.

## Pre-Execution Checks

- The requirements established by `/reprospec:init` are present and enforced:
  `computation_policy.status` is `enforced`, publication values are
  `comparison_only`, reproduction inputs are `approved_real_data_only`, and
  `data_plan.decision_required` is false. The `time_range_policy.status` is
  `selection_confirmed`, `user_confirmed` is true, and `selection` is
  `publication_period` or `through_today`. Exact dates remain pending for
  `/reprospec:analyse`.
- `definition_policy.status` is `enforced` and
  `definition_policy.decision_required` is false. Every non-explicit master
  definition used by a target figure has an approved `SUB-*` record.
- If any Init requirement is missing, relaxed, or unresolved, stop and return
  to `/reprospec:init`. Never continue by using a publication value or by
  bypassing the `supplement_data` or `skip` decision.
- `master_spec.md` exists and contains the paper-level outline.
- The included and excluded figure inventories are available in the manifest.
- `source_evidence.status` is `frozen`. Every target included figure has one
  frozen `evidence/<figure-id>.md` item with a matching SHA-256.
- The report or paper is not opened in this stage to discover requirements. If
  a required fact is absent from the frozen evidence pack or master outline,
  stop and return to `/reprospec:outline`.

## Goal

Create one detailed specification directory per included data-driven figure.
The result must be an execution runbook detailed enough that a fresh agent can
build and validate the figure from `spec.md`, the frozen evidence pack, and
approved source data without rereading the paper or report or relying on
conversation memory.

Every report-derived rule must cite an `E###` evidence ID. Every input,
field, dtype, filter, join, formula, parameter, code entrypoint, output,
validation, failure action, and handoff must be explicit. Every data dependency
must use either a source definition explicitly recorded in the master
specification or the replacement `D-*` named by an approved `SUB-*`.

Preserve the published chart type as a hard requirement. Require centered title
alignment and the default Matplotlib Notebook title font and size, resolved
from `matplotlib.rcParamsDefault` independently of the source figure. Do not
prescribe fixed canvas or output dimensions; any general starting size is a
non-binding recommendation outside the per-figure specification. Treat the
source palette as a required display contract for every figure with
color-dependent encoding. Do not require imitation of other fine visual
details. Use English for all plotted text by default.

## Execution Steps

1. Read the included `figures`, `excluded_figures`, and `source_evidence`
   entries from the manifest. Stop if evidence is not frozen.
2. Process only included data-driven figures. Do not create directories for
   `excluded_schematic` figures.
3. Read the target frozen evidence pack before writing the specification. Read
   the master outline only for paper-level definitions, substitutions, and
   shared rules. Do not open the report or paper to discover additional
   requirements.
4. Read
   [references/execution-runbook-standard.md](references/execution-runbook-standard.md)
   before defining the steps.
5. Create one figure directory with `scripts/init_figure.py`. The script must
   populate the evidence path and hashes from the frozen manifest record.
6. Fill each `spec.md` from `assets/figure-spec-template.md`. Replace every
   template placeholder and complete every heading.
7. Build the Specification Evidence Map first. Link each executable
   specification area to the exact `E###` rows that support it and record the
   exact rule or fact.
8. List the exact master IDs and substitution IDs used by the figure.
9. Verify every master dependency is `explicit` or is replaced by an approved
   `SUB-*`. If not, stop this figure and return to `/reprospec:outline`; do not
   infer a definition in the figure specification.
10. In the data contract, retain the original `D-*`, reference the replacement
    `D-*` and `SUB-*`, repeat the explicit replacement definition, and record
    the known deviation. Do not treat the original underspecified term as
    executable.
11. Define the input artifact contract and global transformation contract
    before writing steps. State exact paths or sources, row grain, fields,
    dtypes, units, time filters, join cardinality, sort order, missing-value
    rule, outlier rule, revision rule, conversion, and rounding.
12. Define every operation as a contiguous `S01`, `S02`, and so on. Each step
    must state `Depends on`, `Input`, `Operation`, `Formula or logic`,
    `Parameters`, `Code entrypoint`, `Output`, `Validation`, `Failure action`,
    and `Handoff`.
13. Split steps whenever the input artifact, schema, row grain, join or
    aggregation boundary, formula, unit, output artifact, validation method,
    or failure action changes. Do not combine unrelated operations.
14. Keep all published numbers in the comparison contract only. Do not use
    them as source data, implementation inputs, hard-coded values, missing-data
    fills, plot coordinates, annotations, labels, or output values.
15. Define the chart type contract before implementation details, including
    overall and per-panel chart types and required data-to-mark encoding. Do
    not allow a type change.
16. Define the rendering contract. Require overall and per-panel titles to use
    `matplotlib_notebook_default`, centered independently of the source figure.
    Do not derive title family or size from source evidence. Use an adaptive
    canvas-sizing policy; do not write fixed canvas dimensions, output pixel
    dimensions, or a required `figsize` into `spec.md`.
17. Set the plot text language to English. Require an explicit user request or
    documented exception before using another language.
18. Record a mandatory palette contract for every color-dependent encoding.
    Use exact vector colors when available; otherwise record representative
    sampled colors, sampling regions, extraction uncertainty, color mapping,
    and acceptance tolerance. Mark the palette `not_applicable` only when
    evidence shows that no color-dependent encoding exists.
19. Define the artifact, validation, comparison, and stop-condition contracts.
    Every runbook step must produce or consume a named artifact, and every
    validation must be able to fail. Published values remain comparison-only.
20. Complete the No-Reread Checklist. Every item must be checked.
21. Record the output formats. Default to PNG only and document any requested
    or required additional format.
22. Perform a preflight check against the master outline, including every
    substitution ID and replacement definition.
23. If the outline or evidence pack is insufficient, return to
    `/reprospec:outline`, revise the shared record, re-freeze it, and recreate
    or update the figure specification. Do not add a figure-only override.
24. Run
    `python scripts/validate_spec.py --workspace <workspace> --paper-id <paper-id>`.
    The script validates the evidence hashes, evidence IDs, step fields,
    placeholders, prohibitions, and No-Reread Checklist, then records the
    specification hash in the manifest. Do not complete this stage while any
    figure fails validation.
25. Update the manifest with figure paths, dependencies, substitution IDs,
    statuses, evidence hashes, and successful detail-validation records.

## References

Read [references/detail-rules.md](references/detail-rules.md) for the detailed
specification contract and
[references/execution-runbook-standard.md](references/execution-runbook-standard.md)
for the self-contained runbook standard.

## Decision Protocol

When a figure rule still cannot be determined after checking the frozen
evidence pack, master outline, and available data:

Present the decision as rendered Markdown outside a code fence, using a
`**Decision Required | <topic>**` label, a context block, an options table,
and a recommended option.

1. State the unresolved rule and its source location.
2. Explain which figures or steps are affected.
3. Present concrete options and the recommended option.
4. Ask exactly one question and wait.

If the missing fact belongs to the report itself, do not ask the user to
reinterpret the paper in Detail. Return to `/reprospec:outline`, record the
answer in the evidence pack, and re-freeze it. Write accepted answers into the
relevant specification and the master outline when the rule is shared.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 3/12 | DETAIL**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Figures specified | `<count>` |
| Excluded schematics | `<count>` |
| Master dependencies | `<count>` |
| Definition substitutions | `<count>` |
| Unapproved definitions | `<count>` |
| Evidence packs frozen | `<count>` |
| Self-contained specifications | `<count>` |
| Runbook steps | `<count>` |
| Missing evidence IDs | `<count>` |
| Report reread requirements | `0` |
| Chart type contracts | `<count>` |
| Plot-language exceptions | `<count>` |
| Preflight failures | `<count>` |
| Outline revisions | `<count>` |
| Palette contract failures | `<count>` |
| Figures with extra formats | `<count>` |

**Artifacts**

- `work/<paper-id>/figures/<figure-id>/spec.md`
- `work/<paper-id>/evidence/<figure-id>.md`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:plan`
>
> **Reason:** All known figures now have detailed specifications and dependency maps.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Preserve the Init-selected time-range
  mode, leave exact dates for `/reprospec:analyse`, and never change either
  silently.
- One included figure gets one directory and one `spec.md`.
- Create directories only for included data-driven figures.
- Never create a reproduction directory for an excluded schematic.
- Do not create implementation code in this stage.
- Do not open the paper or report to discover requirements. Use only the frozen
  evidence pack, master outline, and approved source-data contract.
- Do not leave any `{{placeholder}}`, `TBD`, `TODO`, or unchecked No-Reread
  Checklist item.
- Do not leave vague steps such as "clean data", "handle appropriately",
  "normalize as needed", or "use a suitable source".
- Every report-derived executable fact must cite an `E###` evidence ID.
- Every runbook step must include all required fields, exact parameters, a
  code entrypoint, an objective validation, an explicit failure action, and
  the artifact handed to the next step.
- If the frozen evidence pack lacks a fact needed to specify the figure, stop
  and return to `/reprospec:outline`; never fill the gap from memory or a
  report reread.
- Do not silently change master definitions.
- Do not specify a figure from an `underspecified` or `conflicting` definition.
  Use only the replacement `D-*` in an approved `SUB-*` contract.
- Record each substitution ID, replacement definition, and known deviation in
  the figure data contract so implementation and verification do not fall back
  to the original vague term.
- Treat paper or report numbers as comparison targets only. Never use them as
  source data, implementation inputs, hard-coded values, missing-data fills,
  plot coordinates, annotations, labels, or output values.
- Source-derived palette colors are rendering metadata, not quantitative
  values. They may be recorded as style constants under the mandatory palette
  contract.
- Require visible overall and per-panel titles to be centered after layout
  adjustments.
- Require overall and per-panel titles to use
  `matplotlib_notebook_default`, sourced from `matplotlib.rcParamsDefault`.
  Never derive title family, size, or weight from the published figure.
- Do not write fixed canvas dimensions, output pixel dimensions, or a required
  `figsize` into figure specifications. Allow the implementation to choose or
  automatically adjust the canvas from source aspect ratio, panel layout, text,
  and content. A general `figsize=(12, 5)` value may be recommended outside a
  figure specification, but it is non-binding.
- Require a source-derived palette whenever color encodes data. Record exact or
  sampled colors, the mapping to marks, and the acceptance tolerance. Use
  `not_applicable` only with evidence that no color-dependent encoding exists.
  For raster sources, palette colors must be produced by raster-level pixel
  sampling (record sampling method, source region, exact RGB/hex, color space,
  series mapping, and tolerance); qualitative color names alone are
  insufficient, and a raster palette that cannot be sampled must be marked
  `blocked`.
  Do not require or gate on non-title typography, margin, line, marker, grid,
  spine, legend, annotation, or similar fine visual details.
- Default to PNG output only; require an explicit source-based or user-requested
  reason before adding another format.
- Treat chart type, data encoding, and source-derived palette matching as
  mandatory.
- Require English plotted text by default. Translate titles, labels, ticks,
  legends, annotations, and panel text while preserving symbols, units,
  acronyms, and numeric values.
- Record uncertainty when source resolution or compression prevents reliable
  palette measurement.
- Generated specifications must be English.
- Run `scripts/validate_spec.py` after writing or revising a specification and
  before completing the stage. A failed validation blocks `/reprospec:plan`.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] Every included figure has one directory and one `spec.md`.
- [ ] Excluded schematic figures have no reproduction directory.
- [ ] Every processing step is numbered, testable, and traceable.
- [ ] Every report-derived executable requirement cites a frozen `E###`
      evidence row.
- [ ] Every runbook step contains `Depends on`, `Input`, `Operation`,
      `Formula or logic`, `Parameters`, `Code entrypoint`, `Output`,
      `Validation`, `Failure action`, and `Handoff`.
- [ ] Every specification is self-contained and passes the execution-runbook
      standard without rereading the report.
- [ ] No unresolved placeholder, vague instruction, `TBD`, or `TODO` remains.
- [ ] Every No-Reread Checklist item is checked.
- [ ] `scripts/validate_spec.py` passed for every included figure and recorded
      the evidence and specification hashes in the manifest.
- [ ] Every data dependency is either explicitly defined or references an
      approved `SUB-*` replacement field.
- [ ] Every figure data contract records the replacement definition and known
      deviation for substituted data.
- [ ] Published values are confined to comparison and verification records and
      are never implementation inputs or data substitutes.
- [ ] Every panel has a mandatory chart type and data-encoding contract.
- [ ] The rendering contract requires a source-derived palette for every
      color-dependent encoding, or an evidenced `not_applicable` result.
- [ ] For raster sources, every color-dependent series or mark has a
      raster-sampled RGB/hex value with sampling method and tolerance.
- [ ] Plot text defaults to English, with every exception explicitly recorded.
- [ ] The rendering contract requires
      `matplotlib_notebook_default` for overall and panel titles and prohibits
      source-derived title font matching.
- [ ] The rendering contract requires centered overall and panel titles.
- [ ] The rendering contract uses adaptive canvas sizing and contains no fixed
      canvas or output dimensions.
- [ ] The rendering contract requires PNG and documents any additional format.
- [ ] Master dependencies and preflight revisions are recorded.
- [ ] The completion report identifies `/reprospec:plan` as the next stage.
