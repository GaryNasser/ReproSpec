---
name: "audit"
description: "Create one stepwise A-to-B-to-C traceability document per reproduced figure and verify every source, approved definition substitution, processing, rendering, and export operation needed to build the image, including palette and default title style. Use only after /reprospec:organize confirms canonical datasets and source disposition, and before /reprospec:deliver. Do not use for repair, data organization, or final packaging."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.8.0"
---

## User Input

Use invocation arguments to select specific final figure IDs. If no targets are
supplied, audit every included figure whose status is `verified`, `partial`, or
`blocked`.

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
- No included figure is `draft` or `stale`.
- Every target figure has a locked specification, code, logs, and either final
  output and comparison evidence or explicit limitation evidence.
- `spec_lock.json` records the current `spec.md` and frozen evidence-pack
  SHA-256 for every target figure.
- Each target figure has `run_validation.status: passed` and a matching
  `logs/run_record.json` hash.
- Every target run record identifies the locked hashes, contains one completed
  entry per `Sxx` step, sets `report_reread_for_requirements` to `false`, and
  has no `reread_events`.
- `partial` and `blocked` figures have `limitations.md`.
- The data-integrity gate is `complete`.
- `manifest.organization.status` is `complete`.
- Canonical datasets, their source maps, the inventory, catalog, organization
  record, and source disposition are available.
- Previous rework rounds, adjustment records, and accepted limitations are
  available.

## Goal

Create one traceability document for every included figure at
`work/<paper-id>/audits/<figure-id>.md`. Reconstruct the complete lineage from
data source through every processing and reproduction operation to the final
image using sequential uppercase step labels `A`, `B`, `C`, and so on.

The acceptance test is: a reader unfamiliar with the project can move through
the document step by step and know exactly what entered, what operation
occurred, which parameters and code were used, what output was produced, what
evidence proves it, and how that output leads to the final figure.

## Execution Steps

1. Resolve target figure IDs or select every final included figure.
2. Collect the master specification, figure specification, data-integrity
   records, frozen evidence pack, `spec_lock.json`, confirmed reproduction time
   range, raw and derived data, source code, commands, run records, logs,
   outputs, comparison report, limitations, rework history, adjustment
   history, and approved definition substitutions.
3. Reconstruct the actual lineage for each figure. Cover source acquisition,
   definition selection or approved substitution, raw intake, extraction, OCR,
   parsing, cleaning, normalization,
   canonicalization, joins, filtering, aggregation, unit conversion,
   imputation, derived calculations, statistical processing, panel
   construction, figure sizing, `matplotlib_notebook_default` title resolution
   and application, palette extraction and mapping, rendering options actually
   applied, export, verification, rework, and adjustment whenever those
   operations actually occurred. Record the resolved default title family,
   point size, and weight. Document the exact or sampled palette source, mapping
   to marks, tolerance, and verification outcome. Do not require or reconstruct
   source font matching or other fine visual imitation that was not performed.
4. Assign one sequential letter to each distinct operation. Do not collapse
   unrelated transformations into a vague step such as "process data".
5. Create `work/<paper-id>/audits/<figure-id>.md` from
   `assets/figure-audit-template.md`.
6. For every lettered step, record the input or source, exact operation,
   parameters, code or command, output, evidence path or hash, validation, and
   handoff to the next step.
7. Link each step to its specification step and master IDs when available.
   Distinguish source data from derived data. Verify that no published or
   digitized expected value was copied, hard-coded, backfilled, interpolated,
   or injected into data, code, axes, annotations, labels, or outputs. Require
   `verification.computation_provenance` to be
   `computed_from_approved_real_data`; otherwise mark the figure audit
   `blocked`.
   When a substitution is used, prove that the audited lineage uses the
   approved replacement `D-*` and `SUB-*`, not an inferred interpretation of
   the original term.
   Verify that every `Sxx` specification step has one corresponding run-record
   entry and that the specification, evidence-pack, input, and output hashes
   match `spec_lock.json` and the run record. Confirm
   `report_reread_for_requirements: false`, an empty `reread_events` list, and
   no requirement discovered by reopening the report.
8. Apply the reader test from the Goal to every step. If any required element
   is missing, record the gap explicitly and mark that figure audit `blocked`.
   Do not infer, recreate, or overfit an explanation.
9. Write `work/<paper-id>/audit_report.md` from
   `assets/audit-report-template.md` with per-figure status, step counts,
   computation-integrity results, lineage coverage, and unresolved gaps.
