# Outline Rules

## Purpose

Define the full-document scan, figure classification, stable IDs, and decision
protocol for the paper-level outline.

## Inputs

- the selected paper and supporting material;
- the source-data inventory;
- the initialized reproduction manifest.
- `assets/figure-evidence-template.md` for each included figure.

## Full-Document Scan

Scan the complete document before drafting the outline:

- abstract, introduction, and conclusion;
- data and methodology sections;
- every figure caption and panel label;
- footnotes and table notes;
- appendices and supplementary material;
- data source and replication statements;
- the user's source-data inventory.

Record page, figure, table, or section references for every extracted rule.
Numbers transcribed from the paper or report are expected comparison targets;
label them as such and never treat them as source observations or implementation
inputs.

## Source Evidence Freeze

Before Detail begins, create `evidence/<figure-id>.md` for every included
data-driven figure and fill every section of
`assets/figure-evidence-template.md`.

The evidence pack is the only report-derived fact source allowed in Detail and
Reproduce. It must capture:

- source pages, captions, body paragraphs, tables, footnotes, appendices, and
  supplementary evidence used by the figure;
- the overall and per-panel chart types;
- panel boundaries, axes, scales, encodings, legends, series order, labels,
  annotations, and visible text;
- exact source text required to interpret each data field or transformation;
- source terms, explicit definitions, approved `SUB-*` contracts, units,
  samples, periods, frequencies, and required fields;
- exact printed or vector values for later comparison, marked
  `comparison_only`;
- exact or sampled palette colors with source regions, conversion, mapping, and
  tolerance, or evidence for `not_applicable`;
- every unresolved question and its decision or accepted limitation.

Split compound observations into separate `E###` rows. Every row records its
source locator, exact quote or observed fact, required use, and classification.
Do not summarize away details that Detail needs to produce an executable
specification.

If any required fact cannot be recovered, ask one question before freezing the
pack. Do not leave the issue for Reproduce to solve by rereading the report.
After the packs are complete, run:

```text
python scripts/finalize_evidence.py --workspace <workspace> --paper-id <paper-id>
```

The script writes `source_evidence.status`, one hashed item per figure, and the
freeze timestamp to the manifest. A blocked or draft evidence pack prevents
Detail and all later stages.

Before freezing, the Freeze Summary must declare `yes` for panels, axes and
series, visible text, required definitions, palette evidence (or
`not_applicable`), and comparison values. It must set `Missing evidence` to
`none` and `No report reread required` to `yes`, and it must contain no
unresolved Open Questions row. The script sets `Evidence status: frozen` and
the freeze timestamp only after all declarations pass.

Record the paper or report's original start and end dates in
`master_spec.md`. Copy the Init-confirmed mode from
`time_range_policy.selection`, but leave the exact reproduction window pending.
`/reprospec:analyse` must preserve that mode unless the user explicitly changes
it, resolve the exact dates, timezone, and basis, and obtain final confirmation
before locking.

## Definition Clarity Gate

For every required term, metric, field, sample rule, period, frequency, unit,
formula, or transformation, classify the source definition as:

- `explicit`: the document states an operational definition complete enough to
  reproduce without guessing;
- `missing`: no operational definition is provided;
- `underspecified`: at least one material facet is absent or vague;
- `conflicting`: the document provides incompatible definitions.

Do not treat common industry usage, a familiar acronym, a field name, an image
label, or agreement with the expected published result as an explicit
definition. Do not silently infer missing facets.

Every `missing`, `underspecified`, or `conflicting` item requires a user
decision before a dependent figure can be specified. Record the original item
and replacement as separate `D-*` fields, create a `SUB-NNN` mapping, and link
it to the relevant `Q-*` decision. A valid replacement contract contains:

- the original `D-*`, source location, source text, and the exact definition
  gap;
- the replacement `D-*` and replacement term;
- an explicit operational definition covering meaning, source field,
  universe, period, frequency, unit, formula or transformation, and material
  missing-value or aggregation behavior;
- the functional relationship to the original item and why the replacement is
  analytically appropriate;
- source and provenance requirements;
- known semantic, coverage, or measurement deviation and its expected effect;
- affected figures and master dependencies;
- the linked `Q-*`, user response, approval timestamp, and status.

