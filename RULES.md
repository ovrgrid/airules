# AIRULES - the network operating ruleset

**Version 1.1 - 2026-09-14.** Owner: Rhys Andersen. This file is the single source of the
rules every Claude session follows on every ovrgrid site. It is not documentation about the
rules. It IS the rules: the block between the markers below is copied verbatim into every
repo's `CLAUDE.md` by the sync, so a session reads it before it does anything.

Nothing here is site-specific. Site-specific facts (architecture, deploy targets, bindings,
layout) stay in each repo's own `CLAUDE.md` and `INFRASTRUCTURE.md`, outside the markers.

Change the rules here and nowhere else. Editing a synced block inside a product repo is a
change that the next sync deletes.

---

<!-- AIRULES:START v1.1 -->
## Network rules (synced from `ovrgrid/airules` - do not edit here)

These come from `RULES.md` in `ovrgrid/airules` and are identical in every ovrgrid repo.
If a rule below is wrong, fix it there, not in this file: the sync overwrites this block.

### R1. Secrets - the one unbreakable rule
Never put a secret value in any file in any repo. Credential *names* and *locations* only.
Real values live in Cloudflare Worker secrets, GitHub Actions secrets, and the owner's
password manager. This applies to code, docs, `INFRASTRUCTURE.md`, commits, and anything
you paste into chat. If you find a live secret committed anywhere, stop and say so rather
than quietly rotating around it.

### R2. Writing style - applies to CHAT REPLIES as much as to files
Everything you write is covered: what you say to Rhys in conversation, site copy, UI
strings, docs, `BUILDLOG.md` and `INFRASTRUCTURE.md` entries, code comments, commit
messages, PR bodies, and anything an in-app assistant generates.

**No em dashes, anywhere** (owner call, 2026-08-22). Use " - ", a comma, a colon, or a
period. The whole network was swept clean of them; do not reintroduce any. This includes
your replies in chat, which is where they slip back in most often: the first version of
this rule listed only files, so sessions read it as an artifact rule and let conversation
slide. Watch for the escaped form too, a backslash-u-2014 sequence inside a JS string: a
literal grep will not catch it, and it renders as a real em dash to the reader. Every AI
surface carries it as a system-prompt style rule (`NO_EM_DASH` in each worker). Standing
exception: `docs/infra-versions/` snapshots are frozen and never edited.

**Four signals, so the reader can tell categories apart at a glance** (owner call,
2026-08-31). When a table name and a company are formatted identically, the reader cannot
tell what is doing what to what. Terminal markdown has no colour, so use contrast:

| Signal | Means | Example |
|---|---|---|
| `backticks` | a literal string, greppable: table, column, role value, file, endpoint, command | `build_messages`, `admin_dev`, `src/worker.js`, `/api/nthsky/tasks` |
| **bold** | a site or product | **ovrops**, **NTHSKY**, **OVR3D**, **OVRFLIGHT**, **TeamTrain** |
| emoji + name | a system or process | 🛠 the build bridge, 🛰 the network check, 🔑 SSO, 🕸 federation |
| plain text | people, concepts, everything else | Mark, the dev host, access, the roadmap |

The test for backticks is one question: could the reader copy this and find it? If not, it
is not code. Bold is reserved for sites so it stays meaningful; do not spend it on general
emphasis. Keep the emoji set small and fixed, because inventing one per sentence turns a
signal back into decoration. When a site name genuinely appears as stored data, say so in
words ("the site slug stored as ovrops") rather than making formatting carry the difference.

### R3. Keep `INFRASTRUCTURE.md` current
When you change infrastructure (Worker, schema, bindings, vars, secrets, routes, domains,
deploy), update the relevant section in the same change. Bump the version and date at the
top, add a Changelog row, update the status tags (✅ live / 🟡 in progress / ⬜ planned).
If reality and that file disagree, flag the conflict; do not silently assume.

### R4. Append to `BUILDLOG.md` on every meaningful drop
What shipped, why, any incident plus root cause, the lesson. In the same commit as the
work. `INFRASTRUCTURE.md` says what the system IS; `BUILDLOG.md` says what HAPPENED and
what we learned. It is the network's long-term memory: a lesson that is not written down
gets re-learned by the next session at full price.

### R5. Do not rewrite working systems to "improve" them
Prefer the smallest change that solves the task. Ask before large refactors.

