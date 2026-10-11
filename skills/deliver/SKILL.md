---
name: "deliver"
description: "Validate the completed reproduction, approved definition substitutions, mandatory source-derived palette, default Matplotlib Notebook title style, data-organization record, and stepwise audit, then assemble the final English delivery package. Use only after /reprospec:audit confirms every included figure has a complete source-to-image audit. Do not use for unresolved reproduction, repair, data organization, or audit work."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.9.0"
---

## User Input

Use invocation arguments to optionally select a paper ID. If no paper ID is
supplied, resolve the selected paper from the workspace manifest.

## Pre-Execution Checks

- All requirements established by `/reprospec:init` are satisfied before
  delivery. The detailed policy checks are listed below and are non-negotiable.
- If the Init policy is missing or relaxed, stop and return to
  `/reprospec:init`. If `time_range_policy.status` is not `confirmed` or the
  exact window is invalid, stop and return to `/reprospec:analyse`. Never
  continue by using a publication value or by bypassing the `supplement_data`
  or `skip` decision.
- The master specification is locked.
- `manifest.computation_policy` is `enforced`, with publication values limited
  to comparison and reproduction inputs limited to approved real data.
- `manifest.time_range_policy.status` is `confirmed` with `user_confirmed:
  true`, an allowed `selection`, exact ISO start and end dates, an explicit
  timezone, and a recorded basis.
- No unresolved `data_plan.decision_required` supplement-or-skip decision
  remains.
- `definition_policy.status` is `enforced`, its `decision_required` is false,
  and every `SUB-*` is complete, approved, and linked to a replacement `D-*`.
- The data-integrity gate is `complete`.
- `source_evidence.status` is `frozen`, and every included figure has one
  current evidence pack matching the manifest and `spec_lock.json`.
- Every included figure has a successful Detail validation record with the
  current `spec.md` hash, and `spec_lock.json` records the same specification
  and evidence hashes.
- Every included figure has a successful run-record validation with the current
  `logs/run_record.json` hash.
- Every included figure is `verified`, `partial`, or `blocked`.
- `partial` and `blocked` figures have `limitations.md`.
- No figure is `draft` or `stale`.
- `manifest.organization.status` is `complete`.
- The canonical datasets, inventory, catalog, organization record, and source
  disposition are present.
- The organization record confirms `audit_ready` and `reuse_ready`.
- `manifest.audit.status` is `complete`.
- Every included figure has an audit file under `audits/`.
- Every included figure has audit entry `computation_integrity: passed` and
  verified computation provenance from approved real data.
- Every included audit records `runbook_coverage: complete` and
  `report_reread_for_requirements: false`.
- Every included figure with rendered output has `palette_outcome` equal to
  `matched` or evidenced `not_applicable`.
- Every `matched` result or `verified` figure has either no rework challenge or
  a `verification.rework_challenge.status` of `resolved`.
- Every adjustment record is completed; residual risks remain explicit
  limitations.

## Goal

Assemble one deterministic English delivery package under
`figure-output/<paper-id>/`. Put every available rendered image in the flat
`figures/` gallery and keep the complete per-figure evidence in
`figure_details/`. Verified figures and documented partial or blocked figures
may be delivered; draft and stale figures may not.

## Execution Steps

1. Inspect the manifest and resolve the paper ID.
2. Reject delivery if any adjustment record is not completed.
3. Reject delivery if any definition-substitution decision is unresolved or any
   `SUB-*` is incomplete, unapproved, or missing from the data and figure
   lineage.
4. Reject delivery if any figure is `draft` or `stale`.
5. Reject delivery if a specification or evidence-pack hash differs from the
   Detail validation record or `spec_lock.json`.
6. Reject delivery if any runbook step is missing from the audit or if the
   report was reread to discover an execution requirement.
7. Reject delivery if organization is incomplete, the source disposition is
   pending, or an original-data move, overwrite, or deletion is not explicitly
   approved.
8. Reject delivery if the audit is incomplete or any included figure lacks a
   complete audit document.
9. Reject delivery if any figure uses a published or digitized expected value
   as data, a code constant, a missing-value fill, an interpolation, a plot
   coordinate, an annotation, a label, or an output value.
10. Run `scripts/assemble_delivery.py`.
11. Verify that `figure-output/<paper-id>/figures/` contains all rendered images
   as a flat, uniquely named gallery with no subdirectories.
12. Verify that `figure-output/<paper-id>/figure_details/` contains the complete
   per-figure evidence, alongside audits, organized data, data records, specs,
   comparison reports, limitations, logs, and the final reports.
13. Verify that `evidence/` contains every frozen pack and that
    `specs/spec_lock.json` records the delivered specification and evidence
    hashes.
14. Confirm that plotted titles, axes, ticks, legends, annotations, and panel
    labels use English unless the specification records an explicit exception.
15. For every included figure with rendered output, confirm that overall and
   panel titles use `matplotlib_notebook_default`, their run records identify
   `matplotlib.rcParamsDefault`, and no source-derived title font matching is
   present. A `blocked` figure with no output may record a blocked title-style
   outcome without fabricating one.
16. For every included figure with rendered output, confirm that the mandatory
    source-derived palette is `matched` or evidenced `not_applicable`. Reject a
    missing, `mismatched`, or `blocked` palette result.
17. Reject delivery when a `matched` result or `verified` figure has an
    unresolved AI rework challenge. Only `resolved` may support matched or
    verified status; `issued`, `answered`, or `blocked` remains explicitly
    `partial` or `blocked` with limitations.
18. Check that no secret-like files were copied and that raw data was included
    only when the organization record explicitly permits it.
