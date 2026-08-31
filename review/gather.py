#!/usr/bin/env python3
"""The gather: collect evidence about every repo. No judgement, no AI, no network writes.

Runs Saturdays at 03:00 Phoenix. Writes reviews/<date>/evidence.json plus a readable
summary, and that file is the audit trail: if the analysis half never runs, or runs and
is wrong, the evidence still exists and can be re-read.

Usage: gather.py <workdir with the repo clones> <output dir>
Every field here is a fact with a source. Nothing in this file is an opinion.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

REPOS = ["nthsky.ai", "ovrops", "ovr3d", "ovrflight", "teamtrain"]

# Unauthenticated-safe probes only. The 401/503 split is deliberate network design:
# 401 = the endpoint is armed, 503 = deployed but the key is missing, 404 = not deployed.
PROBES = {
    "nthsky.ai": "https://nthsky.ai/api/nthsky/tasks",
    "ovrops": "https://ovrops.com/api/nthsky/tasks",
    "ovr3d": "https://ovr3d.com/api/nthsky/tasks",
    "ovrflight": "https://ovrflight.org/api/nthsky/tasks",
    "teamtrain": "https://teamtrain.us/api/nthsky/tasks",
}

# Built from the codepoint, not typed: a file that hunts for em dashes must not contain
# one, and it must not contain the escaped form either or it flags itself.
EM_DASH = chr(0x2014)
ESCAPED_EM_DASH = chr(92) + "u2014"

BLOCK = re.compile(r"^<!-- AIRULES:START[^>]*-->$.*?^<!-- AIRULES:END -->$", re.M | re.S)
# The five repos write their version header two ways: "**Version:** 2.07a" (nthsky, ovr3d)
# and "**Version 0.91o - 2026-08-28**" (ovrops). Match both rather than picking a winner:
# normalising the headers would be a rewrite of four working files to satisfy a script.
VERSION = re.compile(r"^\*\*Version[:*\s]*([0-9]+\.[0-9]+[a-z]?)", re.M)
DATED_HEADING = re.compile(r"^#{2,4}\s*(\d{4}-\d{2}-\d{2})", re.M)


def git(repo, *args):
    try:
        return subprocess.run(
            ["git", "-C", repo, *args], capture_output=True, text=True, timeout=60
        ).stdout.strip()
    except (subprocess.SubprocessError, OSError) as exc:
        return "ERROR: %s" % exc


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def probe(url):
    """Return the status code, or a reason string. Never raises: a probe that cannot
    run is evidence too, and it must not take the whole gather down."""
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:  # network, DNS, TLS, timeout
        return "unreachable: %s" % type(exc).__name__


def since(repo, ref):
    """Commits on main since a date, oldest first, as 'hash date subject'."""
    out = git(repo, "log", "--since", ref, "--date=short",
              "--pretty=%h %ad %s", "origin/main")
    return [line for line in out.splitlines() if line]


def gather_repo(workdir, name, window):
    path = os.path.join(workdir, name)
    claude = read(os.path.join(path, "CLAUDE.md"))
    infra = read(os.path.join(path, "INFRASTRUCTURE.md"))
    buildlog = read(os.path.join(path, "BUILDLOG.md"))

    block = BLOCK.search(claude) if claude else None
    infra_version = VERSION.search(infra).group(1) if infra and VERSION.search(infra) else None
    buildlog_dates = DATED_HEADING.findall(buildlog) if buildlog else []
    commits = since(path, window)

    # An em-dash sweep of everything a session or a user actually reads. Text files only:
    # a binary asset containing the byte sequence is not prose and is not a violation.
    dashed = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "infra-versions")]
        for fn in files:
            if not fn.endswith((".md", ".js", ".mjs", ".html", ".json", ".sql", ".toml", ".jsonc")):
                continue
            fp = os.path.join(root, fn)
            body = read(fp)
            if body and (EM_DASH in body or ESCAPED_EM_DASH in body):
                dashed.append(os.path.relpath(fp, path))

    return {
        "repo": name,
        "head": git(path, "rev-parse", "--short", "origin/main"),
        "head_date": git(path, "log", "-1", "--date=short", "--pretty=%ad", "origin/main"),
        "commits_in_window": commits,
        "commit_count": len(commits),
        "airules_block_present": bool(block),
        "airules_block_sha": (
            subprocess.run(["sha256sum"], input=block.group(0), capture_output=True,
                           text=True).stdout.split()[0][:16] if block else None
        ),
        "infrastructure_version": infra_version,
        "buildlog_last_entry": max(buildlog_dates) if buildlog_dates else None,
        "buildlog_entries_in_window": [d for d in buildlog_dates if d >= window],
        "em_dash_files": dashed,
        "federation_probe": probe(PROBES.get(name, "")) if name in PROBES else None,
    }


def canonical_sha(airules_dir):
    rules = read(os.path.join(airules_dir, "RULES.md")) or ""
    m = BLOCK.search(rules)
    if not m:
        return None
    return subprocess.run(["sha256sum"], input=m.group(0), capture_output=True,
                          text=True).stdout.split()[0][:16]


def main():
    workdir, outdir = sys.argv[1], sys.argv[2]
    airules_dir = sys.argv[3] if len(sys.argv) > 3 else "."
    window = sys.argv[4] if len(sys.argv) > 4 else "7 days ago"
    # Normalise the window to a date so string comparisons against BUILDLOG headings work.
    window_date = git(".", "log", "-1", "--pretty=%ad") and subprocess.run(
        ["date", "-u", "-d", window, "+%Y-%m-%d"], capture_output=True, text=True
    ).stdout.strip()

    canon = canonical_sha(airules_dir)
    sites = []
    for name in REPOS:
        if not os.path.isdir(os.path.join(workdir, name)):
            sites.append({"repo": name, "error": "not cloned"})
            continue
        row = gather_repo(workdir, name, window_date or "1970-01-01")
        row["block_matches_canonical"] = (row["airules_block_sha"] == canon) if canon else None
        sites.append(row)

    evidence = {
        "gathered_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "window_since": window_date,
        "canonical_block_sha": canon,
        "sites": sites,
    }

    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "evidence.json"), "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, indent=2, sort_keys=True)
    with open(os.path.join(outdir, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(render(evidence))
    print(render(evidence))
    return 0


def render(ev):
    lines = [
        "# Gather - %s" % ev["gathered_at"][:10],
        "",
        "Facts only. Collected by `review/gather.py`, no judgement applied. The analysis",
        "half reads this file; if it never ran, this is still the record of that week.",
        "",
        "Window: commits and BUILDLOG entries since **%s**." % ev["window_since"],
        "Canonical rules block: `%s`." % (ev["canonical_block_sha"] or "unknown"),
        "",
        "| Site | Head | Commits | Rules block | INFRA | BUILDLOG last | Em dashes | Federation |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in ev["sites"]:
        if s.get("error"):
            lines.append("| %s | %s | | | | | | |" % (s["repo"], s["error"]))
            continue
        block = "missing" if not s["airules_block_present"] else (
            "ok" if s.get("block_matches_canonical") else "DRIFTED")
        lines.append("| %s | `%s` %s | %d | %s | %s | %s | %d | %s |" % (
            s["repo"], s["head"], s["head_date"], s["commit_count"], block,
            s["infrastructure_version"] or "n/a", s["buildlog_last_entry"] or "none",
            len(s["em_dash_files"]), s["federation_probe"]))
    lines += [
        "",
        "Federation probe: 401 = armed, 503 = deployed but key missing, 404 = not deployed.",
        "A drifted or missing rules block is the sync's job. Everything else is a question",
        "for the review, not an answer.",
        "",
    ]
    for s in ev["sites"]:
        if s.get("em_dash_files"):
            lines.append("**%s em dashes:** %s" % (s["repo"], ", ".join(s["em_dash_files"][:20])))
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
