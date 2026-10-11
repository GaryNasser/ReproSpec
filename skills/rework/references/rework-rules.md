# Rework Rules

## Purpose

Define bounded multi-round repair, root-cause classification, invalidation, and
stopping behavior.

## Inputs

- comparison reports and limitations;
- one issued `rework_challenge.json` per target figure;
- the frozen source-evidence pack and the current `spec_lock.json`;
- approved definition substitutions and replacement definitions;
- previous rework rounds;
- target figure IDs or challenge IDs.

## Challenge Contract

A rework round may begin only for a figure whose verification challenge status
is `issued`. If the challenge is missing, lacks required evidence, is already
resolved, or is blocked, stop and return to `/reprospec:verify`.

Before editing, rework must answer every field listed in the challenge's
`required_response_fields`:

- `cause_type`;
- `causal_evidence`;
- `rejected_alternatives`;
- `affected_lineage_or_code`;
- `minimum_change`;
- `falsification_test`;
- `expected_effect`;
- `acceptance_check`.

The answer must cite concrete evidence. "Likely", "probably", or a visual
impression without a discriminating test is not sufficient. At least one
falsification test must be run before editing to distinguish the selected
cause from plausible alternatives. If the test contradicts the answer, revise
the response rather than changing code.

The challenge is AI-facing. Do not ask the user to choose a cause, select a
repair path, or approve an automatic correction. If an unavoidable human
business decision prevents an evidence-based answer, set the challenge status
to `blocked`, make no edits, and defer manual review to `/reprospec:adjust`.

After the answer is complete, run `scripts/begin_rework.py`. The script must
validate the challenge, mark it `answered`, append the response to its history,
increment the rework round, and mark the targets `stale` before artifacts are
changed.

## Round Model

Each invocation handles one round. Multiple rounds are expected.

Record:

- round number;
- target figures;
- challenge ID and prior attempt;
- root cause;
- cause type;
- challenge response and falsification result;
- changed files;
- changed master IDs;
- stale figures;
- rerun targets;
- result.

## Classification

Use exactly one primary cause:

- `data`: source, version, mapping, coverage, or units;
- `outline`: missing or conflicting master rule;
- `detail`: incorrect figure-specific specification;
- `implementation`: code, join, formula, aggregation, or rendering logic;
- `style`: required palette or representative-color rendering;
- `pixel`: calibration, extraction, occlusion, or uncertainty;
- `impossible`: unavailable evidence or an accepted limitation.

## Anti-Overfitting

Do not tune data, formulas, parameters, styling, or validation choices solely
to force an exact match with the published result. A correction must be
justified by the classified root cause and supported by available evidence.
When honest exact agreement is not attainable, do not present the result as an
exact match. Record and explain the residual mismatch, uncertainty, or accepted
limitation to the user.

Published values are comparison targets only. Never repair a mismatch by
copying, hard-coding, backfilling, interpolating, digitizing, or injecting an
expected published value into data, code, axes, annotations, labels, or output
values. A valid repair must change real inputs, formulas, joins, or
implementation logic and must reproduce the result from approved source data.

The rework answer must explain why the proposed change addresses the cause. It
must not tune thresholds, filters, parameters, or validation rules merely to
make the published result match. The challenge's original acceptance check
cannot be weakened or rewritten to convert a failure into a pass.

Wrong chart type, stacking, grouping, mark, or data encoding is always a defect
and must be repaired using `detail` or `implementation` as the primary cause.
Never change a stacked bar chart into a grouped bar or line chart, a line chart
into bars or points, or any other type into a different representation.

A title that does not use `matplotlib_notebook_default` is a rendering-contract
defect. Repair it through `detail` or `implementation` by resolving the default
family, size, and weight from `matplotlib.rcParamsDefault` and pinning them on
the title text. A title that matches or approximates the published title font
must be restored to the default policy. A font difference from the source is
not a defect.

Non-English plot text is also a defect unless the locked specification records
an explicit user-requested exception. Repair titles, labels, ticks, legends,
annotations, and panel text through `detail` or `implementation` while
preserving symbols, units, acronyms, and numeric values.

Palette matching is a required rendering outcome whenever color encodes data.
A palette mismatch or blocked palette contract must be repaired using the
recorded source extraction, mark mapping, color-space conversion, and
tolerance. It cannot remain `matched`, and arbitrary replacement colors are
not acceptable. Figure size, source fonts, typography other than the fixed
title policy, lines, markers, grids, legends, annotations, layouts, and other
fine visual details need not be matched. The prohibited behavior is arbitrary
cosmetic tuning that is not grounded in the source or user instruction.

## Invalidation

When master IDs change:

1. increment the master version;
2. update the version history;
3. update the frozen evidence pack for every affected figure;
4. rerun `finalize_evidence.py`;
5. update affected figure specifications and rerun `validate_spec.py`;
6. rerun `lock_spec.py` and record the new hashes;
7. mark dependent figures `stale`;
8. rerun only those figures.

When a figure-specific executable rule changes:

1. update the frozen evidence pack if the missing facts belong to the report;
2. re-freeze the evidence and update the affected `spec.md`;
3. rerun `validate_spec.py`;
4. rerun `lock_spec.py` and replace the old specification/evidence hashes;
5. mark the affected figures `stale` before reproduction.

`validate_spec.py` removes any prior `run_validation` record when a
specification is revalidated. The figure cannot inherit an old execution
record after its locked inputs change.

When only a figure implementation changes, mark only that figure `stale`.
When only its palette contract or rendering code changes, mark only that figure
`stale`.

Rework must not discover a requirement by reopening the report and inserting it
directly into code or a challenge response. The requirement belongs in the
frozen evidence pack and, when executable, in the validated runbook.

## Output Contract

Append one traceable round to `rework_log.md`, identify the minimum changed
artifacts, mark dependent figures `stale`, and list the rerun targets. Update
each challenge to `answered` with its complete response, falsification result,
history entry, and rework round. If no honest answer exists, set the challenge
to `blocked` and make no correction.

Record every changed specification or evidence hash, the successful
`validate_spec.py` result, and the new `spec_lock.json` hashes. A figure may not
return to reproduction with an old lock record.

`/reprospec:verify` owns closure. Rework does not mark a challenge `resolved`;
only a later verification that passes the recorded acceptance check may do so.

## Definition Substitutions

Rework must use the locked explicit definition or the replacement field named by
an approved `SUB-*`. It must not infer a different meaning for an
`underspecified` or `conflicting` paper term and must not change a substitution
to improve numerical agreement.

If the evidence shows that the approved definition is missing, incomplete, or
the wrong analytical role, do not edit automatically. Set the challenge to
`blocked`, record why the definition decision is human-owned, and return the
issue to `/reprospec:outline` and `/reprospec:adjust` for negotiation. A new or
changed `SUB-*` requires explicit user approval and a new master version.

## Failure Handling

When a challenge cannot be answered with evidence:

1. set its status to `blocked`;
2. make no artifact changes;
3. record the missing evidence or human decision;
4. do not invoke `/reprospec:adjust` automatically.

After three rounds with the same unresolved root cause:

1. stop automatic retries;
2. report the evidence and attempts;
3. leave the challenge blocked and identify manual `/reprospec:adjust` review
   as an available human action.

Do not loop indefinitely.
