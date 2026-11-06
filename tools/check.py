#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Daniel Sandner
"""Checks a translation file against the English vocabulary:  python3 tools/check.py translations/cs.json"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
EN = {r["id"]: r for r in csv.DictReader(open(os.path.join(HERE, "../src/terms.en.tsv"), encoding="utf-8"), delimiter="\t")}
problems = []
for path in sys.argv[1:]:
    T = json.load(open(path, encoding="utf-8"))
    entries = T.get("terms", T)
    for k, r in EN.items():
        e = entries.get(k)
        if not e: problems.append(f"{path}: missing {k}"); continue
        if not str(e.get("term", "")).strip(): problems.append(f"{path}: {k}: empty term")
        if r["definition"] and not str(e.get("definition", "")).strip(): problems.append(f"{path}: {k}: missing definition")
        if r["status"] == "coined" and len([a for a in e.get("alt", []) if str(a).strip()]) < 2:
            problems.append(f"{path}: {k}: coined term needs at least two alternatives in 'alt'")
        if e.get("short") and len(e["short"]) > 22: problems.append(f"{path}: {k}: short label over 22 characters")
    for k in entries:
        if k not in EN and not k.startswith("_"): problems.append(f"{path}: unknown id {k}")
print("\n".join(problems) or "ok: " + ", ".join(sys.argv[1:]))
sys.exit(1 if problems else 0)
