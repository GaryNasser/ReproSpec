# ReproSpec

ReproSpec is a Claude Code plugin that reproduces figures and quantitative
claims from data-driven papers and research reports. The plugin is named
`reprospec`; each workflow stage is one skill under it, invoked as a
`/reprospec:<stage>` slash command.

Only data-driven figures are reproduced. Schematic diagrams, conceptual
illustrations, workflow diagrams, and other images that communicate meaning
without a data mapping are recorded as excluded and do not receive reproduction
directories.

The workflow is split into twelve explicit stages so users can inspect progress,
resolve specification and data issues, and run bounded repair loops without
losing provenance.

## Workflow

| Stage | Command | Primary outcome |
| --- | --- | --- |
| Init | `/reprospec:init` | Select one paper, enforce the computation-source policy, and create the isolated workspace |
| Outline | `/reprospec:outline` | Extract the data contract, classify figures, and freeze one evidence pack per figure |
| Detail | `/reprospec:detail` | Expand included figures into self-contained step-by-step runbooks |
| Plan | `/reprospec:plan` | Inspect data integrity and resolve data quality with the user |
| Analyse | `/reprospec:analyse` | Final-align definitions and lock the specification |
| Reproduce | `/reprospec:reproduce` | Build the figures and preserve provenance |
| Verify | `/reprospec:verify` | Quantify deviations and issue AI repair challenges |
| Rework | `/reprospec:rework` | Answer AI repair challenges and run bounded corrections |
| Adjust | `/reprospec:adjust` | Apply agreed manual-review corrections and recheck all affected figures |
| Organize | `/reprospec:organize` | Turn raw PDFs and text into reusable canonical datasets |
| Audit | `/reprospec:audit` | Write the stepwise source-to-image traceability record |
| Deliver | `/reprospec:deliver` | Assemble the flat figure gallery and evidence package |

Each stage reports its status and the exact next command. Generated artifacts
are written in English. Terminal responses follow the user's current language.

## Terminal Display

Each stage emits a compact Markdown completion card with progress, status,
summary values, artifacts, and the exact next command. For example:

```markdown
**ReproSpec 3/12 | DETAIL**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | ---: |
| Figures specified | 6 |
| Excluded schematics | 4 |
| Preflight failures | 0 |

**Artifacts**

- `work/001-paper-title/master_spec.md`
- `work/001-paper-title/figures/F001/spec.md`

> **Next**
>
> `/reprospec:plan`
>
> **Reason:** All included figures now have detailed specifications.
```

## Run the Workflow

Place the paper and any private source data in the workspace root, then run the
stages in order:

```text
/reprospec:init
/reprospec:outline
/reprospec:detail
/reprospec:plan
/reprospec:analyse
/reprospec:reproduce
/reprospec:verify
/reprospec:rework
/reprospec:adjust
/reprospec:organize
/reprospec:audit
/reprospec:deliver
```

Each stage is a skill under the `reprospec` plugin and is invoked as the
corresponding `/reprospec:<stage>` slash command.

