#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Daniel Sandner
"""Exports the vocabulary for translation tools and apps, into dist/:

    glossary.tbx         TBX (ISO 30042) termbase, all languages: for CAT tools (Trados, memoQ, OmegaT) and Weblate
    glossary-<lang>.csv  English term, translation, definition, note: a glossary for Crowdin, Lokalise or a spreadsheet
    terms-<lang>.json    { id: { term, short, definition } }: for apps that show terms and their definitions in help

    python3 tools/export.py
"""
import csv, json, os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
LANGS = ["cs", "de", "es", "pl", "ru"]
GENDER = {"m": "masculine", "f": "feminine", "n": "neuter"}


def main():
    en = list(csv.DictReader(open(os.path.join(ROOT, "src/terms.en.tsv"), encoding="utf-8"), delimiter="\t"))
    tr = {}
    for l in LANGS:
        p = os.path.join(ROOT, "translations", l + ".json")
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8"))
            tr[l] = {k: v for k, v in d.get("terms", d).items() if not k.startswith("_")}
    out = os.path.join(ROOT, "dist")
    os.makedirs(out, exist_ok=True)

    # TBX-Basic: one concept per term, English first; status "admitted" for alternatives
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<tbx type="TBX-Basic" style="dca" xml:lang="en" xmlns="urn:iso:std:iso:30042:ed-2">',
         '<tbxHeader><fileDesc><sourceDesc><p>eigensoundlab sound vocabulary, https://github.com/eigensoundlab/sound-vocabulary</p></sourceDesc></fileDesc></tbxHeader>',
         '<text><body>']
    for r in en:
        x.append(f'<conceptEntry id="{escape(r["id"])}">')
        x.append(f'<descrip type="subjectField">{escape(r["group"])}</descrip>')
        x.append('<langSec xml:lang="en">')
        if r["definition"]:
            x.append(f'<descrip type="definition">{escape(r["definition"])}</descrip>')
        x.append(f'<termSec><term>{escape(r["term"])}</term><termNote type="administrativeStatus">preferredTerm-admn-sts</termNote></termSec>')
        if r["avoid"]:
            x.append(f'<termSec><term>{escape(r["avoid"].split(" (")[0])}</term><termNote type="administrativeStatus">deprecatedTerm-admn-sts</termNote></termSec>')
        x.append('</langSec>')
        for l, t in tr.items():
            e = t.get(r["id"])
            if not e:
                continue
            x.append(f'<langSec xml:lang="{l}">')
            if e.get("definition"):
                x.append(f'<descrip type="definition">{escape(e["definition"])}</descrip>')
            x.append(f'<termSec><term>{escape(e["term"])}</term><termNote type="administrativeStatus">preferredTerm-admn-sts</termNote>'
                     + (f'<termNote type="grammaticalGender">{GENDER[e["gender"][:1]]}</termNote>' if str(e.get("gender", ""))[:1] in GENDER else "")
                     + (f'<note>{escape(e["note"])}</note>' if e.get("note") else "") + '</termSec>')
            for a in e.get("alt", []):
                if a and a != e["term"]:
                    x.append(f'<termSec><term>{escape(a)}</term><termNote type="administrativeStatus">admittedTerm-admn-sts</termNote></termSec>')
            x.append('</langSec>')
        x.append('</conceptEntry>')
    x.append('</body></text></tbx>')
    open(os.path.join(out, "glossary.tbx"), "w", encoding="utf-8").write("\n".join(x) + "\n")

    for l, t in tr.items():
        with open(os.path.join(out, f"glossary-{l}.csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")     # plain newlines, so patches of the glossaries apply everywhere
            w.writerow(["term", "translation", "definition", "note", "status", "alternatives"])
            for r in en:
                e = t.get(r["id"])
                if e:
                    w.writerow([r["term"], e["term"], r["definition"], e.get("note", ""), r["status"], "; ".join(a for a in e.get("alt", []) if a)])
        app = {r["id"]: {k: v for k, v in (("term", t[r["id"]]["term"]), ("short", t[r["id"]].get("short") or t[r["id"]]["term"]), ("definition", t[r["id"]].get("definition", ""))) if v}
               for r in en if r["id"] in t}
        open(os.path.join(out, f"terms-{l}.json"), "w", encoding="utf-8").write(json.dumps(app, ensure_ascii=False, indent=1) + "\n")
    eng = {r["id"]: {k: v for k, v in (("term", r["term"]), ("short", r["short"] or r["term"]), ("definition", r["definition"])) if v} for r in en}
    open(os.path.join(out, "terms-en.json"), "w", encoding="utf-8").write(json.dumps(eng, ensure_ascii=False, indent=1) + "\n")
    print("wrote dist/: glossary.tbx, " + ", ".join(f"glossary-{l}.csv" for l in tr) + ", terms-<lang>.json for en " + " ".join(tr))


if __name__ == "__main__":
    main()
