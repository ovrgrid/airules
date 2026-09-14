# LESSONS - what the network learned, harvested from every BUILDLOG

Each site's `BUILDLOG.md` records what happened *there*. This file holds the lessons that
turned out to be true **everywhere**, so the next session on any site pays for them once.

A lesson earns a place here when it meets one of two tests:
1. It caused, or would have caused, the same failure on more than one site.
2. It changed a rule in `RULES.md`. In that case the rule cites the lesson and the lesson
   cites the rule, so neither can quietly drift away from the other.

Format: date, one-line title, what happened, the root cause, the rule it produced. Newest
first. Append only; a lesson that stops being true gets a correcting entry, not a delete.

---

### 2026-09-14 - "Cannot" was a strategy preference wearing a law's clothes
The **OVRMARK** product board told Rhys that consent for pooled data cannot be obtained
retroactively, and leaned on that to make the ownership model the one decision that could
never be corrected later. He asked what actually stops a contract amendment plus a shared
access pathway from doing exactly that. Nothing does. Re-consent by amendment is ordinary
commercial practice, and he was right to refuse to put an impossibility on a board that
investors and customers will audit.
**Root cause:** a planning preference (settle ownership early) was written in the grammar of
a hard constraint, because the hard grammar made the recommendation sound more urgent. The
real constraint was one level down and had been stepped over: the permission is recoverable
by amendment, but the provenance recorded beside each row is not, so what has to be right
before the first row is written is the schema, not the signature. The narrower claim is also
the more useful one, because it names something a session can actually build.
**Produced:** R13. And a habit: when a claim of impossibility collapses, go one level down
and find the true constraint rather than quietly deleting the sentence.

### 2026-08-31 - A rule that lists files leaks into chat
The em-dash ban had been in force since 2026-08-22 and kept failing anyway. Two causes,
both structural, neither about effort. First, the rule existed in exactly one repo's
`CLAUDE.md` (**NTHSKY**) and had never been written into the other four, so four out of
five sessions had never read it. Second, its wording enumerated artifacts ("not in site
copy, not in BUILDLOG, not in commits"), so a session reading it correctly concluded that
conversation was out of scope.
**Root cause:** a rule stored in one place is not a network rule, it is a local habit. And
a rule that enumerates surfaces is read as excluding the surfaces it forgot to name.
**Produced:** R2, which names chat replies first, and this repo, which exists so that
"written into one place" and "in force everywhere" are the same act.

### 2026-08-31 - Shipped correct in the worker, wrong on the screen
A new role (`admin_dev`) went out with the API and D1 both right. Every probe passed. The
admin SPA had never learned the role string, so the dropdown fell back to the lowest option
and would have demoted the user on the next save. The owner found it in a screenshot.
**Root cause:** the role ladder is stored in two places, `src/worker.js` and
`public/index.html`, and I verified the half I had edited. Passing probes proved only that
the half I had looked at worked.
**Produced:** R7. Verify on the screen the user actually touches. When a value is enumerated
in more than one file, changing one of them is not a change, it is a split brain.

### 2026-08-31 - Order code before data when changing a role ladder
Applying a new role value to live D1 before the worker that understands it is deployed
leaves that user resolving to rank 0. On an auth system that fails closed, that locks them
out of their own account.
**Root cause:** an unknown role string has no safe default; "least privilege" and "do not
break the user" point opposite directions.
**Produced:** deploy the code that understands a value, then write the value. Never the
reverse.

### 2026-08-31 - A literal grep cannot see an escaped character
The em-dash sweep reported clean while three em dashes sat inside JS string literals in
their backslash-u-2014 escaped form, in the text the hub assistant reads out to users. The
purge was measured with a grep for the character itself.
**Root cause:** the audit tool and the artifact spoke different encodings.
**Produced:** R2's escaped-form warning. More generally: when you sweep for a character,
sweep for its escapes too, and state which forms you checked.

### 2026-08-23 - Status tables go stale faster than the systems they describe
A brand-conformance row said ovrops was correct; a later sweep read a working branch still
holding the old palette and reported the standard broken. Both were true at once.
**Root cause:** a doc row records a moment, and branches make several moments true
simultaneously.
**Produced:** verify status by probe against `main`, never by reading the table that claims
it. Tables are an index of what to check, not evidence.

### 2026-08-12 - A bug fixed once is a bug class everywhere
**ovrops** fixed an 🔑 SSO callback that referenced an element a sidebar restyle had
removed. It threw on the first line and killed the callback before the fetch, so sign-in
silently did nothing. Checking siblings found **OVR3D**'s denied path making seven
unguarded DOM calls: safe that day, one redesign away from the identical silent failure.
**Root cause:** the sites share ported code, so they share latent bugs, and nobody looks at
a sibling's fix unless the process makes them.
**Produced:** R10, and check 8 of the 🛰 network check.

### Standing - a hardcoded value outside the token block is the drift
An **OVR3D** palette sweep found around 50 hex values sitting outside the `:root` blocks.
Five of six surfaces already had a token block and all five had drifted anyway, because the
block was a suggestion the rest of the file was free to ignore. The stale *spec* in a
`.md` file was worse than the stale stylesheet: it would have re-created the drift through
the next session.
**Root cause:** a canonical block only means something if nothing is allowed to bypass it.
**Produced:** grep, do not read, when you claim a sweep is complete. And grep the docs too:
a stale spec outlives a stale implementation.
