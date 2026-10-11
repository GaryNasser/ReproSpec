# Final Specification Check

## Identity

- Paper ID: `{{PAPER_ID}}`
- Master version: `{{MASTER_VERSION}}`
- Check date: `{{DATE}}`

## Data Integrity

- Sources inspected:
- Origin confirmed:
- Reliability confirmed:
- Definitions aligned:
- Definition substitutions:
- Unresolved definitions:
- Evidence packs frozen:
- Evidence hashes current:
- Specification hashes current:
- Self-contained runbooks:
- Report reread requirements:
- User confirmed:
- Blocking items:

## Completeness

- Master outline complete:
- Figure specifications complete:
- Runbook step completeness:
- No-Reread Checklist complete:
- Evidence map complete:
- Data plan complete:

## Consistency

- IDs consistent:
- Units consistent:
- Samples consistent:
- Formulas consistent:
- Sources consistent:

## Feasibility

- Available data:
- Acquirable data:
- Derived data:
- Approved fallbacks:
- Approved definition substitutions:
- Unavailable data:

## Traceability

| Figure | Master Dependencies | Covered | Missing |
| --- | --- | --- | --- |
|  |  |  |  |

For every substitution, record `SUB-*`, original `D-*`, replacement `D-*`, and
whether the replacement definition matches the master, figure, and integrity
records.

## Self-Contained Runbook Gate

For every included figure, record:

- evidence-pack path and current SHA-256;
- specification SHA-256 and successful Detail validation hash;
- number of contiguous `Sxx` steps;
- whether every step has `Depends on`, `Input`, `Operation`,
  `Formula or logic`, `Parameters`, `Code entrypoint`, `Output`, `Validation`,
  `Failure action`, and `Handoff`;
- unresolved placeholders, vague instructions, or missing `E###` references;
- `Self-contained execution: yes` and
  `Report reread for requirements: prohibited`;
- No-Reread Checklist result.

## Blocking Issues

| Issue | Affected Figures | Decision Required | Status |
| --- | --- | --- | --- |
|  |  |  |  |

## Lock Decision

- Ready to lock: `yes | no`
- Locked version:
- Notes:
