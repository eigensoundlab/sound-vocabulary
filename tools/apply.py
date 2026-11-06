#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Daniel Sandner
"""Applies the choices exported from docs/review.html: the chosen alternative becomes the term, the old term moves to
the alternatives.

    python3 tools/apply.py decisions.json          # write the changes
    python3 tools/apply.py decisions.json --dry    # only list them
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")


def main(args):
    if not args:
        sys.exit(__doc__)
    dry = "--dry" in args
    d = json.load(open(args[0], encoding="utf-8"))
    if d.get("format") != "sound-vocabulary-decisions":
        sys.exit("not a decisions file from docs/review.html")
    review = []
    for lang, picks in d.get("picks", {}).items():
        path = os.path.join(ROOT, "translations", lang + ".json")
        T = json.load(open(path, encoding="utf-8"))
        entries = T.get("terms", T)
        changed = 0
        for tid, chosen in picks.items():
            e = entries.get(tid)
            if not e or not chosen or chosen == e.get("term"):
                continue
            old = e["term"]
            e["alt"] = [old] + [a for a in e.get("alt", []) if a != chosen and a != old]
            e["term"] = chosen
            changed += 1
            print(f"{lang} {tid}: {old} -> {chosen}")
            # labels and definitions were written for the old term: list them for a look
            if e.get("short"):
                review.append(f"{lang} {tid}: label is still '{e['short']}'")
            if old.lower() in (e.get("definition") or "").lower():
                review.append(f"{lang} {tid}: definition mentions '{old}'")
        if changed and not dry:
            open(path, "w", encoding="utf-8").write(json.dumps(T, ensure_ascii=False, indent=2) + "\n")
    if review:
        print("\nCheck by hand:\n  " + "\n  ".join(review))
    print("\nThen: python3 tools/check.py translations/*.json, and update the apps' translations that use these terms.")


if __name__ == "__main__":
    main(sys.argv[1:])
