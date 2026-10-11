# Planning Rules

## Purpose

Define source priority, data-gap registration, user tradeoffs, and credential
boundaries for the Plan stage.

## Inputs

- the master outline and figure specifications;
- the manifest dependency map;
- local, private, public, and approved API sources.

## Data Integrity Check

Run `scripts/inspect_data.py` before asking the user about an unexplained
dataset. The structural check records:

- file identity, SHA-256, size, and modification time;
- format readability and parse errors;
- schema, row count, duplicate rows, and empty cells when available;
- missing, metadata-only, or unsupported formats.

For every inspected item, confirm:

- origin and acquisition method;
- acquisition date, provider, or source system;
- reliability as `high`, `medium`, or `low`, with supporting evidence;
- definition alignment for fields, keys, units, sample, period, frequency,
  coverage, missing values, and transformations;
- `definition_basis` as `source_explicit` or `approved_substitution`;
- for `approved_substitution`, the linked `SUB-*`, replacement `D-*`, and the
  exact explicit replacement definition used for alignment;
- affected master IDs and figure IDs;
- explicit user confirmation.

Ask provenance and reliability as separate questions, one at a time. Record the
first answer before asking the second.

Use only `aligned`, `mismatch`, or `unknown` for definition alignment. Only
`aligned` passes the gate. Reliability must be `high`, `medium`, or `low`;
`unknown` always blocks completion.

Definition alignment is against the executable contract, not against a guessed
meaning of an undefined paper term:

- `source_explicit`: the paper or report provides a complete operational
  definition.
- `approved_substitution`: the paper definition is missing or ambiguous and the
  user has approved a `SUB-*` whose replacement `D-*` is explicit, sourced, and
  fully recorded.

Any other basis blocks the integrity gate. For `approved_substitution`, verify
that the substitution is user-approved, references the same replacement `D-*`,
and records the exact explicit operational definition used by the source.
Never reinterpret the original term or mark it `aligned` without this contract.

Set the overall status to `complete` only when every item is present, inspected,
has a confirmed origin and reliability, is exactly `aligned`, has no unresolved
quality risk, and is confirmed by the user. A `low` reliability rating requires
documented quality risks. Any mismatch or unknown value blocks the next stage.

## Source Priority

1. Immutable files supplied by the user.
2. The paper's replication package, appendix, or supplementary data.
3. A user-authorized private source.
4. A versioned commercial API such as TuShare.
5. A reproducible public source.
6. A derived or estimated value with explicit uncertainty.

Values printed in the paper or report are comparison targets, not a source
priority. They may not make a gap `available`, `acquirable`, or `derivable`,
and they may not be copied, digitized, interpolated, or backfilled into a
dataset. A gap is `derivable` only when the derivation uses approved source
data and a documented method.

Do not substitute a source silently. If the substitution changes the
specification, update the master outline and affected figure specifications.

## Data Gaps

`data_gaps.csv` is an acquisition register, not a clarification document.

Record:

- master field ID;
- affected figure IDs;
- required definition and sample;
- source candidate;
- access method;
- permission requirement;
- status;
- fallback;
- evidence path;
- last verification time;
- linked `DATA-*` integrity ID;
- definition status;
- linked `SUB-*` when a replacement is approved;
- replacement definition;
- user approval.

Use one status: `available`, `acquirable`, `derivable`, `inferable`,
`unavailable`, or `ambiguous`.

`inferable` means inferable from approved source data and a documented method,
never inferred from the expected published result.

## User Discussion

For each material gap, state:

- what is missing;
- which figures it affects;
- available options;
- cost, quality, and coverage implications;
- recommended option with reasoning;
- fallback if the user cannot provide the source.

Ask one decision question at a time and write the accepted answer back into the
specification and data-gap register.

For option-based questions, state the recommendation before the options table
and allow the user to accept it by replying `yes` or `recommended`. For
short-answer questions, provide a suggested answer and allow the user to accept
it by replying `yes` or `suggested`.

## Credentials

Read credentials from environment variables or an approved secret store.
Never write secret values to specifications, logs, reports, or manifests.

## Output Contract

Update `data_gaps.csv`, the affected specifications, and the manifest so every
material data dependency is available, acquirable, derivable, limited, or
explicitly unresolved.

`data_integrity.json` must be `complete` and `data_integrity.md` must reflect
the same state before this stage reports completion.

## Failure Handling

When a source cannot be approved or acquired, or its definition is not exactly
aligned, keep the integrity status `in_progress` or `blocked`, explain the
affected figures, and ask one decision question about correction, replacement,
or fallback. If the issue is an undefined paper term, return to
`/reprospec:outline` for an approved `SUB-*`; do not infer the definition in
Plan. Do not advance to `/reprospec:analyse`.
