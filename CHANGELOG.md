# CHANGELOG - every rule change, dated, with who decided it

A rule with no decision behind it is a preference somebody typed. Each row says who chose
it, so a future session can tell an owner call from an inherited habit and knows which one
it may argue with.

| Version | Date | Decided by | Change |
|---|---|---|---|
| v1.3 | 2026-09-27 | Rhys | **R15 added: one library, the same rules as tasks, for files.** Owner call, in his words: "The project library should be the library - but just as the same with Tasks - the library should have chain of custody that shows up based on who has access to what and what their role is etc. Same concept of chain of custody and all that. If I add a team member to a project or team, theyd get access to that team library unless one of the team leaders uploads somwthing that is only for a role or above." Written the same day as R14, after a build document was filed on a drive folder and linked from a page because the hub's library had no project sections to hold it. The contract lives in the hub's `docs/LIBRARY-STANDARD.md`. |
| v1.2 | 2026-09-27 | Rhys | **R14 added: one task system.** Owner call, in his words: "The tasks should probably be managed at the hub level but full functionality on the page - just a tab/filter/pages section in the admin side, as well as has those tasks available for users in their profile. Full functionality and proper chain of custody/routing/management and managed with settings filter able etc. ... all tasks should fit that same profile. Capable of being sectioned off but always managed the same." And: "A task not managed is a task lost on a random page." Written the day a private working side was about to get its own Tasks tab, when the hub already carried several task shapes (the admin build board, each Builder build's board, per-person tasks, team tasks) plus each spoke's own board. The profile itself lives in the hub's `docs/TASK-STANDARD.md`. |
| v1.1 | 2026-09-23 | Rhys | **R13 added: every switch ships with its control on an admin screen.** Owner call, in his words: "Do not ever make code that is a toggle or trigger for something without connecting it to a setting and/or toggle inside an admin page. I keep on having to come up with my own acknowledgement that there should be settings toggles, but it isn't created naturally." Written after a network audit the same day found the pattern in every repo: switches set only by SQL or a wrangler var (the hub's site registry and build-session tokens, **ovrops**' sheet-sync pause, **OVRFLIGHT**'s signup switch), and, worse, controls that save but do nothing (**OVRFLIGHT**'s flight-visibility selector, **TeamTrain**'s AI-builder toggle, the hub's organization settings). The "saves but does nothing" clause comes from that second group. |
| v1.0 | 2026-08-31 | Rhys | Repo created. R1 to R10 gathered from the five `CLAUDE.md` files and the hub standards, deduplicated into one canonical block, and wired to sync into every repo. Two rules are new rather than gathered: **R2's four signals** (owner call, 2026-08-31, so a table name and a site are not formatted identically) and **R7's screen clause** (from the `admin_dev` incident the same day). R2's em-dash ban is unchanged in substance since 2026-08-22 but restated to cover chat replies, which is why it had been failing. |

## How to add a row

Bump the version in the `AIRULES:START` marker in `RULES.md` in the same commit as the rule
change, add the row here, and say who decided it. "Decided by" is Rhys for owner calls and
the session name for anything a session proposed and the owner merged. If nobody decided it,
it is not a rule yet.
