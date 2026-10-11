---
name: "feedback"
description: "Turn a problem encountered while using ReproSpec into a GitHub issue on the ReproSpec repository. Drafts the issue locally, scrubs private information, shows the verbatim title, labels, and body, and requires the user's explicit permission before the issue is created. Never creates a branch, commit, push, or pull request. When the GitHub CLI is missing or unauthenticated, tell the user that the feedback skill cannot be used and stop. Use only when the user actively asks to report reproduction feedback, including right after a stage reports a problem. Never use it to modify the reproduction workspace or to run workflow stages."
disable-model-invocation: true
metadata:
  author: "ReproSpec contributors"
  version: "0.1.0"
---

## User Input

Invocation arguments are optional scope guidance. They may state the problem
topic, the affected stage or figure, and an optional `repo:<owner>/<repo>`
override for the target repository. With no arguments, derive candidate
problems from the current session and confirm exactly one topic with the user
before drafting.

## Pre-Execution Checks

- `gh` is installed and authenticated (`gh --version`, `gh auth status`).
  When either check fails, the feedback skill is unavailable: notify the user
  with the exact install and login instructions from the reference and stop.
  Do not draft, do not create files, and do not fall back to any manual
  submission path.
- The target repository resolves to one `owner/repo` and accepts issues. Show
  the resolved target to the user.
- `git`, branches, commits, pushes, and pull requests are never used. The
  skill publishes exactly one issue and nothing else.
- The user has been told the privacy model before any drafting begins:
  everything is prepared locally, and nothing leaves the machine until the
  consent card is explicitly approved.

## Goal

Produce exactly one privacy-scrubbed feedback issue about exactly one
reproduction problem and publish it on the ReproSpec repository with
community-conventional structure, only after the user has seen the complete
content and explicitly approved it. Cancellation or ambiguity must always be
safe: no issue may exist after an unapproved run. When the GitHub CLI is
unavailable, the skill says plainly that feedback cannot be used yet and what
to install.

## Execution Steps

1. State the privacy model in the user's language before drafting: the issue
   is prepared locally, the consent card shows the final content verbatim, and
   no GitHub write happens before an explicit approval.
2. Verify the preconditions: `gh --version`, `gh auth status`, and target
   reachability with issues enabled. If any check fails, notify the user that
   the feedback skill cannot be used without a working, authenticated GitHub
   CLI, give the exact installation and `gh auth login` commands from the
   reference, and stop with a `blocked` card. Do not draft anything.
3. Resolve the target repository using the resolution order in
   [references/feedback-rules.md](references/feedback-rules.md), list its
   available labels, and display the resolved `owner/repo`.
4. Determine the topic. Use the invocation arguments when present; otherwise
   list the candidate problems observed in this session as one selection
   question and wait for the user's answer.
5. Collect the issue context read-only from session artifacts: affected stage,
   paper ID, environment and tool versions, expected behavior, and actual
   behavior. Never copy raw dataset rows or long excerpts from the paper.
6. Draft the issue with the community-conventional structure in
   [assets/feedback-issue-template.md](assets/feedback-issue-template.md):
   `[<Category>] <short problem title>`, category-derived labels from the
   target repository's existing label set, and the standard body sections.
7. Scrub the draft against every category in the privacy checklist in
   [references/feedback-rules.md](references/feedback-rules.md). Record each
   applied redaction in the body's Privacy Statement section.
8. Present the consent card from the Decision Protocol with the complete
   verbatim issue title, labels, and body. Then wait.
9. If the user answers `revise`, apply the requested changes, re-scrub, and
   present the card again. If the user answers `cancel`, stop and emit a
   `cancelled` card. No issue may be created before `submit`.
10. On `submit`, write the approved body to a temporary file in the system
    temp directory and publish the issue with `gh issue create --repo
    <owner/repo> --title "<approved title>" --body-file <temp-file>`,
    adding only the approved labels. Delete the temporary file afterwards.
11. Verify the issue with `gh issue view`, report its URL, and emit the
    completion card. If issue creation fails, stop, keep the temporary body
    file, report its path, and emit a `blocked` card with the failing
    command's output. Never open a branch, commit, push, or pull request as a
    workaround.

## References

- [references/feedback-rules.md](references/feedback-rules.md): GitHub CLI
  requirements and the unavailability notice, repository resolution, label
  mapping, privacy scrub checklist, consent semantics, and issue conventions.
- [assets/feedback-issue-template.md](assets/feedback-issue-template.md):
  the required issue body structure.