Outside the twelve stages, file a problem encountered during a reproduction
with `/reprospec:feedback` (see [Feedback](#feedback)).

Place source datasets under `inputs/` or pass each file explicitly to the Plan
stage. Stages that accept target IDs, such as reproduce, verify, rework, adjust,
organize, and audit, also accept a bounded request such as
`/reprospec:reproduce F001,F002`.

Every stage after `/reprospec:init` must verify and comply with the
`computation_policy`, `time_range_policy`, and data-decision state established
by Init. A missing, relaxed, or unresolved Init requirement blocks that stage.

`/reprospec:init` asks whether to reproduce the paper or report's original time
range or extend through today immediately after paper selection and before
inspecting or acquiring input data or creating the workspace. This early answer
determines which input data must be acquired and inspected.
`/reprospec:analyse` then resolves and confirms the exact ISO start and end
dates, timezone, basis, and confirmation timestamp before locking or
reproduction. If the user later wants a different end date, the analysis gate
must be reopened and affected figures must be re-run. For `through_today`, the
end date is the latest available observation on the confirmed date, not an
unverified assumption that every source has data through the calendar date.

## Definition Substitution Gate

When the paper or report does not state an explicit operational definition for
a required term, metric, sample, period, unit, formula, or transformation,
ReproSpec does not silently choose a common interpretation. `/reprospec:outline`
makes the ambiguity explicit, discusses replacement candidates with the user,
and records an approved `SUB-*` contract.

Each substitution links the original `D-*` to a new replacement `D-*` and
records:

- the exact missing or conflicting definition and source location;
- the replacement's operational definition, source field, universe, period,
  frequency, unit, formula, and transformation;
- the functional relationship to the original item and the known semantic,
  coverage, or measurement deviation;
- affected figures, the linked user decision, approval time, and status.

The substitute must preserve the analytical role. It must not be selected or
tuned to match published values. `/reprospec:detail`, `/reprospec:plan`,
`/reprospec:analyse`, `/reprospec:reproduce`, and `/reprospec:audit` all keep
the same `SUB-*` contract, and locking is blocked while any required definition
is underspecified, conflicting, unapproved, or incompletely recorded.

## Evidence Freeze and Execution Runbook

Reproduction should not rediscover the same report while building each figure.
`/reprospec:outline` therefore reads the report once, creates
`evidence/<figure-id>.md` for every included figure, and freezes each pack with
a SHA-256 in `reproduction_manifest.json`.

Each evidence pack records the source snapshot, panel and chart anatomy, axes,
series, labels, annotations, data semantics, definitions or approved
substitutions, palette evidence, comparison-only printed values, and resolved
questions. Every report-derived fact receives an `E###` identifier. A missing
fact is resolved before Outline completes; it is not left for reproduction to
guess.

`/reprospec:detail` uses only the frozen evidence pack, master outline, and
approved source-data contract. It writes a self-contained execution runbook
with contiguous `S01`, `S02`, and later steps. Every step states:

- its dependencies and exact input;
- one precise operation and the formula or decision rule;
- all parameters, timezone, units, filters, joins, and aggregation behavior;
- a code entrypoint and command;
- the exact output path, format, and schema;
- an objective validation that can fail;
- the failure action and the artifact handed to the next step.

The specification also maps executable areas to `E###` evidence, records the
evidence-pack SHA-256, and includes a checked No-Reread Checklist.
`validate_spec.py` rejects placeholders, vague language, missing step fields,
orphan evidence references, unchecked items, and changed evidence hashes.

`/reprospec:analyse` revalidates the same specification and evidence hashes
before writing `spec_lock.json`. `/reprospec:reproduce` may read only the
locked `spec.md`, the frozen evidence pack, and approved source data. It must
not reopen the paper or report to discover a requirement. If a runbook rule is
missing, reproduction returns to `/reprospec:detail`; if evidence is missing,
it returns to `/reprospec:outline`. If either locked hash changes, the
specification must be validated and locked again.

The run record stores the specification and evidence hashes, one execution
entry per `Sxx` step, `report_reread_for_requirements: false`, and an empty
`reread_events` list. Verification, rework, adjustment, audit, and delivery all
preserve or revalidate those records.

## Data Organization Gate

After automated repair and manual adjustment are complete,
`/reprospec:organize` inventories the raw data used by the reproduction and
replaces expensive-to-reprocess source collections with canonical datasets
under `data/organized/`. Typical raw inputs include large collections of PDFs,
text files, OCR output, HTML, and spreadsheets; typical canonical outputs are
JSON, Parquet, CSV, or SQLite.

The goal is to make later reproduction, audit, and reuse load the canonical
dataset instead of parsing the raw sources again. This is not generic
compression or lossy summarization. Every canonical dataset records its scope,
schema, metadata, source hashes, extraction methods, source locators,
transformations, figure links, and audit handoff. Required values and source
links must remain complete even when the resulting dataset is much smaller.
The inventory covers reproduction-local `data/` directories, figure-local
data, and raw corpora under the workspace `inputs/` directory.

Retaining original data is a valid outcome and requires no approval. Moving,
overwriting, or deleting original data requires an explicit user decision
after showing the affected paths, hashes, verification evidence, consequences,
and recovery options. Ambiguous or missing approval means the originals remain
untouched.

The canonical datasets, inventory, catalog, organization record, and source
disposition are required before the workflow may advance to `/reprospec:audit`.

## Figure Audit

Before delivery, `/reprospec:audit` writes one Markdown traceability document
per included figure. Each document uses sequential `A -> B -> C` steps from
the original data source through every processing and reproduction operation
to the rendered image.

Audit files are stored at `work/<paper-id>/audits/<figure-id>.md` and delivered
under `figure-output/<paper-id>/audits/<figure-id>.md`, outside the rendered
figure output directories. Every step must identify its input, operation,
parameters and code, output, evidence, validation, and next handoff.

## Figure Rendering Guidelines

Every rendered figure title and panel title uses Matplotlib's default Notebook
title font and size, resolved from `matplotlib.rcParamsDefault` independently of
the published figure. Both overall and panel titles remain centered.

Published numbers and values extracted from the paper or report are comparison
targets only. Never copy, hard-code, backfill, interpolate, digitize, or
otherwise inject those values into source data, intermediate datasets, model
inputs, code constants, plot coordinates, annotations, labels, or final output
values. Every reproduced value and mark must be computed from approved real
data with traceable code. If the required source data is unavailable, mark the
figure blocked, partial, or limited and request the actual source; do not
reconstruct it from the publication.

`/reprospec:init` records this rule as `computation_policy` in the shared
manifest. If an item can only be drawn from publication numbers, Init reports
the data gap and asks the user to either supplement the underlying data or skip
the item. It records `data_plan.decision_required` and pauses the next stage
until that decision is made. The publication value is never an allowed
fallback.

Canvas size is not a specification requirement and must not be written as a
fixed per-figure size or output dimension in `spec.md`. Reproduction code
chooses or automatically adjusts the canvas from the published aspect ratio,
panel layout, text, and data content. A general `figsize=(12, 5)` value may be
used as a non-binding fallback recommendation in execution guidance, but it is
not a required size and does not become an acceptance criterion.

The figure type and data encoding are hard requirements. A stacked bar chart
must remain a stacked bar chart, a line chart must remain a line chart, a
scatter plot must remain a scatter plot, and no style adjustment may change the
chart type.

Matching the published figure's palette is required for every figure that uses
color to encode data. Use exact vector colors when available; otherwise sample
representative raster regions and record the extraction method and tolerance.
Only a figure with no color-dependent encoding may be marked
`not_applicable`, with evidence. A palette mismatch or unverifiable palette
prevents a `matched` result. Title font family and size must not be derived from
the source. Margins, line widths, markers, grids, spines, legends, annotations,
colorbars, and other fine visual details do not need to be imitated.

Figure outputs are PNG by default. Reproduction should not generate PDF, SVG,
EPS, JPEG, TIFF, or other formats unless the specification records an explicit
user request or downstream requirement.

Plotted titles, axes, ticks, legends, annotations, and panel labels use English
by default. Another language is allowed only when the user explicitly requests
it or the figure specification records a documented exception.

The final delivery package keeps every available rendered image in a flat
`figure-output/<paper-id>/figures/` gallery with unique
`<figure-id>__<relative-name>` filenames. Complete per-figure evidence remains
under `figure-output/<paper-id>/figure_details/`.

## Verification and Rework Challenges

For every confirmed mismatch, `/reprospec:verify` writes
`figures/<figure-id>/rework_challenge.json`. The challenge is addressed to the
`/reprospec:rework` AI, not to the user. It records the quantified or structural
deviation, evidence paths, one causal question, required structured response
fields, and the acceptance check that must pass after repair.

`/reprospec:rework` cannot edit a figure until it answers the challenge. The
response must identify one primary cause, cite supporting evidence, rule out
plausible alternatives, name the affected lineage or code, define the minimum
change, run a falsification test, and preserve the original acceptance check.
The work then moves through reproduction and re-verification. Verification
closes the challenge only when the same acceptance check passes.

The challenge loop never asks the user to diagnose a machine mismatch. After
three failed attempts, the challenge is marked `blocked` and automatic repair
stops. `/reprospec:adjust` remains unchanged: it is a separate, human-controlled
stage for issues that the automatic loop cannot resolve.

## Manual Adjustment

After `/reprospec:verify` and `/reprospec:rework` finish the automated checks
and bounded repairs, use `/reprospec:adjust` for human review findings that the
machine did not resolve or could not detect. Describe the exact figure, panel,
source location, expected result, and actual result. The adjust skill
investigates the cause, presents correction options, and waits for approval
before editing data, specifications, or implementation code.

After an approved correction, `/reprospec:adjust` classifies every included
figure as `affected`, `unaffected`, or `unknown`. It re-renders and re-verifies
every affected or unknown figure, records the impact evidence in
`adjustment_log.md`, and updates the manifest. Missing data may be completed
only from an approved source or fallback; it is never fabricated.

After all manual corrections and affected-figure rechecks are complete,
`/reprospec:adjust` pauses and asks whether to move to the next stage or keep
adjusting. It presents exactly two commands:

- Move to the next stage: `/reprospec:organize`
- Continue adjusting: `/reprospec:adjust`

The workflow does not advance until the user selects one of these commands.

## Data Integrity Gate

Data integrity is a mandatory gate between specification and reproduction:

1. Inspect every user-provided dataset for format, schema, row count, duplicate
   rows, empty cells, and parse errors.
2. Ask how unexplained data was obtained and what evidence supports its
   reliability.
3. Final-align fields, keys, units, sample, period, frequency, coverage,
   missing values, and transformations before reproduction.
4. Record explicit user confirmation in `data_integrity.json`.

The status may become `complete` only when every source is present, inspected,
has confirmed origin and reliability, is exactly aligned, and has no unresolved
quality issue. Otherwise ReproSpec must not lock the specification, must not
start `/reprospec:reproduce`, and must keep the next action inside
`/reprospec:plan` or `/reprospec:analyse`.

## Feedback

When a reproduction exposes a ReproSpec problem — a broken stage, a confusing
gate, a documentation gap — `/reprospec:feedback` turns it into a GitHub issue
on this repository. You can invoke it yourself at any time, or start it after
a stage reports a problem. The skill never creates a branch, commit, push, or
pull request, and never writes into your reproduction workspace.

Privacy is a hard gate, not a guideline. The skill prepares the issue entirely
on your machine, scrubs credentials, personal paths, identifiers, raw data
rows, and long paper excerpts, then shows a consent card with the verbatim
issue title, labels, and body. Nothing is published until you explicitly
approve that preview. Declining or giving an ambiguous answer cancels the
submission with no residue anywhere.

Issues follow the repository's conventions: the title is
`[<Category>] <short problem title>`, labels come from the repository's
existing labels, and the body mirrors the
[feedback issue form](.github/ISSUE_TEMPLATE/feedback.yml) with summary,
environment, reproduction steps, expected versus actual behavior, and a
privacy statement.

The GitHub CLI (`gh`) is required. If it is not installed or not
authenticated, the skill tells you plainly that feedback cannot be used yet,
prints the install and `gh auth login` steps, and stops without creating
anything.

## Install

Validate the plugin first:

```bash
claude plugin validate .
```

Load it for a single session without installing (run from the repo root, or
pass the path to `--plugin-dir`):

```bash
claude --plugin-dir .
```

To install it for real, add the bundled marketplace and install the plugin:

```bash
claude plugin marketplace add .
claude plugin install reprospec@reprospec-marketplace
```

To install from a git clone or a hosted repository, push this repository (it
already contains `.claude-plugin/marketplace.json`) and run:

```bash
claude plugin marketplace add <owner>/<repo>
claude plugin install reprospec@reprospec-marketplace
```

After editing skill files in an already-loaded session, run `/reload-plugins`
to pick up the changes.

## Repository Layout

```text
.claude-plugin/
|-- plugin.json
`-- marketplace.json
.github/
`-- ISSUE_TEMPLATE/
    `-- feedback.yml        # feedback issue form used by /reprospec:feedback
docs/
|-- skill-format.md
skills/
|-- init/
|-- outline/
|-- detail/
|-- plan/
|-- analyse/
|-- reproduce/
|-- verify/
|-- adjust/
|-- rework/
|-- organize/
|-- audit/
|-- deliver/
`-- feedback/
```

The reusable format contract for contributors is documented in
[docs/skill-format.md](docs/skill-format.md). It defines the shared entrypoint
skeleton without changing workflow behavior or generated artifact paths.

Generated workspaces, downloaded data, credentials, and final figure outputs
are ignored by Git. Only reusable skill source files are tracked.
