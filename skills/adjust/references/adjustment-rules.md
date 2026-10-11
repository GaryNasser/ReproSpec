# Adjustment Rules

## Purpose

Define the interaction, correction, impact-analysis, and traceability contract
for human-guided adjustments after automated verification and bounded repair.

## Inputs

- the user's manual-review finding;
- the published paper or report and its exact source location;
- the existing verification report, specification, data lineage, code, logs,
  and rendered output;
- the frozen source-evidence pack and current `spec_lock.json`;
- the reproduction manifest and known inter-figure dependencies.
- approved definition substitutions and their replacement definitions.

## Finding Contract

Record each finding with:

- a stable `ADJ-NNN` identifier;
- the target figure, panel, or paper section;
- the exact expected and actual observations;
- the source page, table, figure, paragraph, or code location used as evidence;
- the user decision and approval status;
- when the finding was accepted, rejected, or deferred.

Do not treat a visual impression as a confirmed data mismatch. Distinguish:

- an observed difference;
- a hypothesis about its cause;
- evidence that distinguishes among causes;
- the correction the user approves.

## Diagnosis

Use one primary cause:

- `data`: source, coverage, vintage, mapping, unit, or missing value;
- `outline`: missing or conflicting master rule;
- `detail`: incorrect figure-specific specification;
- `implementation`: acquisition, transformation, calculation, encoding, or
  rendering code;
- `style`: required palette or representative-color rendering;
- `pixel`: extraction, calibration, occlusion, or measurement uncertainty;
- `impossible`: the required source or evidence is unavailable.

If two causes remain plausible, gather one discriminating piece of evidence
before asking the user to choose a correction.

## Correction Contract

Before editing, state:

- the approved correction;
- the files and data objects to change;
- the reason each change is necessary;
- the expected effect on the target figure;
- the acceptance check;
- the possible impact on shared definitions and other figures.

Prefer the smallest correction that addresses the root cause. Do not bundle
unrelated improvements into an approved adjustment.

When data is missing:

1. Use an approved source or fallback when available.
2. Record the source, query or request, retrieval time, schema, row count, and
   SHA-256 hash.
3. If the value must be derived, document the formula, inputs, assumptions, and
   uncertainty.
4. If neither source nor derivation is supportable, keep the finding blocked
   and ask the user for a source or an accepted limitation.

Published values are expected comparison targets only. Never use a number from
the paper or report as source data, a missing-value fill, a hard-coded
constant, a plot coordinate, an annotation, a label, or a fabricated output
value. Never digitize the published image to complete missing data or replace
an approved source without disclosure.

If the correction reveals that the paper did not explicitly define a required
term, metric, sample, period, unit, formula, or transformation:

1. do not infer the definition or tune a result toward the publication;
2. present the `Definition Substitution` decision and obtain user approval for
   an explicit, source-backed replacement;
3. create or update `SUB-*`, including the replacement `D-*`, operational
   definition, provenance, functional rationale, and known deviation;
4. update the master specification, affected figure data contracts, and
   data-integrity records consistently;
5. increment the master version and mark every dependent figure `stale`.

The corrected figure cannot be rerun from the original vague definition.

Do not reopen the report during adjustment to discover a new execution
requirement and patch it directly into code. Return the fact to
`/reprospec:outline`, update and re-freeze the evidence pack, revise the
affected runbook, rerun `validate_spec.py`, and rerun `lock_spec.py` before
reproduction.

## Impact Analysis

After every correction, classify every included figure as `affected`,
`unaffected`, or `unknown`. Inspect at least:

- direct `MASTER-*`, `DATA-*`, and specification dependencies;
- raw, canonical, interim, or derived datasets used by multiple figures;
- shared acquisition, cleaning, transformation, and calculation modules;
- shared plotting helpers, themes, layout functions, title handling, and export
  code;
- figure IDs, panel mappings, paths, and manifest links;
- whether a master-level definition or shared version changed.

