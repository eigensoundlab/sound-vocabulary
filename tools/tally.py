#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Daniel Sandner
"""Counts the term choices people sent from the review sheet (GitHub issues titled "Term choices", made from the
term-choices form) into docs/votes.json, which the review sheet shows next to each alternative. One account counts
once per term: its latest choice. Only the vocabulary's own terms and alternatives are counted; other words go to
"other" for the maintainer to read.

    python3 tools/tally.py                 # needs the GitHub CLI (gh), logged in, or GH_TOKEN in CI
"""
import csv, datetime, json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
REPO = os.environ.get("GITHUB_REPOSITORY", "eigensoundlab/sound-vocabulary")


def main():
    en = {r["id"] for r in csv.DictReader(open(os.path.join(ROOT, "src/terms.en.tsv"), encoding="utf-8"), delimiter="\t")}
    offered = {}
    for f in os.listdir(os.path.join(ROOT, "translations")):
        if f.endswith(".json"):
            T = json.load(open(os.path.join(ROOT, "translations", f), encoding="utf-8"))
            offered[f[:-5]] = {k: {v["term"], *[a for a in v.get("alt", []) if a]} for k, v in T.get("terms", T).items() if not k.startswith("_")}
    out = subprocess.run(["gh", "issue", "list", "--repo", REPO, "--state", "all", "--limit", "5000", "--search", "Term choices in:title",
                          "--json", "number,author,body,createdAt"], capture_output=True, text=True, check=True).stdout
    issues = sorted(json.loads(out), key=lambda i: i["createdAt"])
    latest = {}                                    # (author, lang, id) -> term, the latest issue wins
    for i in issues:
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", i.get("body") or "", re.S)
        if not m:
            continue
        try:
            choices = json.loads(m.group(1))
        except ValueError:
            continue
        who = (i.get("author") or {}).get("login", "?")
        for lang, picks in choices.items() if isinstance(choices, dict) else []:
            if lang in offered and isinstance(picks, dict):
                for tid, term in picks.items():
                    if tid in en and isinstance(term, str) and 0 < len(term) < 120:
                        latest[(who, lang, tid)] = term.strip()
    votes, other = {}, {}
    for (who, lang, tid), term in latest.items():
        bucket = votes if term in offered[lang].get(tid, ()) else other
        bucket.setdefault(lang, {}).setdefault(tid, {})
        bucket[lang][tid][term] = bucket[lang][tid].get(term, 0) + 1
    result = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "voters": len({w for w, _, _ in latest}), "votes": votes, "other": other}
    path = os.path.join(ROOT, "docs", "votes.json")
    old = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    if {k: v for k, v in old.items() if k != "updated"} == {k: v for k, v in result.items() if k != "updated"}:
        print("no change:", result["voters"], "people")
        return
    open(path, "w", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print("wrote docs/votes.json:", result["voters"], "people,", sum(len(t) for t in votes.values()), "terms with votes")


if __name__ == "__main__":
    main()