10. Update `audit.status`, `audit.updated_at`, and `audit.figures` in the
    manifest. Store each figure as
    `{"status": "complete|blocked", "path": "audits/<figure-id>.md",
    "computation_integrity": "passed|blocked",
    "runbook_coverage": "complete|blocked",
    "report_reread_for_requirements": false}`. Set
    `computation_integrity` to `passed` only when no copied, hard-coded,
    digitized, interpolated, or backfilled published value affects the figure.
    Set the overall status to `complete` only when every included figure has a
    complete audit file, `computation_integrity` is `passed`, and no
    undisclosed lineage gap remains. Set
    `workflow.active_stage` to `audit`; set `workflow.next_stage` to
    `deliver` only when the audit is complete.
11. If any audit is blocked, keep the workflow at `audit`, leave the next stage
    unavailable, and report the exact missing evidence and affected figures.

## References

Read [references/audit-rules.md](references/audit-rules.md) for lineage
coverage, step quality, gap handling, and the output contract.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 11/12 | AUDIT**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Figures audited | `<count>` |
| Complete audits | `<count>` |
| Blocked audits | `<count>` |
| Definition substitutions verified | `<count>` |
| Complete runbook lineages | `<count>` |
| Report reread events | `0` |
| Steps documented | `<count>` |
| Critical gaps | `<count>` |

**Artifacts**

- `work/<paper-id>/audits/`
- `work/<paper-id>/audit_report.md`
- `work/<paper-id>/reproduction_manifest.json`

> **Next**
>
> `/reprospec:deliver`
>
> **Reason:** Every included figure has a complete source-to-image traceability audit.
```

If any audit is blocked, use `Status: blocked`, report the missing evidence and
affected steps, and do not identify `/reprospec:deliver` as the next action.

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Audit the exact user-confirmed
  reproduction time range.
- Create exactly one audit Markdown file per included figure.
- Use sequential uppercase labels `A`, `B`, `C`, and so on. Do not skip,
  duplicate, or replace them with opaque phase names.
- Do not use vague steps such as "clean the data" or "generate the chart".
- Every step must identify its input, operation, parameters, code or command,
  output, evidence, validation, and next handoff.
- Do not claim a source, transformation, or parameter that cannot be supported
  by an artifact, log, command, or specification.
- Do not hide missing lineage or use an unjustified adjustment to make the
  sequence appear complete.
- For every non-explicit paper definition, require the approved `SUB-*` and
  replacement `D-*` in the lineage. Mark the audit `blocked` if the figure
  depends on an inferred original definition or an unapproved substitute.
- Do not pass a figure whose result depends on a copied or hard-coded published
  value. Record the exact value location and mark the audit `blocked`.
- Do not pass an audit whose run record has a changed specification or evidence
  hash, a missing `Sxx` step, or a report reread event.
- Do not write `computation_integrity: passed` unless every numeric value and
  coordinate in the figure traces to approved real data and traceable code.
- Source-derived palette colors are rendering metadata, not quantitative data.
  Their use as style constants does not violate computation integrity.
- Confirm that the audit records the title-style policy, the
  `matplotlib.rcParamsDefault` source, and the resolved overall and panel title
  properties actually applied. A source-derived or undocumented title font is
  an audit gap.
- Confirm that the audit records palette extraction, extracted or exact colors,
  mark mapping, tolerance, and the final `palette_outcome`. A missing or
  undocumented palette step is an audit gap whenever color encodes data.
- Palette colors are rendering metadata. Document that they were not used as
  numeric data, coordinates, annotations, labels, or output values.
- Preserve accepted `partial` or `blocked` limitations explicitly.
- Trace approved original-data removals through the inventory hashes,
  tombstones, organization record, canonical data, and code. Do not treat an
  approved, documented removal as an audit gap.
- Never include credentials or secret values.
- Generated audit documents must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Every included figure has one `audits/<figure-id>.md`.
- [ ] Every audit uses sequential `A -> B -> C` steps.
- [ ] Every audit maps the actual execution to every locked `Sxx` step and
      confirms the specification and evidence hashes.
- [ ] No report reread event or missing runbook step is present.
- [ ] Data source, raw intake, processing, rendering, and export are covered.
- [ ] Every approved definition substitution is traced from the original term
      through the replacement field and into the figure, or the audit is
      blocked.
- [ ] The `matplotlib_notebook_default` title policy and its resolved
      properties are documented without source-font inference.
- [ ] The mandatory source-derived palette lineage and outcome are documented
      without using palette colors as data.
- [ ] Every step passes the reader test and cites real evidence.
- [ ] Every numeric result traces to approved real data rather than a copied
      published value.
- [ ] Every complete audit entry records `computation_integrity: passed`.
- [ ] Missing evidence is disclosed without inference or overfitting.
- [ ] The manifest audit status and per-figure audit paths are accurate.
- [ ] `audit_report.md` and the manifest reflect the true audit status.
- [ ] A completed audit identifies `/reprospec:deliver` as the next stage.