19. Report final status counts, definition substitutions, palette results,
    computation-integrity status, organization readiness, and unresolved
    limitations.

## References

Read [references/delivery-rules.md](references/delivery-rules.md) for the final
layout, required evidence, and forbidden content.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence or copy the example fence markers.

Stage commands use the `/reprospec:*` slash-command form, including the
`Next` command.

```markdown
**ReproSpec 12/12 | DELIVER**

**Status:** `completed`
**Delivery Gate:** `PASS`

**Summary**

| Item | Result |
| --- | ---: |
| Verified | `<count>` |
| Partial | `<count>` |
| Blocked | `<count>` |
| Limitations | `<count>` |
| Complete audits | `<count>` |
| Complete runbook lineages | `<count>` |
| Report reread events | `0` |
| Specification and evidence lock | `PASS` |
| Approved definition substitutions | `<count>` |
| Palette matched or not applicable | `<count>` |
| Computation integrity | `PASS` |
| Canonical datasets | `<count>` |
| Source disposition | `<retain|move|delete|mixed>` |
| Flat gallery images | `<count>` |
| Audit-ready | `true` |
| Reuse-ready | `true` |
| Validation | `PASS` |

**Artifacts**

- `figure-output/<paper-id>/`
- `figure-output/<paper-id>/figures/`
- `figure-output/<paper-id>/figure_details/`
- `figure-output/<paper-id>/evidence/`
- `figure-output/<paper-id>/audits/`
- `figure-output/<paper-id>/data/organized/`
- `figure-output/<paper-id>/data/data_organization.md`
- `figure-output/<paper-id>/audit_report.md`
- `figure-output/<paper-id>/reproduction_report.md`

> **Next**
>
> None. The reproduction package is complete.
>
> **Reason:** All required delivery checks passed.
```

## Operating Constraints

- Comply with the requirements established by `/reprospec:init`. Never use a
  publication value as a reproduction input or bypass an unresolved
  `supplement_data` or `skip` decision. Deliver only the exact user-confirmed
  reproduction time range.
- Use `figure-output`, never a localized output directory name.
- Keep `figures/` flat. Every rendered image must be copied there with a unique
  `<figure-id>__<relative-name>` filename, without nested subdirectories.
- Keep complete per-figure evidence under `figure_details/`.
- Plot titles, axis labels, ticks, legends, annotations, and panel labels must
  be English by default unless the specification records an explicit exception.
- Overall and panel titles must use `matplotlib_notebook_default`, resolved
  from `matplotlib.rcParamsDefault`, centered, and free of source-derived font
  matching.
- Every rendered figure must satisfy the mandatory source-derived palette
  contract. Missing, `mismatched`, or `blocked` palettes cannot be delivered.
- Do not deliver when any specification or evidence hash differs from
  `spec_lock.json` or the Detail validation record.
- Do not deliver a figure whose audit lacks complete `Sxx` runbook coverage or
  records a report reread requirement.
- An unresolved `issued` or `answered` AI rework challenge cannot be delivered
  as `matched` or `verified`; it remains only on an explicit `partial` or
  `blocked` figure with limitations.
- Do not deliver `draft` or `stale` figures.
- Do not deliver without one complete audit Markdown file per included figure.
- Do not deliver while any required definition is unresolved or any substitute
  is unapproved, incomplete, or inconsistent across the manifest, master,
  figure specification, integrity record, and audit.
- Do not deliver when any figure or adjustment depends on a copied, hard-coded,
  digitized, interpolated, or backfilled published value. Publication values
  may appear only in comparison evidence.
- Do not deliver a pending source disposition.
- Do not deliver an unapproved original-data move, overwrite, or deletion.
- Do not copy raw data unless the organization record explicitly
  permits delivery inclusion.
- Do not hide partial or blocked results.
- Do not copy credentials, `.env` files, caches, or temporary files.
- Generated delivery documentation must be English.

## Done When

- [ ] The requirements established by `/reprospec:init` were verified and
      satisfied before this stage completed.
- [ ] The exact user-confirmed reproduction time range was preserved.
- [ ] Delivery was rejected if any figure is `draft` or `stale`.
- [ ] The audit gate is `complete` and every included figure has an audit file.
- [ ] Every required non-explicit definition has an approved, complete,
      consistently recorded `SUB-*`.
- [ ] Every included figure has verified computation provenance from approved
      real data and `computation_integrity: passed`.
- [ ] Every included figure has current, matching specification and evidence
      hashes in the manifest, Detail validation, and `spec_lock.json`.
- [ ] Every audit covers the complete locked runbook and confirms that the
      report was not reread for requirements.
- [ ] The organization gate and source disposition are complete.
- [ ] Canonical data and organization records are present in the delivery
      package.
- [ ] `figure-output/<paper-id>/figures/` is a flat gallery containing every
      available rendered image with a unique filename.
- [ ] `figure-output/<paper-id>/figure_details/` contains complete per-figure
      evidence.
- [ ] `figure-output/<paper-id>/evidence/` contains the frozen source-evidence
      packs and `specs/spec_lock.json` records their hashes.
- [ ] Plotted text is English unless an explicit exception is recorded.
- [ ] Every rendered figure uses the recorded
      `matplotlib_notebook_default` title policy without source font matching.
- [ ] Every rendered figure has `palette_outcome: matched` or evidenced
      `not_applicable`.
- [ ] Every `matched` result or `verified` figure has no unresolved AI rework
      challenge.
- [ ] `figure-output/<paper-id>/` contains the required artifacts.
- [ ] The data-integrity report and manifest are present.
- [ ] Partial and blocked results remain explicit.
- [ ] No secret-like or temporary file was copied.
- [ ] The final status counts and limitations are reported.
