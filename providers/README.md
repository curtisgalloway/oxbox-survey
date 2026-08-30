<!--
SPDX-FileCopyrightText: 2026 Curtis Galloway
SPDX-License-Identifier: Apache-2.0
-->

# providers/

One living page per venue. What it costs to get in, what it takes to call a free
model, what shape its API is, and what it has actually done when probed.

Three directories, three different jobs, and keeping them apart is what stops
this repo from turning into a blog:

| Directory | Holds | Changes |
|---|---|---|
| `snapshots/<venue>/` | which models exist and what they cost | weekly, mechanically |
| `observations/` | one dated thing an agent saw, immutable once written | append-only |
| `providers/` | standing facts about the venue itself | edited in place when they change |

A provider page is the only document here that gets **edited rather than
appended**. That is deliberate: nobody wants to reconstruct "does ZenMux need a
deposit" by reading eight months of observations. When a standing fact changes,
change it, and cite the observation that proved it.

## Rules

- **Tier every claim inline.** `[M]` measured — someone ran it and the evidence
  is in `observations/`. `[R]` reported — docs, a blog, a support page. `[?]`
  unverified — believed, never tested. A page with no `[?]` markers is usually a
  page nobody looked hard at.
- **Date the verification.** `last_verified` in the frontmatter, and re-check
  before quoting a page in an issue. Rate limits and signup terms rot faster
  than anything else here.
- **Link the observation.** Any `[M]` claim names the file that proved it, so a
  reader can judge the evidence rather than trust the summary.
- **Never upgrade a tier without new evidence.** A `[R]` claim repeated
  confidently for six months is still `[R]`.

## At a glance

| Venue | Class | Gate on free models | API shape | Free models |
|---|---|---|---|---|
| [openrouter](openrouter.md) | A | account-wide prompt logging, for some `[R]` | `chat/completions` | 22 |
| [zenmux](zenmux.md) | A | **funded account required** `[M]` | `chat/completions` `[M]` | 8 |
| [requesty](requesty.md) | A | none; no card `[M]`/`[R]` | `chat/completions` `[M]` | 12 |
| [opencode](opencode.md) | B | **used funded** `[M]`; cardless untested `[?]` | `chat/completions` `[M]` | unknown — no pricing in catalog |

Class A means the catalog carries pricing, so `free` is Measured. Class B means
it does not, so `free` is `null` — unknown, never false.

**All four are reachable from oxbox** as of 2026-08-23: `ox --venue <name>`,
each reading its own key variable. Every one of them speaks
`chat/completions`, which was verified per venue rather than assumed. So the
`USE`-requires-a-run rule is no longer blocked by plumbing on any venue here —
what is missing now is review runs, not access.
