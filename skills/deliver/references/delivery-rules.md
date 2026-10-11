# Delivery Rules

## Purpose

Define the required state, final layout, evidence, forbidden content, and
language rules for the delivery package.

## Inputs

- the locked master specification;
- the completed data-integrity report;
- the canonical data and completed data-organization record;
- the current reproduction manifest;
- verified, partial, or blocked figure directories.

## Required State

Delivery requires:

- a locked master specification;
- `manifest.computation_policy.status: enforced`;
- a user-confirmed `time_range_policy` with exact start and end dates and
  timezone;
- no unresolved `data_plan.supplement_data` or `skip` decision;
- no unresolved definition-substitution decision and no incomplete,
  unapproved, or inconsistent `SUB-*`;
- `source_evidence.status` is `frozen`, and every included figure has a
  current evidence pack matching its manifest and lock hashes;
- every included figure has a successful Detail validation record and a
  current `spec_lock.json` specification hash;
- every included figure has a successful run-record validation with an
  unchanged run-record hash, `report_reread_for_requirements: false`, and no
  reread events;
- every audit records `runbook_coverage: complete` and
  `report_reread_for_requirements: false`;
- a `complete` data-integrity gate;
- a `complete` data-organization record;
- canonical datasets plus inventory, catalog, record, and report;
- organization-record confirmation that `audit_ready` and `reuse_ready` are
  true;
- a `complete` traceability audit;
- one complete audit document per included figure;
- `computation_integrity: passed` for every included audit entry;
- verified `matplotlib_notebook_default` title policy for every included
  figure with rendered output, with no source-derived title font matching;
- verified `palette_outcome: matched` or evidenced `not_applicable` for every
  included figure with rendered output;
- no unresolved `draft`, `partial`, or `blocked` adjustment record;
- no `draft` figures;
- no `stale` figures;
- every figure marked `verified`, `partial`, or `blocked`;
- limitations for every `partial` or `blocked` figure.

## Final Layout