Use code search, import graphs, data lineage, manifest links, and hash
comparisons when available. Do not rely on filenames alone.

Classification rules:

- `affected`: the corrected object participates in the figure's lineage or its
  output can change.
- `unaffected`: record concrete evidence that the figure does not use the
  changed object.
- `unknown`: the dependency cannot be proven either way. Treat it as requiring
  a rerun or an explicit user-accepted limitation.

If a master-level definition changes, increment the master version and mark all
dependent figures `stale`. If a shared data or code change has broad
dependencies, the affected set may include most or all figures.

Any changed frozen evidence pack or figure specification invalidates both its
Detail validation and its old lock record. Re-freeze, validate, and relock
before re-rendering. Revalidation also removes any prior run-validation record
so an old execution cannot be reused.

## Recheck Contract

For the corrected figure and every `affected` or `unknown` figure:

1. Re-render from the approved inputs.
2. Re-run the applicable numerical, chart-type, encoding, palette, language,
   default title-style, title-alignment, and pixel checks.
3. Compare before-and-after outputs.
4. Record pass, fail, or blocked with exact evidence.
5. Leave unaffected figures untouched unless their validation evidence is
   stale or the user requests a full gallery review.

## Artifact Schema

Append one record per finding to `adjustment_log.md`. The record must contain
the finding, evidence, options, user decision, correction, changed artifacts,
impact matrix, rerun targets, verification results, and residual risk.

Keep `reproduction_manifest.json.adjustments` aligned:

```json
{
  "adjustments": {
    "session": 1,
    "path": "adjustment_log.md",
    "history": [
      {
        "id": "ADJ-001",
        "status": "completed",
        "finding": "Short statement of the observed difference",
        "target_figures": ["F001"],
        "cause_type": "data",
        "computation_source": "computed_from_approved_real_data",
        "definition_substitutions": [],
        "user_approved": true,
        "changed_artifacts": [],
        "affected_figures": [],
        "unaffected_figures": [],
        "unknown_figures": [],
        "rerun_figures": [],
        "verification": {},
        "residual_risk": [],
        "continuation_decision": {
          "status": "pending",
          "selection": null,
          "next_command": null
        }
      }
    ]
  }
}
```

Use `completed`, `partial`, or `blocked` for the record status. A finding with
an explicit user-accepted residual risk can be `completed` when the limitation
is recorded; otherwise unresolved work remains `partial` or `blocked`. Update
`workflow.active_stage` to `adjust`.

## Continuation Decision

After a completed adjustment round, do not move directly to organization.
Keep `workflow.active_stage` as `adjust`, clear `workflow.next_stage`, and ask
the user to choose between exactly two commands:

1. `/reprospec:organize` to accept the completed adjustment round and move to
   canonical data organization.
2. `/reprospec:adjust` to continue adjustment with another finding or scope.

Record the decision in the adjustment record as `organize` or `adjust_more`
after the user answers. Set `workflow.next_stage` to `organize` only for the
first choice. For the second choice, keep the workflow in `adjust` and begin a
new finding cycle; do not set `workflow.next_stage`.

If the round is `partial` or `blocked`, resolve the outstanding issue or obtain
an explicit user-accepted limitation before offering `/reprospec:organize`.
Otherwise the only valid continuation is `/reprospec:adjust`.

## Failure Handling

Keep the finding blocked when:

- the user has not approved a correction;
- the required source cannot be obtained or verified;
- the impact cannot be bounded;
- the correction would require an unapproved data substitution;
- the approved correction cannot satisfy the agreed acceptance check.
- the required definition substitution is unapproved, incomplete, or
  inconsistent with the replacement field used by the figure.

Do not mark the adjustment complete while the corrected figure or an affected
figure has an unexplained required failure.

The default title style is part of the locked rendering contract. A
source-matched title font does not justify changing it; only an explicit
approved finding may alter the title policy.

The source-derived palette is also part of the locked rendering contract. A
palette mismatch or blocked palette outcome requires a source-backed correction
or an explicit approved change to the specification.
