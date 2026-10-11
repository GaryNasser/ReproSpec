# Reproduction Report: {{PAPER_ID}}

## Identity

- Title: `{{PAPER_TITLE}}`
- Source: `{{SOURCE}}`
- Source hash: `{{SOURCE_HASH}}`
- Master specification version: `{{MASTER_VERSION}}`
- Delivery date: `{{DELIVERED_AT}}`

## Data Integrity

| Metric | Count |
| --- | --- |
| Inspected data items | {{INTEGRITY_ITEMS}} |
| Origin confirmed | {{INTEGRITY_ORIGIN_CONFIRMED}} |
| Reliability confirmed | {{INTEGRITY_RELIABILITY_CONFIRMED}} |
| Definitions aligned | {{INTEGRITY_ALIGNED}} |
| User confirmed | {{INTEGRITY_USER_CONFIRMED}} |

## Definition Substitutions

| Metric | Result |
| --- | --- |
| Approved substitutions | {{DEFINITION_SUBSTITUTION_COUNT}} |
| Substitution IDs | `{{DEFINITION_SUBSTITUTION_IDS}}` |
| Replacement master IDs | `{{DEFINITION_REPLACEMENT_MASTER_IDS}}` |

Every non-explicit paper definition is replaced by a source-backed,
user-approved `SUB-*` with an explicit operational definition. Substitutes
preserve the analytical role and are never selected or tuned to match
published values.

## Traceability Audit

| Metric | Count |
| --- | ---: |
| Audited figures | {{AUDITED_FIGURES}} |
| Complete audits | {{AUDIT_COMPLETE}} |
| Blocked audits | {{AUDIT_BLOCKED}} |

## Computation Integrity

| Metric | Result |
| --- | ---: |
| Status | `{{COMPUTATION_INTEGRITY_STATUS}}` |
| Figures checked | {{COMPUTATION_FIGURES_CHECKED}} |
| Published values used as inputs | {{COMPUTATION_VIOLATIONS}} |

Publication values are comparison targets only. All reproduced values must be
computed from approved real data through traceable code.

## Evidence and Runbook Integrity

| Metric | Result |
| --- | ---: |
| Frozen evidence packs | {{EVIDENCE_PACK_COUNT}} |
| Specification and evidence lock | `{{SPEC_LOCK_STATUS}}` |
| Complete runbook records | {{RUNBOOK_COMPLETE_COUNT}} |
| Missing runbook steps | {{RUNBOOK_MISSING_COUNT}} |
| Report reread events | {{REPORT_REREAD_EVENTS}} |

Each included figure must have a frozen evidence pack, a validated
self-contained `spec.md`, and one completed execution entry for every locked
`Sxx` step. The report or paper must not be reopened to discover requirements.

## Reproduction Time Range

| Metric | Result |
| --- | --- |
| Selection | `{{TIME_RANGE_SELECTION}}` |
| Start date | `{{TIME_RANGE_START}}` |
| End date | `{{TIME_RANGE_END}}` |
| Timezone | `{{TIME_RANGE_TIMEZONE}}` |

## Data Organization

| Metric | Result |
| --- | ---: |
| Status | `{{DATA_ORGANIZATION_STATUS}}` |
| Canonical datasets | {{ORGANIZATION_DATASETS}} |
| Canonical formats | `{{ORGANIZATION_CANONICAL_FORMATS_TEXT}}` |
| Canonical checkpoint | `{{ORGANIZATION_CANONICAL_CHECKPOINT_TEXT}}` |
| Raw sources consolidated | {{ORGANIZATION_SOURCES}} |
| Source disposition | `{{DATA_DISPOSITION}}` |
| Audit-ready | `{{ORGANIZATION_AUDIT_READY}}` |
| Reuse-ready | `{{ORGANIZATION_REUSE_READY}}` |

## Outcome

| Status | Count |
| --- | --- |
| Verified |  |
| Partial |  |
| Blocked |  |
| Excluded schematics |  |
| Stale |  |
| Draft |  |

## Figure Summary

| Figure | Status | Data Result | Implementation Result | Attribution | Limitations |
| --- | --- | --- | --- | --- | --- |
{{FIGURE_SUMMARY_ROWS}}

## Figure Gallery

- Flat review gallery: `figures/`
- Flat images: {{FLAT_FIGURE_COUNT}}
- Per-figure evidence: `figure_details/`
- Manual adjustment log: `logs/adjustment_log.md`
- Title style: `matplotlib_notebook_default` from `matplotlib.rcParamsDefault`
  for overall and panel titles; source font matching is disabled.
- Title alignment: Centered for overall and panel titles.
- Palette: Source-derived palette matching is required; every rendered figure
  must be `matched` or evidenced `not_applicable`.
- Plot text language: English by default; exceptions require an explicit
  specification record.

## Palette Contract

| Metric | Result |
| --- | ---: |
| Status | `{{PALETTE_STATUS}}` |
| Rendered figures checked | {{PALETTE_RENDERED_COUNT}} |
| Matched or not applicable | {{PALETTE_PASS_COUNT}} |
| Palette failures | {{PALETTE_FAILURE_COUNT}} |

## Data Sources

| Source | Version or Vintage | Access | Reproducible | Notes |
| --- | --- | --- | --- | --- |
{{DATA_SOURCE_ROWS}}

## Master Specification History

| Version | Changed IDs | Reason | Re-run Figures |
| --- | --- | --- | --- |
{{MASTER_HISTORY_ROWS}}

## Reproduction Commands

{{REPRODUCTION_COMMANDS}}

## Overall Limitations

{{OVERALL_LIMITATIONS}}