```text
figure-output/<paper-id>/
|-- figures/                 # Flat gallery: all rendered images
|-- figure_details/          # Full per-figure evidence
|-- evidence/                # Frozen per-figure source-evidence packs
|-- audits/
|-- data/
|   |-- organized/
|   |-- data_inventory.csv
|   |-- data_catalog.csv
|   |-- data_organization.json
|   |-- data_organization.md
|   |-- data_gaps.csv
|   |-- data_integrity.json
|   `-- data_integrity.md
|-- specs/
|   |-- master_spec.md
|   |-- spec_lock.json
|   `-- <figure-id>/spec.md
|-- comparison_reports/
|-- limitations/
|-- logs/
|-- audit_report.md
|-- reproduction_report.md
`-- delivery_manifest.json
```

## Required Figure Evidence

Each verified figure includes:

- rendered output;
- specification;
- frozen source-evidence pack;
- code and environment metadata;
- `logs/run_record.json` with one completed entry per locked `Sxx` step and no
  report reread events;
- input and derived data contract;
- logs;
- `logs/adjustment_log.md`;
- pixel evidence when used;
- comparison report;
- palette extraction and mark-mapping evidence;
- run record with the resolved overall and panel title style;
- limitations when applicable.

Each included figure also has one `audits/<figure-id>.md` document outside the
rendered image output.

The `figures/` directory is the flat review gallery. It contains every
available rendered image, including images from partial or blocked figures
when present. Files use `<figure-id>__<relative-name>` and must not create
subdirectories. The `figure_details/` directory keeps each complete figure
directory, including code, logs, specification, comparison evidence, and
limitations.

The canonical datasets under `data/organized/` are the default data payload.
Include `data/raw/` only when the organization record explicitly sets
`include_raw_in_delivery` to true.

## Self-Contained Runbook Integrity

Delivery requires the locked `spec.md`, frozen evidence pack, and audit lineage
to agree on the specification and evidence SHA-256. The run record and audit
must cover every `Sxx` step, all required validations must pass, and
`report_reread_for_requirements` must be `false` with no `reread_events`.
Reject delivery when a figure was produced by reopening the report to discover
a requirement, when a runbook step is missing, or when the locked hash no
longer matches.

## Computation Integrity

Publication numbers are comparison targets only. Delivery is invalid when an
included figure or adjustment uses a paper or report value as source data,
implementation input, hard-coded constant, missing-value fill, interpolation,
digitized coordinate, annotation, label, or output value.

Every reproduced value and coordinate must derive from approved real data
through traceable code. Require verified
`verification.computation_provenance: computed_from_approved_real_data` and an
audit entry with `computation_integrity: passed` for every included figure.
Missing provenance, copied values, or unsupported computation must block
delivery. If required real data is unavailable, deliver a documented partial or
blocked result rather than reconstructing it from the publication.

## Definition Substitution Integrity

Every required definition must be explicit in the source or replaced by an
approved `SUB-*`. Delivery requires the substitution to contain the original
`D-*`, replacement `D-*`, explicit operational definition, source, universe,
period and frequency, unit, transformation, functional rationale, known
deviation, affected figures, linked decision, approval timestamp, and
user approval.

The same replacement definition must appear in the manifest, master
specification, figure data contract, data-integrity item, run record, and audit.
Delivery is invalid if a figure depends on an inferred original definition, an
unapproved substitute, or a replacement definition that changed after locking.
The substitute must preserve the analytical role and must not have been chosen
or tuned to match published values.

## Reproduction Time Range

Delivery requires the exact user-confirmed time range. Validate that
`time_range_policy.status` is `confirmed`, `user_confirmed` is true, the
selection is `publication_period` or `through_today`, and the start date, end
date, timezone, and basis are recorded. Never deliver a package whose figures
silently mix or substitute different periods.

## Forbidden Content

Do not copy:

- credentials;
- `.env` files;
- token stores;
- caches;
- temporary files;
- local editor configuration;
- raw private data unless the user explicitly requested delivery inclusion.
- data, code, coordinates, annotations, labels, or outputs that depend on a
  copied, hard-coded, digitized, interpolated, or backfilled published value.

## Language

All generated paths, documents, schemas, and code comments are English.
Plotted titles, axes, ticks, legends, annotations, and panel labels are English
by default. A different plot-text language requires an explicit user request or
documented specification exception.
Terminal responses follow the user's language.

## Default Title Style

Overall and panel titles use `matplotlib_notebook_default`. Their family, size,
and weight resolve from `matplotlib.rcParamsDefault` and are pinned after any
style or theme setup. For a figure with rendered output, the run record and
comparison report must record the resolved values and set source-derived title
font matching to false. A title font that differs from the published figure is
acceptable; a missing policy or a source-matched title font blocks delivery. A
`blocked` figure with no rendered output may record a blocked title-style
outcome without fabricating one.

## Palette Contract

Every rendered figure must satisfy the mandatory source-derived palette
contract. The specification, run record, comparison report, and audit must
identify exact vector colors or raster sampling regions, extraction and
normalization method, color-space conversion, extracted colors, mark mapping,
acceptance tolerance, final `palette_outcome`, and non-empty
`verification.palette_evidence`. The outcome must be `matched` or evidenced
`not_applicable`. A missing, `mismatched`, or `blocked` palette result blocks
delivery.

Palette colors are rendering metadata and must not be used as numeric data,
coordinates, annotations, labels, or output values.

## Rework Challenge Contract

A figure verification record may include `verification.rework_challenge` when
`/reprospec:verify` issued an AI repair challenge. Its status must be `issued`,
`answered`, `resolved`, or `blocked`. A `matched` result or `verified` figure
status requires `resolved`. An unresolved `issued` or `answered` challenge may
remain only on an explicit `partial` or `blocked` figure with limitations. Do
not deliver an unresolved challenge as verified or matched.

## Output Contract

Produce `figure-output/<paper-id>/` with the flat `figures/` gallery, complete
`figure_details/` evidence, audits, canonical data, data records, specs,
comparison reports, limitations, logs, the data-integrity report, the audit
report, the reproduction report, and the delivery manifest.

## Failure Handling

Reject delivery when any figure is `draft` or `stale`, when a partial or blocked
figure lacks `limitations.md`, when the audit is incomplete, when an included
figure lacks its audit document, when the source disposition is pending, when
an original-data move, overwrite, or deletion lacks explicit approval, when
raw-data inclusion conflicts with the organization record, when a verified or
partial figure has no rendered image, or when secret-like content would be
copied. Also reject delivery when any included figure lacks
`computation_integrity: passed`, lacks verified computation provenance from
approved real data, or depends on a published expected value. Reject delivery
when the reproduction time-range status is not `confirmed`, or its exact
window is missing, contradictory, or unsupported. Reject delivery when an
included figure with rendered output lacks a verified
`matplotlib_notebook_default` title style or uses a source-derived title font.
Also reject delivery when an included figure with rendered output lacks a
`matched` or evidenced `not_applicable` palette outcome.
Reject delivery when a `matched` result or `verified` figure has an unresolved
AI rework challenge.
Reject delivery when a non-explicit definition lacks an approved `SUB-*`, when
any substitution record is incomplete, or when its replacement definition does
not match the locked specification and reproduced lineage.
Reject delivery when a specification or evidence hash differs from
`spec_lock.json`, when a Detail validation record is missing or stale, when a
runbook step is absent from the audit, or when the report was reread for
requirements.
