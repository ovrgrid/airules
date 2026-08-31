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

## Automating loop 2 (not built, deliberately)

A scheduled Action could run a session against this protocol on its own. It needs an
Anthropic API key in this repo's secrets and a decision from the owner about whether an
unattended session may open PRs across five repos. Until that decision is made, loop 2 is
owner-invoked and this paragraph stays here as the open question, not as a plan.
