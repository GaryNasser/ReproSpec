# ReproSpec Skill Format

This document defines the presentation contract for every ReproSpec stage
skill, from `init` through `deliver`. It governs structure and wording only.
Skill names, workflow order, script interfaces, manifest fields, status values,
and artifact paths are behavior and must not change during a formatting-only
revision.

## Required Frontmatter

Use quoted scalar values and the same metadata shape in every entrypoint:

```yaml
---
name: "stage"
description: "Describe the stage outcome and its activation boundary."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.1.0"
---
```

`disable-model-invocation: true` means a stage runs only on explicit user
invocation. The `metadata` map follows the Agent Skills specification. Do not
add a runtime-specific field unless that runtime actually consumes it and the
skill needs that behavior.

## Runtime Targets

The stages are packaged as one Claude Code plugin named `reprospec`. Each stage
is a skill under the plugin and is invoked as a `/reprospec:<stage>` slash
command: `/reprospec:init`, `/reprospec:outline`, and so on through
`/reprospec:deliver`.

- Claude Code reads `SKILL.md` and its frontmatter; the plugin name supplies the
  `reprospec:` prefix and the skill's `name` supplies the stage segment.
- Entrypoints keep `/reprospec:*` as the canonical written form for every stage
  command, including the `Next` command in each `Completion Report`.

## Entrypoint Structure

Every `SKILL.md` uses this order:

```text
## User Input
## Pre-Execution Checks
## Goal
## Execution Steps
## References
## Decision Protocol      # only when user decisions are required
## Completion Report
## Operating Constraints
## Done When
```

Keep each section concise. Put detailed contracts, schemas, and edge cases in
the linked reference or asset instead of repeating them in the entrypoint.

### Non-Stage Skills

`feedback` is a utility skill, not one of the twelve stages. It uses the same
frontmatter and section skeleton, but its completion card starts with
`**ReproSpec | FEEDBACK**` (no stage number), it owns no stage gate, and its
`Next` block tells the user to resume the workflow rather than naming the next
stage. It additionally owns a consent decision protocol: no branch, commit,
push, pull request, or issue may be created before the user explicitly approves
the previewed content. Do not add stage numbering or stage gates to it.

## Section Rules

- `User Input`: explain how optional invocation arguments affect the stage.
- `Pre-Execution Checks`: list files, states, and previous stages that must
  exist. Every skill after `init` must explicitly verify the
  Init-established computation policy, the time-range selection and exact
  final-window confirmation state, and the unresolved data-decision gate.
- `Goal`: state the observable outcome, not implementation history.
- `Execution Steps`: use numbered, imperative steps.
- `References`: link only the files needed by the stage.
- `Decision Protocol`: define one-question-at-a-time interaction when required.
- `Completion Report`: preserve the shared stage status and result semantics
  while rendering the report using the display contract below.
- `Operating Constraints`: state hard boundaries and provenance requirements.
  Every skill after `init` must state that Init requirements are
  binding and cannot be bypassed.
- `Done When`: finish with a Markdown checkbox list.

## Terminal Display Contract

Terminal reports are rendered Markdown. Emit the final report directly rather
than wrapping the entire response in a fenced code block. Fenced examples in
skill entrypoints describe the required structure and are not literal output.

### Stage Completion Card

Start with a bold stage label in the form
`**ReproSpec <n>/12 | <STAGE>**`, followed immediately by `Status`. Keep the
existing `completed`, `partial`, and `blocked` values. Do not use H1, H2, or H3
headings in terminal output.

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

- `work/<paper-id>/master_spec.md`
- `work/<paper-id>/figures/F001/spec.md`

> **Next**
>
> `/reprospec:plan`
>
> **Reason:** All included figures now have detailed specifications.
```

Use a table when the stage has three or more comparable result values. Use
bullets for artifacts and short lists. Keep `Next` and `Reason` in the final
blockquote. For `partial` or `blocked`, keep the same card and update the
status, summary, next action, and reason.

Only include a gate when the stage owns one:

- `plan` and `analyse`: `**Integrity Gate:**`
- `deliver`: `**Delivery Gate:**`

Do not add gate fields to other stages.

### Decision Required Card

When user input blocks progress, emit a rendered Markdown decision card instead
of presenting the decision as unstructured prose.

```markdown
**Decision Required | Data Provenance**

**Context**

The source has no documented origin.

**Why This Blocks Progress**

The integrity gate cannot become `complete`.

**Recommended:** Option B - Acquisition evidence allows final alignment.

| Option | Answer | Implication |
| --- | --- | --- |
| A | Use the file as provided | Provenance remains unknown |
| B | Provide acquisition evidence | Allows final alignment |

You can reply with `A`, `B`, accept the recommendation by replying `yes` or
`recommended`, or provide your own answer.
```

Ask only the single question required by the stage, then wait. Keep status
labels, options, and evidence explicit so the card remains readable as plain
text.

For option-based questions, present a recommendation in the form
`**Recommended:** Option <letter> - <reason>` before the options table. After
the table, state that the user can reply with an option letter, accept the
recommendation by replying `yes` or `recommended`, or provide a custom answer.

For short-answer questions, present `**Suggested:** <answer> - <reason>` and
state that the user can accept it by replying `yes` or `suggested`, or provide
their own answer.

## Supporting Files

References begin with a purpose and their required inputs. Reusable output
templates begin with a title and an identity block. Tables use spaces around
cell contents and `| --- |` separators.

Generated artifacts remain English. Plot text uses English by default unless
the specification records an explicit language exception. Terminal reports
follow the user's language. Existing snake_case artifact paths remain stable
for compatibility.
