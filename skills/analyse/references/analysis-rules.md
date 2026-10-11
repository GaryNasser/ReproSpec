# Analysis Rules

## Purpose

Define the final completeness, consistency, feasibility, and traceability gate
before reproduction.

## Inputs

- the master and figure specifications;
- the frozen per-figure source-evidence packs and their recorded hashes;
- the Init-established `time_range_policy`;
- the data plan and user decisions;
- the data-integrity report and source evidence;
- any remaining blocking issues.

## Data Integrity Gate

Before the final check, confirm for every user-provided dataset:

- the file still matches the inspected SHA-256; `lock_spec.py` recomputes it
  immediately before locking;
- origin and acquisition evidence are confirmed;
- reliability is confirmed as `high`, `medium`, or `low`;
- the user has been told about every known quality risk;
- fields, keys, units, sample, period, frequency, coverage, missing values,
  outliers, joins, aggregations, and transformations are exactly `aligned`;
- `definition_basis` is `source_explicit` or `approved_substitution`;
- every `approved_substitution` points to an approved `SUB-*` whose replacement
  `D-*` and explicit operational definition are identical in the manifest,
  master specification, figure specification, and integrity record;
- the user has confirmed the final definition.

Set `data_integrity.json.status` to `complete` only when all conditions pass.
Any mismatch or unknown value blocks locking and reproduction.

An undefined paper term is not a valid alignment basis. Require an approved
`SUB-*` with an explicit replacement definition and source-backed provenance.
Confirm that the substitute preserves the analytical role, states its known
deviation, and was not selected or tuned to match published values.

## Source Evidence Freeze Gate

Before locking, require `source_evidence.status: frozen`. For every included
figure:

- recompute the evidence-pack SHA-256 and compare it with
  `source_evidence.items`;
- compare the manifest figure record with the same evidence path and hash;
- compare the hash recorded in `spec.md` with the frozen pack;
- compare the current `spec.md` hash with the successful Detail validation
  record;
- require `Self-contained execution: yes` and
  `Report reread for requirements: prohibited`;
- require a valid `E###` evidence map, contiguous runbook steps, every required
  `Sxx` field, no unresolved placeholder or vague instruction, and a fully
  checked No-Reread Checklist.

Any mismatch invalidates the figure specification. Return to
`/reprospec:detail` when the specification or its validation record is stale,
or to `/reprospec:outline` when the evidence pack itself is missing, changed, or
incomplete. Reproduction cannot begin from a spec that would require the model
to reopen the report.

## Reproduction Time Range Gate

Before locking, preserve the mode already confirmed at Init unless the user
explicitly changes it:

- `publication_period`: use the original paper or report period;
- `through_today`: extend through the confirmed current date.

Do not present the mode question again when `selection` is already
`publication_period` or `through_today`. Resolve and present the exact ISO
`start_date` and `end_date`, timezone, and source or calculation basis, then
obtain final user confirmation. Record `status: confirmed`,
`user_confirmed: true`, and the final `confirmed_at` only after that
confirmation. For `through_today`, record the latest available observation per
source when it differs from the calendar date.

A time range whose status is not `confirmed`, or whose exact window is missing,
contradictory, or unsupported, blocks locking and reproduction. Confirm whether
the selected window changes data coverage, definitions, sample size, or figure
values. Never silently choose a window or substitute one for the other.

## Final Check

Check these properties:

| Property | Requirement |
| --- | --- |
| Complete | All required fields, rules, figures, and sources are specified |
| Consistent | IDs, units, samples, formulas, and sources do not conflict |
| Feasible | Data is present, obtainable, derivable, or explicitly limited |
| Traceable | Every figure requirement maps to a master ID |
| Computed | Every reproduced value derives from approved real data, not published expected values |
| Definitions | Every required definition is explicit or replaced by an approved, complete `SUB-*` |
| Evidence | Every included figure has one unchanged frozen evidence pack |
| Self-contained | Every figure has a complete runbook, `E###` traceability, no placeholders, and a checked No-Reread Checklist |
| Locked hashes | Specification and evidence hashes match the Detail validation and freeze records |
| Window | The user-confirmed reproduction time range and exact dates are recorded |

## Blocking Rules

Do not lock the specification when:

- a figure has no detailed specification;
- an evidence pack is missing, draft, unfrozen, or changed after freezing;
- a figure specification or evidence hash does not match the Detail validation
  record;
- a figure runbook is incomplete, contains placeholders or vague instructions,
  or cannot be executed without rereading the report;
- a required field has no source or fallback;
- a formula, unit, period, or universe conflicts;
- a required definition is `missing`, `underspecified`, `conflicting`, or
  `unknown`;
- a `SUB-*` is unapproved, incomplete, lacks provenance, or does not match the
  replacement field used by the figure and integrity records;
- `time_range_policy.status` is not `confirmed`, or its exact dates conflict
  with the required data coverage;
- a specification uses a paper or report number as data, an implementation
  input, a hard-coded constant, a missing-value fill, a plot coordinate, an
  annotation, a label, or an output value;
- a material user decision is unresolved;
- a figure cannot be traced to the master outline.

Ask one question at a time for blocking issues.

## Lock Artifact

`scripts/lock_spec.py` writes `spec_lock.json` and updates the manifest.

The lock records:

- paper ID;
- master version;
- timestamp;
- figure count;
- data-plan status.
- confirmed reproduction time range.
- definition-substitution count, IDs, and replacement master IDs.
- per-figure specification path and SHA-256.
- per-figure frozen evidence path and SHA-256.
- runbook step count per figure.

Locking does not make the specification immutable. A later rework round may
change it through the rework workflow and must create a new version.

## Output Contract

Write `spec_lock.json`, record the per-figure specification and evidence hashes
in the manifest, update the manifest to the locked version, and report the
completeness, consistency, feasibility, traceability, data-integrity,
evidence-freeze, self-contained-runbook, and time-range results.

## Failure Handling

Do not lock while a blocking issue remains. For an unresolved origin,
reliability, or definition-alignment item, explain the data-quality impact,
state that reproduction is prohibited, ask one question, write the accepted
answer into the integrity report and specification, then repeat the final check.

For a time range that has not passed the final-window gate, preserve the
Init-selected mode, present the proposed exact dates, timezone, basis, and
coverage impact, and wait for confirmation. Ask for a mode change only if the
user explicitly requests one. Do not assume that `through_today` matches the
publication period or that the publication period is current.

For missing evidence or a stale evidence hash, return to
`/reprospec:outline`; do not solve the gap by reading the report during
Analyse. For an incomplete or changed specification, return to
`/reprospec:detail`, rerun `validate_spec.py`, and repeat this gate.

For an undefined required definition, return to `/reprospec:outline` and obtain
an approved `SUB-*`. Do not lock, infer, or ask for an arbitrary paper-term
interpretation at this gate.
