# CHANGELOG - every rule change, dated, with who decided it

A rule with no decision behind it is a preference somebody typed. Each row says who chose
it, so a future session can tell an owner call from an inherited habit and knows which one
it may argue with.

| Version | Date | Decided by | Change |
|---|---|---|---|
| v1.1 | 2026-09-23 | Rhys | **R13 added: every switch ships with its control on an admin screen.** Owner call, in his words: "Do not ever make code that is a toggle or trigger for something without connecting it to a setting and/or toggle inside an admin page. I keep on having to come up with my own acknowledgement that there should be settings toggles, but it isn't created naturally." Written after a network audit the same day found the pattern in every repo: switches set only by SQL or a wrangler var (the hub's site registry and build-session tokens, **ovrops**' sheet-sync pause, **OVRFLIGHT**'s signup switch), and, worse, controls that save but do nothing (**OVRFLIGHT**'s flight-visibility selector, **TeamTrain**'s AI-builder toggle, the hub's organization settings). The "saves but does nothing" clause comes from that second group. |
| v1.0 | 2026-08-31 | Rhys | Repo created. R1 to R10 gathered from the five `CLAUDE.md` files and the hub standards, deduplicated into one canonical block, and wired to sync into every repo. Two rules are new rather than gathered: **R2's four signals** (owner call, 2026-08-31, so a table name and a site are not formatted identically) and **R7's screen clause** (from the `admin_dev` incident the same day). R2's em-dash ban is unchanged in substance since 2026-08-22 but restated to cover chat replies, which is why it had been failing. |

## How to add a row

Bump the version in the `AIRULES:START` marker in `RULES.md` in the same commit as the rule
change, add the row here, and say who decided it. "Decided by" is Rhys for owner calls and
the session name for anything a session proposed and the owner merged. If nobody decided it,
it is not a rule yet.
