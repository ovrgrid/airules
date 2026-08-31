#!/usr/bin/env python3
"""Replace the AIRULES block in a consumer file with the canonical one.

Usage: apply_block.py <canonical RULES.md> <target file>
Exit 0 = file changed, 1 = already identical, 2 = markers missing (needs a human).

The block is everything from the START marker line through the END marker line,
inclusive, so the markers themselves are re-written and the version in the START
marker always tells the truth about which rules the repo carries.
"""
import re
import sys

START = re.compile(r"^<!-- AIRULES:START[^>]*-->$", re.M)
END = re.compile(r"^<!-- AIRULES:END -->$", re.M)


def extract(text, what):
    s, e = START.search(text), END.search(text)
    if not s or not e or e.start() < s.start():
        sys.stderr.write("markers missing or out of order in %s\n" % what)
        sys.exit(2)
    return text[s.start():e.end()], s.start(), e.end()


def main():
    canonical_path, target_path = sys.argv[1], sys.argv[2]
    with open(canonical_path, encoding="utf-8") as fh:
        block, _, _ = extract(fh.read(), canonical_path)
    with open(target_path, encoding="utf-8") as fh:
        target = fh.read()
    current, start, end = extract(target, target_path)
    if current == block:
        return 1
    with open(target_path, "w", encoding="utf-8") as fh:
        fh.write(target[:start] + block + target[end:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