### R6. Change workflow - review-first for anything that matters
Pushing to `main` auto-deploys to live on every site. So gate by size:
- **Small / low-risk** (copy, styling, a bug fix, doc updates): commit straight to `main`.
- **Big / risky** (noticeable UI changes, API changes, D1 schema changes, auth, anything
  that could disrupt someone mid-session): branch plus PR. Rhys reviews and picks the
  go-live moment by merging.
- When unsure which bucket a change falls in, treat it as big and use a branch plus PR.

Schema changes are applied manually and never by a deploy, so a push cannot wipe live data.

### R7. "Done" = shipped AND verified
Check the Actions run is green after every push to `main`, then probe the live surface. A
merged commit with a red deploy is not done. **Verify on the screen the user actually
touches**, not only the API and the database: on 2026-08-31 a role shipped correct in the
worker and in D1 while the admin dropdown had never learned it, and the owner found it in a
screenshot. Passing probes proved the half I had looked at.

### R8. Version lanes - so parallel sessions never collide
Version numbers carry a lane letter: `a` multi-site, `n` **NTHSKY**, `o` **ovrops**,
`d` **OVR3D**, `f` **OVRFLIGHT**, `t` **TeamTrain**. The same number in two lanes is two
versions, not a conflict. Resolve changelog collisions by union: keep both rows.

### R9. Commit style
Short, imperative commit messages. When an AI makes the commit, add the trailer with the
model that actually did the work:

```
Co-Authored-By: Claude <model> <noreply@anthropic.com>
```

Never put a model identifier anywhere else in a pushed artifact: not in PR titles or
bodies, not in code comments, not in site copy.

### R10. Reuse before rebuild
Platform machinery already exists somewhere in the network (auth, invites, vault, push,
E2E harness, nightly ops, federation). Port it, do not reinvent it. A bug fixed once is a
bug class everywhere: when you fix one, check whether the sibling sites share it.

### R11. KAMERA - the test every proposed change is judged against
**K**eep it simple, **A**dapt to current tech, **M**odernize and maintain, **E**fficient
for the user, **R**ealistically viable, **A**wesome experience. Build it if it satisfies
these, or at least opposes none. User suggestions flow through the in-app KAMERA queue
where a site has one: AI-assessed, admin-decided.

### R12. Who you are writing for
The owner (Rhys) is technical-adjacent: comfortable with APIs, datasets and AI-assisted
development, not a hand-coder. Explain what a change does and why in plain terms, give the
exact steps to deploy or test it, and do not assume framework knowledge. Say what you
actually did and what you did not do. If a check failed, show the output rather than
summarising it away.

### R13. An impossibility has to name its mechanism
A reader tests the strongest claim on the page first, so "cannot be done" has to survive
being tested. Before writing that something is impossible, irreversible or permanent, name
the thing that makes it so: a law, a signed agreement, a physical limit, a documented vendor
cap. If you cannot name one, it is not impossible, it is expensive. Write it as a cost with
a rough size, and say what paying that cost buys back. The two errors are not the same size:
a limit understated gets corrected in review, while a limit overstated gets corrected by an
investor or a customer in front of everyone, and it puts every other claim beside it in
doubt. This binds hardest on investor and customer material, where the claims are
load-bearing, and it applies to chat replies like every other rule here. When a claim of
impossibility does collapse, the true constraint is usually one level down and more useful
than the false one, so go and find it rather than just deleting the sentence. See the
2026-09-14 entry in `LESSONS.md`.
<!-- AIRULES:END -->

---

## How this reaches every site

A session only reads files on disk in the repo it opened. There is no remote import, so the
block above has to physically land in each repo or nothing reads it. `.github/workflows/
sync-rules.yml` in this repo does that: on a push to `main` here, and weekly, it opens a
docs-only PR in every consumer repo replacing everything between the two markers. Repos
that already match are skipped.

Consumers are listed in `sync/consumers.json`. Adding a site to the network means adding
one line there, not writing its rules again.

## What lives here and what does not

| Here | Not here |
|---|---|
| Rules every session follows (`RULES.md`) | Any site's architecture or bindings |
| Cross-site lessons (`LESSONS.md`) | Any secret value, ever (R1 applies to this repo) |
| The audit protocol (`REVIEW.md`) | A site's own `INFRASTRUCTURE.md` |
| The rule changelog (`CHANGELOG.md`) | Anything that deploys |

This repo has no Worker, no D1, no domain and no deploy. It cannot break a site by being
wrong at runtime, only by being wrong on purpose.
