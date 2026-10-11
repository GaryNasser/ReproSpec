# Feedback Rules

Purpose: define how the feedback skill verifies GitHub CLI availability,
resolves its target repository, maps categories to labels, scrubs private
information, obtains consent, names its issue, and publishes it. Required
inputs: the invocation arguments, the current session context, and an
installed, authenticated `gh` CLI. `git` is not required.

## GitHub CLI Requirement

The feedback skill requires the GitHub CLI. Verify before drafting:

| Check | Command | Requirement |
| --- | --- | --- |
| gh installed | `gh --version` | exits 0 |
| gh authenticated | `gh auth status` | logged in |
| target exists | `gh repo view <owner/repo>` | exits 0 |
| issues enabled | `gh repo view <owner/repo> --json hasIssuesEnabled --jq .hasIssuesEnabled` | `true` |

No push permission is needed: any authenticated account may open an issue on a
public repository.

### Unavailability Notice

If `gh` is missing or unauthenticated, the feedback skill cannot be used.
Notify the user with rendered Markdown, create nothing, draft nothing, and
stop with a `blocked` card. Use this structure:

```markdown
**ReproSpec | FEEDBACK**

**Status:** `blocked`

**Reason:** The feedback skill requires the GitHub CLI (`gh`), which is
<not installed / not authenticated>. Feedback cannot be used until it is
ready.

**To enable feedback**

1. Install the GitHub CLI: https://cli.github.com/
2. Run `gh auth login` and complete the browser sign-in.
3. Re-run `/reprospec:feedback`.
```

Never substitute a branch, commit, pull request, file-based workflow, or any
other fallback for the missing CLI. Never proceed partially.

## Target Repository Resolution

Resolve exactly one target repository in this order and display the result
before drafting:

1. A `repo:<owner>/<repo>` invocation argument.
2. The `origin` remote of the directory that contains this `SKILL.md`, when
   that directory holds `.claude-plugin/plugin.json`.
3. The `origin` remote of the current working directory, when it holds
   `.claude-plugin/plugin.json`.
4. The default `GaryNasser/ReproSpec`.

The resolved `owner/repo` appears verbatim on the consent card. If resolution
yields a repository the user did not expect, stop and ask which repository is
correct before drafting.

## Issue Conventions

Feedback issues follow the repository's community-facing conventions:

- Title: `[<Category>] <short problem title>`, for example
  `[Usability] Consent card does not show the commit message`.
- Category and labels: derive labels from the category, using only labels that
  already exist in the target repository. Never create labels.

  | Category | Preferred labels (first existing one wins) |
  | --- | --- |
  | bug | `bug` |
  | usability | `enhancement`, then `bug` |
  | documentation | `documentation` |
  | data issue | `bug` |
  | feature request | `enhancement` |

- Body: use
  `assets/feedback-issue-template.md`, which mirrors the repository's
  `.github/ISSUE_TEMPLATE/feedback.yml` form: summary, environment, steps to
  reproduce, expected versus actual, privacy statement, and additional
  context. Keep every heading, and fill every field; write `not applicable`
  rather than deleting a section.
- One problem per issue. Never bundle unrelated findings.
- Issue text is English regardless of the terminal language.

## Privacy Scrub Checklist

Apply every category to the draft before the consent card. Replace matched
content rather than deleting surrounding text, so the issue stays readable.

| Category | Example | Required action |
| --- | --- | --- |
| Credentials and tokens | `ghp_...`, `github_pat_...`, `sk-...`, `AKIA...`, `xoxb-...`, `Bearer ...`, `password=...`, `api_key=...` | Remove the value entirely; keep only the field name and `<REDACTED>` |
| Email addresses | `name@example.com` | Replace with `<REDACTED_EMAIL>` |
| Personal paths | `C:\Users\<name>\...`, `/home/<name>/...`, `/Users/<name>/...` | Replace only the user segment with `<USER>`; repository-relative paths stay |
| Hosts and internal URLs | private hostnames, LAN IPs, non-public endpoints | Replace with `<REDACTED_HOST>` unless the URL is public documentation |
| Raw data rows | dataset samples, cell values, record contents | Keep aggregates only: row counts, schemas, value ranges; never row content |
| Paper excerpts | full paragraphs, tables, long quotes | At most one quote of 20 words or fewer, only to locate the issue |
| Personal identifiers | real names, institutions, employers | Remove unless essential to the problem; essential cases must appear on the consent card |
| Log output | full stack traces or console dumps | Quote only the minimal failing lines and scrub them like any other text |
| Binary content | images, PDFs, dataset files | Never attach; issues are Markdown text only |

Record every applied replacement in the issue's Privacy Statement table. When
a category cannot be resolved automatically, flag the item in the consent card
and recommend `revise` until the user resolves it or explicitly accepts the
flagged text in writing.

## Consent Semantics

- Approval answers: `A`, `submit`, `proceed`, or `yes`/`recommended` only when
  the card recommends Option A.
- Revision answers: `B`, `revise`, or any concrete change request. Re-scrub and
  present a new card.
- Cancellation answers: `C`, `cancel`, `no`.
- Any other answer, including silence or an ambiguous reply, is not approval.
  Re-prompt once with the same card; if still ambiguous, stop with a
  `cancelled` card.

No network or `gh` write may happen before an approval answer. Drafting is
local, in-memory content; do not leave draft files in the reproduction
workspace.

## Publication Procedure

Runs only after an approval answer:

1. Write the approved body to a temporary file in the system temp directory.
2. `gh issue create --repo <owner/repo> --title "<approved title>"
   --body-file <temp-file>` adding `--label <label>` once per approved label.
3. `gh issue view <number-or-url> --repo <owner/repo>` to verify the issue,
   then report its URL.
4. Delete the temporary body file.

Never create a branch, commit, push, pull request, or repository file. The
reproduction workspace and the plugin checkout are never modified.

## Failure Handling

- If `gh issue create` fails, stop immediately. Keep the temporary body file,
  report its path and the failing command's output, and emit a `blocked` card.
- Never retry with a different publication mechanism, and never open a branch
  or pull request as a workaround.
- If the issue is created but verification fails, report the attempted URL and
  the verification error; do not close, edit, or reopen it without approval.
