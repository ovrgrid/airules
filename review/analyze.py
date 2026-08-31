#!/usr/bin/env python3
"""The analysis: read the week's evidence, decide what it means, write the results out.

Runs Saturdays at 04:00 Phoenix, one hour after the gather, and the gap is deliberate.
The gather must be committed before this reads it, and if this half fails or is turned
off, the evidence still exists and this can be re-run alone without re-gathering.

Ships INERT. With no ANTHROPIC_API_KEY it prints why and exits 0, the same way the
network's other gated features stay quiet until armed. It never fails a workflow for
being unarmed, because a red cross every Saturday teaches everyone to ignore red crosses.

Three outputs, in descending order of how sure we are:
  1. reviews/<date>/proposal.md      - proposed RULES/LESSONS edits, opened as a PR
  2. a task on each spoke's board    - only where the evidence names a specific fix
  3. one message on the build bridge - the summary a human actually reads

Usage: analyze.py <review dir containing evidence.json>
"""
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("AIRULES_MODEL", "claude-sonnet-5")
BRIDGE = "https://nthsky.ai/api/build-session"

# Where a task can actually be created. teamtrain exposes GET /api/nthsky/tasks only, so
# it can be read and never assigned to; its findings live in the proposal and the summary.
SPOKES = {
    "ovrops": "https://ovrops.com/api/nthsky/tasks",
    "ovr3d": "https://ovr3d.com/api/nthsky/tasks",
    "ovrflight": "https://ovrflight.org/api/nthsky/tasks",
}

SCHEMA = {
    "type": "object",
    "required": ["summary", "lessons", "rule_changes", "site_tasks"],
    "properties": {
        "summary": {"type": "string",
                    "description": "6 lines max, for a human on a phone. What changed, what drifted, what needs a decision."},
        "lessons": {"type": "array", "items": {
            "type": "object",
            "required": ["title", "what_happened", "root_cause", "rule"],
            "properties": {"title": {"type": "string"}, "what_happened": {"type": "string"},
                           "root_cause": {"type": "string"}, "rule": {"type": "string"}}}},
        "rule_changes": {"type": "array", "items": {
            "type": "object", "required": ["rule", "change", "why"],
            "properties": {"rule": {"type": "string"}, "change": {"type": "string"},
                           "why": {"type": "string"}}}},
        "site_tasks": {"type": "array", "items": {
            "type": "object", "required": ["site", "title", "details", "evidence"],
            "properties": {"site": {"type": "string"}, "title": {"type": "string"},
                           "details": {"type": "string"}, "evidence": {"type": "string"},
                           "priority": {"type": "integer"}}}},
    },
}

PROMPT = """You are running the weekly rules review for the ovrgrid network, defined in
REVIEW.md loop 2. You are reading evidence, not the repos themselves, so every claim you
make must be traceable to a field in the evidence below. If the evidence does not settle a
question, say so and propose no task: an unfounded task on someone's board costs more than
a gap in a report.

Judge against these rules (R1 to R12):
%s

This week's evidence:
%s

Four questions, in order:
1. Which rules were missed? A rule missed repeatedly is a DISTRIBUTION failure, not a
   knowledge gap, and the fix is in the rules repo, never "state the rule more firmly".
2. Which incidents in the BUILDLOG entries generalise to a sibling site? That is R10, and
   it is the check no single repo can run on itself.
3. Which rules have earned nothing in months and should be retired?
4. What specific, evidenced work belongs on a site's board?

Style rules apply to your own output: no em dashes anywhere, backticks only for strings a
reader could copy and find, bold only for site names.
"""


def post(url, payload, headers, what):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"content-type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        print("%s failed: HTTP %s %s" % (what, exc.code, exc.read()[:300]))
    except Exception as exc:
        print("%s failed: %s" % (what, exc))
    return None


def main():
    review_dir = sys.argv[1]
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ANTHROPIC_API_KEY is not set. The gather ran and its evidence is committed;")
        print("the analysis stays inert until the key is armed. This is not a failure.")
        return 0

    with open(os.path.join(review_dir, "evidence.json"), encoding="utf-8") as fh:
        evidence = fh.read()
    with open("RULES.md", encoding="utf-8") as fh:
        rules = fh.read()

    out = post(API, {
        "model": MODEL,
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": PROMPT % (rules, evidence)}],
        "tools": [{"name": "report", "description": "Return the review.",
                   "input_schema": SCHEMA}],
        "tool_choice": {"type": "tool", "name": "report"},
    }, {"x-api-key": key, "anthropic-version": "2023-06-01"}, "analysis")
    if not out:
        return 1

    review = next((b["input"] for b in out.get("content", []) if b.get("type") == "tool_use"), None)
    if not review:
        print("no structured output returned; leaving the evidence as the record")
        return 1

    with open(os.path.join(review_dir, "proposal.md"), "w", encoding="utf-8") as fh:
        fh.write(render(review))
    with open(os.path.join(review_dir, "review.json"), "w", encoding="utf-8") as fh:
        json.dump(review, fh, indent=2, sort_keys=True)

    fed = os.environ.get("NTHSKY_FEDERATION_KEY")
    placed, skipped = 0, []
    for task in review.get("site_tasks", []):
        url = SPOKES.get(task.get("site"))
        if not url or not fed:
            skipped.append("%s: %s" % (task.get("site"), task.get("title")))
            continue
        ok = post(url, {
            "title": task["title"],
            "details": "%s\n\nEvidence: %s\n\nRaised by the weekly rules review." % (
                task["details"], task["evidence"]),
            "section": "network",
            "priority": task.get("priority", 2),
        }, {"authorization": "Bearer " + fed}, "task on %s" % task["site"])
        placed += 1 if ok else 0

    bridge = os.environ.get("NTHSKY_BUILDER_TOKEN")
    if bridge:
        note = review["summary"]
        if skipped:
            note += "\n\nNot placed on a board (no write endpoint or key): " + "; ".join(skipped)
        note += "\n\nFull proposal: %s/proposal.md in ovrgrid/airules." % review_dir
        post(BRIDGE + "/messages", {"body": note},
             {"authorization": "Bearer " + bridge}, "bridge message")
    else:
        print("NTHSKY_BUILDER_TOKEN not set; the summary stays in the PR only.")

    print(review["summary"])
    print("tasks placed: %d, skipped: %d" % (placed, len(skipped)))
    return 0


def render(r):
    out = ["# Weekly rules review", "", r["summary"], ""]
    if r.get("rule_changes"):
        out += ["## Proposed rule changes", ""]
        for c in r["rule_changes"]:
            out += ["**%s** - %s" % (c["rule"], c["change"]), "", "Why: %s" % c["why"], ""]
    if r.get("lessons"):
        out += ["## Proposed LESSONS entries", ""]
        for l in r["lessons"]:
            out += ["### %s" % l["title"], "", l["what_happened"], "",
                    "**Root cause:** %s" % l["root_cause"], "",
                    "**Produced:** %s" % l["rule"], ""]
    if r.get("site_tasks"):
        out += ["## Work proposed for the site boards", "",
                "| Site | Task | Evidence |", "|---|---|---|"]
        for t in r["site_tasks"]:
            out.append("| %s | %s | %s |" % (t["site"], t["title"], t["evidence"]))
        out.append("")
    out += ["---", "",
            "Proposed, not applied. Rules change by merging this into `RULES.md` and",
            "`LESSONS.md`. Nothing here edited a site.", ""]
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