## Decision Protocol

### Issue Submission

Present the consent card as rendered Markdown outside a code fence, using a
`**Decision Required | Feedback Submission**` label. Show the resolved target
repository, the redaction count, and then the exact values the user is
approving: issue title, labels, and the full verbatim issue body. State that
nothing has been published yet.

```markdown
**Decision Required | Feedback Submission**

**Context**

The issue is drafted and scrubbed. Nothing has been published yet.

**Why This Blocks Progress**

A published issue is public and its content is irreversible.

**Recommended:** Option A - all scrub categories passed with no unresolved
items.

| Option | Answer | Implication |
| --- | --- | --- |
| A | `submit` | Create the issue with the approved title, labels, and body |
| B | `revise` | Change the issue locally and show a new preview |
| C | `cancel` | Stop; no issue is created |

You can reply with `A`, `submit`, accept the recommendation by replying `yes`
or `recommended`, reply `B` or `revise` with your changes, or reply `C` or
`cancel` to stop.
```

Give an `Option A` recommendation only when every scrub category passed and no
flagged item remains; otherwise recommend `Option B` and list the flagged
items above the table. Ask exactly one question and wait. Treat anything that
is not an explicit approval as no approval: silence, ambiguity, or a partial
answer must trigger a re-prompt or a cancellation, never a publication.

## Completion Report

Emit the report as rendered Markdown in the user's language. Do not wrap the
entire response in a code fence. Issue content remains English. Feedback is
not a workflow stage, so the card carries no stage number and no stage gate.

```markdown
**ReproSpec | FEEDBACK**

**Status:** `completed`

**Summary**

| Item | Result |
| --- | --- |
| Target repository | `<owner/repo>` |
| Issue | `<url>` |
| Issue title | `[<Category>] <short problem title>` |
| Labels | `<label list or "none">` |
| Redactions applied | `<count>` |

> **Next**
>
> Continue the workflow from the stage you were running.
>
> **Reason:** The feedback issue is open; the reproduction workflow is
> unchanged.
```

Use `Status: blocked` with the unavailability notice when the GitHub CLI is
missing or unauthenticated: state plainly that the feedback skill cannot be
used until `gh` is installed and logged in, list the exact commands, create
nothing, and do not identify a `Next` workflow action beyond re-running
`/reprospec:feedback` after installation. Use `Status: cancelled` when the
user declined approval and report that no issue was created. Use
`Status: blocked` also for a failed publication step, name the failing
command, and give the exact next action.

## Operating Constraints

- Verify the GitHub CLI before drafting. If it is missing or unauthenticated,
  tell the user that the feedback skill cannot be used and stop; never draft,
  never publish, and never invent a manual or local submission fallback.
- Never create a branch, commit, push, pull request, or any repository file.
  The only artifact is one GitHub issue; never fall back to a pull-request or
  file-based workflow.
- State the privacy model before drafting, and obtain explicit approval on the
  consent card before publishing. This is a hard gate, not a guideline.
- Treat anything other than an explicit approval answer as no approval.
  Ambiguity, silence, or a partial answer must never trigger a publication.
- Show the verbatim final content in the consent card. Never present a
  summarized or paraphrased preview of what will be published.
- Never publish secrets, credentials, tokens, personal identifiers, raw
  dataset rows, or long excerpts from a paper. Apply every scrub category in
  the reference and record each applied redaction in the issue body.
- Use only labels that already exist in the target repository, and only the
  ones shown in the consent card.
- Keep the scope fixed: one problem, one issue per approval.
- Use exactly the approved title and body; never rewrite them after approval.
- The only file this skill writes is the temporary body file in the system
  temp directory, deleted after publication. Never modify the reproduction
  workspace or the installed plugin checkout.
- Issue content is English. Terminal reports follow the user's language.

## Done When

- [ ] The GitHub CLI was verified before drafting; when it was unavailable,
      the user was told the feedback skill cannot be used and nothing was
      created.
- [ ] The privacy model was stated before drafting.
- [ ] The issue body passed the scrub checklist and every redaction is
      recorded in its Privacy Statement.
- [ ] The consent card showed the verbatim title, labels, and body.
- [ ] Explicit approval was received before the issue was created; an
      ambiguous or declined answer produced no issue.
- [ ] Exactly one issue exists and its URL is reported, or a truthful
      `cancelled`/`blocked` card is reported instead.
- [ ] No branch, commit, push, or pull request was created, and the temporary
      body file was removed.
