# REVIEW - how this repo keeps itself, and everything else, honest

The point of a rules repo is not that the rules are written down. It is that something
keeps checking whether they are true. This file is that protocol.

There are two loops. One is cheap and runs on a machine. One is expensive and needs a
session with judgement. Do not confuse them: the cheap loop proves the text matches, the
expensive loop proves the text is right.

## Loop 1 - the sync (automatic, no judgement)

`.github/workflows/sync-rules.yml` runs on every push to `RULES.md` and weekly. It proves
one thing: every consumer repo carries byte-identical rules. It cannot tell whether a rule
is good, only whether it arrived. A consumer that has drifted gets a docs-only PR; a
consumer whose markers are missing gets reported, because adding markers to a file for the
first time is a decision about where they go, not a text substitution.

Green sync means the rules are *deployed*. It does not mean they are *followed*.

## Loop 2 - the rules review (a session, monthly or on request)

Run when the owner says "rules review", or when a sync has been green for a month and
nobody has looked. It is read-only until the owner says otherwise, same as the 🛰 network
check. Its output is proposed changes to `RULES.md` and `LESSONS.md`, as a PR, never a
direct push.

Read, in this order:

1. **Every `BUILDLOG.md` since the last review.** Incidents are the raw material. For each
   incident ask the two questions from `LESSONS.md`: could this have happened on another
   site, and does an existing rule already cover it? An incident that an existing rule
   covered is more interesting than a new one, because it means the rule is not reaching
   the session that needed it. That is a distribution failure, not a knowledge gap, and it
   is fixed here, not by writing the rule again harder.

2. **Every merged PR since the last review, against the rules.** Not for correctness, for
   compliance. Did big changes go through review, or did something risky land straight on
   `main` (R6)? Did infra changes bump `INFRASTRUCTURE.md` in the same commit (R3)? Did
   meaningful drops append to `BUILDLOG.md` (R4)? Count the misses. A rule that is missed
   often is either wrong, unclear, or unreachable, and all three are this repo's problem.

3. **Every repo's `CLAUDE.md`, outside the markers.** The synced block is guaranteed. The
   rest is where duplication creeps back: a site restating a network rule in its own words
   is the exact failure that produced this repo, because the two copies then drift and both
   look authoritative. Move anything genuinely network-wide inside the markers, and delete
   the restatement rather than "keeping them in sync".

4. **The rules themselves, for rules nobody needs.** A ruleset that only grows stops being
   read. If a rule has produced no correction and no incident in six months, propose
   retiring it and say what evidence would bring it back.

## What a review produces

- A PR to this repo: `RULES.md` edits, new `LESSONS.md` entries, a `CHANGELOG.md` row.
- A short report in chat: rules added, rules retired, compliance misses by site with the
  evidence that settles each one (commit hash, PR number, run id), and any distribution
  failure found in step 1.
- Nothing else. The review does not fix the sites. It fixes the rules, and the sites get
  fixed by the sessions that read them.

## The honesty rule for this repo

This repo has no runtime, so it cannot fail loudly. It fails by being confidently stale:
rules that describe a network that no longer exists, lessons whose root cause was wrong.
The only defence is that every claim here names its evidence. If an entry cannot cite a
commit, an incident, or an owner decision, it is an opinion, and it does not go in.

## The schedule

Two jobs, an hour apart, on Saturday mornings Phoenix time. Arizona does not observe DST,
so UTC-7 holds all year and neither cron drifts twice a season.

| When | Job | Needs | Does |
|---|---|---|---|
| Sat 03:00 | `gather.yml` | `AIRULES_SYNC_TOKEN` | Clones all five repos, collects facts, commits `reviews/<date>/evidence.json`. No AI, no judgement, no writes to any site. |
| Sat 04:00 | `review.yml` | the three below | Reads that evidence, decides what it means, opens a proposal PR here, files evidenced tasks on the spoke boards, posts one summary to the build bridge. |

The hour between them is load-bearing, not padding. The evidence has to be committed
before the analysis reads it; and when the analysis breaks, is switched off, or is simply
not worth paying for that week, the record still exists and the analysis can be re-run
alone without re-gathering. Keeping the cheap half independent of the expensive half is
the whole reason they are two jobs.

The gather works from the day the repo exists, on the one secret the sync already needs.

## Arming loop 2

`review.yml` ships inert. With no `ANTHROPIC_API_KEY` it logs why and passes green, the
same way the rest of the network ships gated features unarmed. It never fails a workflow
for being unarmed, because a red cross every Saturday teaches everyone to ignore red
crosses.

Three secrets turn it on, all in this repo only:

| Secret | For | Without it |
|---|---|---|
| `ANTHROPIC_API_KEY` | the analysis itself | the whole job stays inert |
| `NTHSKY_FEDERATION_KEY` | filing tasks on spoke boards | findings stay in the PR, listed as not placed |
| `NTHSKY_BUILDER_TOKEN` | the summary on the build bridge | the summary stays in the PR |

They degrade independently and on purpose: a missing bridge token loses the notification,
not the review.

## What it can and cannot reach

Tasks can be filed on **ovrops**, **OVR3D** and **OVRFLIGHT**, which accept
`POST /api/nthsky/tasks` behind the shared federation key. **TeamTrain** exposes only the
GET, so it can be read and never assigned to; its findings appear in the proposal and the
summary, named as unplaceable rather than silently dropped. The hub's own board takes work
through the bridge.

## Why the analysis runs here and not in each repo

The obvious design is for this repo to push a weekly file out and let each site analyse
itself. It does not work, for one reason: the highest-value check is R10, does this bug
class exist on the siblings, and no repo can answer that about itself. A session inside
**ovrops** cannot see the fix that landed in **OVR3D**. So the analysis checks out all
five together and runs once, which also means one API key instead of five and one place to
change the prompt.

## The open decision

An unattended session now proposes rule changes and files tasks on live boards. It never
edits a site and never merges its own PR, which is the line drawn on purpose. Whether it
should ever be allowed past that line is the owner's call, and until it is made, this
paragraph stays here as the question rather than as a plan.
