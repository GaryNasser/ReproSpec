# Master Data Specification

## Identity

- Paper ID: `{{PAPER_ID}}`
- Title: `{{PAPER_TITLE}}`
- Source: `{{SOURCE}}`
- Source hash:
- Full-document scan date:
- Master specification version: `1.0.0`
- Status: `draft`

## Source Snapshot

Record the selected paper, appendices, supplement, replication package, and
user-provided data. Include immutable paths and hashes.

## Research Scope

- Research question:
- Sample universe:
- Geography:
- Start date:
- End date:
- Frequency:
- Cross-section:
- Entity mapping:

## Reproduction Time Range

- Mode selected at Init: `{{TIME_RANGE_SELECTION}}`
- Mode confirmed by user at Init: `yes`
- Init confirmation time: `{{TIME_RANGE_CONFIRMED_AT}}`
- Paper or report start date:
- Paper or report end date:
- Confirmed start date: `pending until Analyse`
- Confirmed end date: `pending until Analyse`
- Timezone: `{{TIME_RANGE_TIMEZONE}}`
- Init selection basis: `{{TIME_RANGE_BASIS}}`
- Final window confirmed by user at Analyse: `no`
- Source-specific availability limit:

## Figure Inventory

### Included Data-Driven Figures

| Figure | Source | Panels | Required Data | Master Dependencies | Evidence Pack | Status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |

### Excluded Schematic Figures

| Figure | Source | Category | Exclusion Reason |
| --- | --- | --- | --- |
|  |  | `excluded_schematic` |  |

## Stable Data Contract

| ID | Field | Definition | Definition Status | Source | Integrity ID | Unit | Frequency | Transformation | Substitution ID | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 |  |  | `explicit / missing / underspecified / conflicting` |  |  |  |  |  |  |  |

## Definition Substitutions

Record one `SUB-*` row for every approved replacement of a required item whose
source definition is missing, ambiguous, or conflicting. The replacement field
must use a separate `D-*` row and must be the field referenced by affected
figure specifications.

| Substitution ID | Original Master ID | Original Term | Source Status | Source Location | Source Evidence | Replacement Master ID | Replacement Term | Explicit Operational Definition | Functional Rationale | Source | Unit | Period and Frequency | Universe | Transformation | Known Deviation | Limitations | Affected Figures | Decision ID | User Approved | Approved At | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SUB-001 | D-001 |  | `missing / underspecified / conflicting` |  |  | D-002 |  |  |  |  |  |  |  |  |  |  |  | Q-001 | `no` |  | `draft` |

## Data Integrity

| Data ID | Path | Origin | Reliability | Definition Alignment | Quality Risks | User Confirmed |
| --- | --- | --- | --- | --- | --- | --- |
| DATA-001 |  |  |  |  |  | `no` |

## Processing Rules

| ID | Rule | Inputs | Formula or Logic | Output | Source Reference |
| --- | --- | --- | --- | --- | --- |
| S-001 |  |  |  |  |  |
| T-001 |  |  |  |  |  |

## Computation Integrity

- Published values are comparison targets only.
- No published number may be used as a data source, implementation input,
  hard-coded constant, missing-value fill, plot coordinate, annotation, label,
  or fabricated output value.
- Every reproduced value must be computed from approved real data through
  traceable code.

## Missing Data and Revisions

- Missing-value policy:
- Outlier policy:
- Winsorization:
- Data vintage:
- Provider revision policy:
- Currency conversion:
- Price and return conventions:

## Source Priority

| Priority | Source | Access | Version Control | Status |
| --- | --- | --- | --- | --- |
| 1 | User-provided raw data | Local | Hash |  |

## User-Confirmed Decisions

| ID | Decision | Source Location | User Answer | Date | Affected IDs | Affected Figures |
| --- | --- | --- | --- | --- | --- | --- |
| Q-001 |  |  |  |  |  |  |

## Version History

| Version | Date | Changed IDs | Reason | Affected Figures |
| --- | --- | --- | --- | --- |
| 1.0.0 | {{DATE}} | Initial | Initial outline |  |

## Known Limitations

| ID | Limitation | Impact | Mitigation | Status |
| --- | --- | --- | --- | --- |
| L-001 |  |  |  |  |
