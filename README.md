# AIRULES

The operating brain of the ovrgrid network. One living ruleset that every Claude session on
every site reads, plus the lessons the network has actually paid for.

This repo has no Worker, no D1, no domain, no deploy. It ships text into other repos and
that is all it does.

## Why it is not part of the hub

**NTHSKY** is the network hub, and it was the obvious home. It is the wrong one, for a
reason that is easy to check: **TeamTrain** is deliberately outside 🕸 federation and
outside 🛠 the build bridge, and it still needs the em-dash rule. Rules apply to every site
regardless of whether that site talks to the hub at runtime, because rules are build-time
behaviour and federation is runtime data. Putting them in the hub would make the hub's own
product plumbing a dependency of how sessions write sentences.

The hub is a consumer of this repo, exactly like the spokes. It is the biggest feeder into
it and it lives by it, but it does not own it.

## The files

| File | What it is |
|---|---|
| `RULES.md` | **The rules.** The block between the markers is copied verbatim into every repo's `CLAUDE.md`. Change rules here and nowhere else. |
| `LESSONS.md` | What the network learned, harvested from every `BUILDLOG.md`. Append only. |
| `REVIEW.md` | The two loops that keep this honest: the automatic sync, and the owner-invoked rules review. |
| `CHANGELOG.md` | Every rule change, dated, with who decided it. |
| `sync/consumers.json` | Every repo that carries the block. Adding a site is one line. |
| `sync/apply_block.py` | Swaps the block in one file. Exits 1 if nothing changed, 2 if the markers are missing. |
| `.github/workflows/sync-rules.yml` | Fans the block out as docs-only PRs. |

## How a rule change travels

1. Edit `RULES.md`, bump the version in the `AIRULES:START` marker, add a `CHANGELOG.md`
   row saying who decided it and why.
2. Merge to `main`.
3. The sync opens a docs-only PR in every consumer whose block differs. Repos already
   matching are skipped, so a no-op change is silent.
4. Rhys merges them. Every session opened after that reads the new rule as its first
   instruction, because it is in the file the session loads before it does anything.

Step 3 is the whole reason this repo exists. A session only reads files on disk in the repo
it opened; there is no remote import. Text that stays here reaches nobody.

## Setup the owner does once

1. Create a fine-grained personal access token scoped to the five repos in
   `sync/consumers.json`, with **Contents: read and write** and **Pull requests: read and
   write**. No other permissions.
2. Add it to this repo as the secret `AIRULES_SYNC_TOKEN` (Settings, Secrets and variables,
   Actions). It lives only here: push-based sync means one token in one place instead of
   five repos each holding a read token for this one.
3. Confirm each consumer's `CLAUDE.md` has the `AIRULES:START` and `AIRULES:END` markers.
   Where they go is a one-time human decision; after that the sync owns everything between
   them.

The token is a GitHub secret and never appears in this repo. `RULES.md` R1 applies here
like everywhere else.

## The one rule about this repo

Do not edit a synced block inside a product repo. The next sync deletes it, silently, and
the change looks like it was never made. If a rule is wrong, it is wrong here.