The replacement must preserve the analytical role. It must not be selected to
match a published value, and published values must not be used to tune its
definition. If no acceptable explicit replacement is available, ask the user
to skip the affected figure or claim and record the limitation.

Set `definition_policy.decision_required` to true while any required definition
is unresolved. Set it to false only when every required definition is
`explicit`, covered by an approved `SUB-*`, or explicitly skipped.

Write each approved substitution into the manifest using this contract:

```json
{
  "id": "SUB-001",
  "original_master_id": "D-001",
  "original_term": "Original paper term",
  "source_location": "p. 12, methodology",
  "source_status": "underspecified",
  "replacement_master_id": "D-002",
  "replacement_term": "Explicit replacement term",
  "replacement_definition": "Complete operational definition",
  "functional_rationale": "Why it preserves the analytical role",
  "source": "Approved source and field",
  "unit": "Explicit unit",
  "period_and_frequency": "Explicit period and frequency",
  "universe": "Explicit sample or entity universe",
  "transformation": "Formula, aggregation, and window",
  "known_deviation": "Known semantic, coverage, or measurement difference",
  "limitations": ["Explicit limitation"],
  "affected_figures": ["F001"],
  "decision_id": "Q-001",
  "user_approved": true,
  "approved_at": "YYYY-MM-DDTHH:MM:SS+00:00",
  "status": "approved"
}
```

Allowed `source_status` values are `missing`, `underspecified`, and
`conflicting`. The replacement `D-*` must be different from the original `D-*`.
A skipped item does not receive a `SUB-*`; record the skip and limitation
through the existing decision and exclusion or limitation records.

## Figure Classification

Classify every candidate image before creating detailed specifications.

Use `data_driven` when reproduction requires any of:

- plotted values or coordinates;
- quantitative series, bars, points, intervals, or distributions;
- a numerical table rendered as a chart;
- statistical relationships, maps, heatmaps, or model outputs.

Use `excluded_schematic` when the image communicates a concept without a data
mapping. Examples include:

- workflow and process diagrams;
- conceptual frameworks and architecture diagrams;
- qualitative timelines;
- conceptual arrows, block diagrams, or causal diagrams;
- decorative images or photographs that contain no quantitative structure.

If the classification is genuinely ambiguous after reading the caption, body,
and appendix, ask one question and wait. Do not create a detailed figure
directory for excluded images.

Record excluded items in `reproduction_manifest.json` under
`excluded_figures`:

```json
{
  "id": "F003",
  "title": "Conceptual model",
  "source_page": "p. 12",
  "category": "excluded_schematic",
  "reason": "Conceptual framework with no data mapping"
}
```

## Stable IDs

Use:

- `D-*` for data fields;
- `DATA-*` for user-provided data-integrity records;
- `T-*` for transformations;
- `S-*` for sample or selection rules;
- `Q-*` for user decisions;
- `L-*` for known limitations;
- `SUB-*` for approved definition substitutions.

Never reuse an ID for a different meaning.

## Terminal Questions

When the source is insufficient:

1. State the issue and source location.
2. Quote the relevant source text or caption.
3. Explain what cannot be determined.
4. Present concrete options.
5. State the recommended option and its impact.
6. Ask one question and wait.
7. Write the answer directly into `master_spec.md`.

Do not create a separate clarification document.

For a missing or ambiguous definition, use the
`Definition Substitution` decision protocol in `SKILL.md`. State the original
term and source location, the exact missing facets, the affected figures, the
proposed explicit replacements with provenance and limitations, and one
question. Do not offer an inferred definition as an approved substitute.

## Versioning

Start at `1.0.0`. Increment the version when the outline changes in a way that
affects figure behavior. Record changed IDs and affected figures.

## Output Contract

Write the complete paper-level contract to `master_spec.md` and update the
included figure, excluded figure, decision, and unresolved inventories in the
manifest. Also write every approved substitution to
`definition_policy.substitutions` and keep `definition_policy.decision_required`
aligned with the unresolved definition count. Freeze one source-evidence pack
per included figure under `evidence/` and record its path and SHA-256 in
`source_evidence.items`.

## Failure Handling

Ask one question at a time when the source cannot resolve a material rule. If
the user cannot answer, mark only the dependent field `unresolved` and pause
dependent work.
