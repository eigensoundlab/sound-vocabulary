#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Daniel Sandner
"""Builds the review sheet, docs/review.html: every term in English and each language side by side, the coined terms
with their alternatives to choose from. Choices are kept in the browser, or, where the page is published with a shared
store (a claude.ai artifact declaring db), saved with the page per language (picks/<lang>), so reviewers of different
languages can work at once. Export gives decisions.json, which tools/apply.py writes back into the translations.

    python3 tools/review.py            -> docs/review.html
"""
import csv, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
LANGS = ["cs", "de", "es", "pl", "ru"]


def load():
    en = list(csv.DictReader(open(os.path.join(ROOT, "src/terms.en.tsv"), encoding="utf-8"), delimiter="\t"))
    tr, meta = {}, {}
    for l in LANGS:
        p = os.path.join(ROOT, "translations", l + ".json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        tr[l] = {k: v for k, v in d.get("terms", d).items() if not k.startswith("_")}
        meta[l] = {"name": d.get("_name", l), "notes": d.get("_notes", "")}
    return en, tr, meta


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sound vocabulary review</title>
<style>
:root{--bg:#f6f7f8;--surface:#fff;--ink:#14181b;--ink2:#4c565d;--ink3:#7a858c;--rule:#dde2e5;--accent:#1f5fae;--accentBg:#e7effa;--coined:#fff6e0;--coinedRule:#e8c66a;--pick:#d8f0e0;--pickInk:#14532d}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121517;--surface:#1b1f22;--ink:#e6eaec;--ink2:#a9b3b9;--ink3:#7f8a91;--rule:#2d3439;--accent:#7fb0f0;--accentBg:#1d2a3a;--coined:#2c2614;--coinedRule:#7a6326;--pick:#173a26;--pickInk:#b8ecc9}}
:root[data-theme="dark"]{--bg:#121517;--surface:#1b1f22;--ink:#e6eaec;--ink2:#a9b3b9;--ink3:#7f8a91;--rule:#2d3439;--accent:#7fb0f0;--accentBg:#1d2a3a;--coined:#2c2614;--coinedRule:#7a6326;--pick:#173a26;--pickInk:#b8ecc9}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:1500px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:22px;margin:0 0 4px}
h2{font-size:16px;margin:28px 0 8px}
p.lead{color:var(--ink2);margin:0 0 14px;max-width:80ch}
.bar{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;border-bottom:1px solid var(--rule)}
.bar label{font-size:13px;color:var(--ink2);display:inline-flex;gap:6px;align-items:center}
select,input[type=search],button{font:inherit;font-size:13px;color:var(--ink);background:var(--surface);border:1px solid var(--rule);border-radius:4px;padding:4px 8px;min-height:30px}
input[type=search]{width:min(240px,100%)}
button{cursor:pointer}button:hover{border-color:var(--ink3)}
button.primary{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.count{font-size:13px;color:var(--ink3)}
.wrap{overflow-x:auto;border:1px solid var(--rule);border-radius:6px;background:var(--surface)}
table{border-collapse:collapse;width:100%;min-width:900px}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--rule)}
th{font-size:12px;font-weight:600;color:var(--ink2);background:var(--surface);position:sticky;top:0}
td.en{min-width:220px;max-width:320px}
td.l{min-width:170px}
tr.coined td{background:var(--coined)}
tr.coined td.en{box-shadow:inset 3px 0 0 var(--coinedRule)}
.t{font-weight:600}
.s{font-size:12px;color:var(--ink3)}
.d{font-size:12.5px;color:var(--ink2);margin-top:3px}
.tag{display:inline-block;font-size:11px;padding:0 6px;border-radius:9px;border:1px solid var(--rule);color:var(--ink3);margin-right:4px}
.tag.c{border-color:var(--coinedRule);color:var(--ink)}
.alts{display:flex;flex-wrap:wrap;gap:4px;margin-top:5px}
.alt{font-size:12px;border:1px solid var(--rule);border-radius:4px;padding:1px 6px;background:var(--surface);cursor:pointer;color:var(--ink)}
.alt:hover{border-color:var(--accent)}
.alt[aria-pressed="true"]{background:var(--pick);color:var(--pickInk);border-color:var(--pickInk)}
.picked{color:var(--pickInk);background:var(--pick);border-radius:4px;padding:0 4px}
details{margin-top:4px}summary{font-size:12px;color:var(--accent);cursor:pointer}
details p{font-size:12.5px;color:var(--ink2);margin:4px 0 0}
.notes{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.notes section{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:10px 12px}
.notes h3{margin:0 0 6px;font-size:14px}
.notes div{font-size:12.5px;color:var(--ink2);white-space:pre-wrap}
.hint{font-size:12.5px;color:var(--ink3)}
.hidden{display:none}
@media (max-width:600px){h1{font-size:19px}.bar{position:static}}
</style>
</head>
<body>
<main>
<h1>Sound vocabulary: review</h1>
<p class="lead">__COUNTS__ Shared by Playhead, SFX Workbench and later apps and docs. Coined terms (shaded) are new or unsettled in some
languages; each translation offers alternatives. Click an alternative to choose it instead of the proposed term, then export
the choices for <code>tools/apply.py</code>. Pick one language under Languages to review it on a phone.</p>
<div class="bar">
  <label>Show <select id="f-status"><option value="coined">Coined terms only</option><option value="">All terms</option><option value="standard">Standard</option><option value="common">Common</option></select></label>
  <label>Group <select id="f-group"><option value="">All</option></select></label>
  <label>App <select id="f-app"><option value="">Any</option><option value="playhead">Playhead</option><option value="workbench">Workbench</option></select></label>
  <label>Languages <select id="f-lang"><option value="">All</option></select></label>
  <input type="search" id="f-q" placeholder="Search any language" aria-label="Search any language">
  <span class="count" id="count"></span>
  <button type="button" id="export" class="primary">Export choices</button>
  <button type="button" id="clear">Clear choices</button>
</div>
<p class="hint" id="exported" hidden></p>
<p class="hint" id="sync">Choices are kept in this browser.</p>
<div class="wrap"><table><thead><tr id="head"></tr></thead><tbody id="rows"></tbody></table></div>
<h2>Conventions per language</h2>
<div class="notes" id="notes"></div>
</main>
<script>
const EN = __EN__, TR = __TR__, META = __META__;
const LANGS = Object.keys(TR);
const KEY = "sound-vocabulary.picks";
let picks = {};
try { picks = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { picks = {}; }
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(picks)); } catch (e) { /* not kept */ } };
// where the page has a shared store, each language's choices are one document, picks/<lang>
let DB = null;
const writing = {}, again = {};
const clean = o => Object.fromEntries(Object.entries(o || {}).filter(([k, v]) => typeof k === "string" && typeof v === "string" && v.length < 200));
async function share(l) {
  if (!DB) return;
  if (writing[l]) { again[l] = true; return; }
  writing[l] = true;
  try { await DB.doc("picks/" + l).set({ picks: picks[l] || {}, updated: new Date().toISOString() }); }
  catch (e) { if (e && (e.code === "invalid_argument" || e.code === "revoked")) { DB = null; $("sync").textContent = "You can't save shared choices here; they are kept in this browser."; } }
  finally { writing[l] = false; if (again[l]) { again[l] = false; share(l); } }
}
(async () => {
  if (!window.claude || typeof window.claude.use !== "function") return;
  let db = null;
  try { db = await window.claude.use("db"); } catch (e) { db = null; }
  if (!db) return;
  DB = db;
  $("sync").textContent = "Loading the shared choices…";
  const timer = setTimeout(() => { $("sync").textContent = "The shared choices can't be reached yet; showing this browser's."; }, 10000);
  for (const l of LANGS) db.doc("picks/" + l).onSnapshot(snap => {
    if (snap.metadata.fromCache) return;
    clearTimeout(timer);
    $("sync").textContent = "Choices are saved with this page, one list per language, for everyone who reviews it.";
    if (snap.exists) picks[l] = clean((snap.data() || {}).picks);
    else if (Object.keys(picks[l] || {}).length) share(l);   // first visit with a shared store: keep this browser's choices
    save(); draw();
  }, () => { clearTimeout(timer); $("sync").textContent = "The shared choices can't be reached; they are kept in this browser."; });
})();
const $ = id => document.getElementById(id);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
for (const g of [...new Set(EN.map(r => r.group))]) { const o = el("option", "", g); o.value = g; $("f-group").appendChild(o); }
for (const l of LANGS) { const o = el("option", "", META[l].name); o.value = l; $("f-lang").appendChild(o); }

function head(langs) {
  const h = $("head"); h.innerHTML = "";
  h.appendChild(el("th", "", "English"));
  for (const l of langs) h.appendChild(el("th", "", META[l].name));
}
function cell(r, l) {
  const td = el("td", "l"), e = TR[l][r.id];
  if (!e) { td.appendChild(el("span", "s", "missing")); return td; }
  const pk = (picks[l] || {})[r.id];
  const t = el("div", "t" + (pk ? "" : ""), pk || e.term); if (pk) t.classList.add("picked"); td.appendChild(t);
  if (e.short && e.short !== e.term) td.appendChild(el("div", "s", "label: " + e.short));
  if (e.gender) td.appendChild(el("span", "tag", e.gender));
  const alts = (e.alt || []).filter(Boolean);
  if (alts.length) {
    const box = el("div", "alts");
    for (const a of [e.term].concat(alts)) {
      const b = el("button", "alt", a); b.type = "button";
      b.setAttribute("aria-pressed", String((pk || e.term) === a));
      b.title = a === e.term ? "proposed term" : "use this instead";
      b.addEventListener("click", () => { picks[l] = picks[l] || {}; if (a === e.term) delete picks[l][r.id]; else picks[l][r.id] = a; save(); draw(); share(l); });
      box.appendChild(b);
    }
    td.appendChild(box);
  }
  if (e.definition || e.note) {
    const d = el("details"); d.appendChild(el("summary", "", "definition and note"));
    if (e.definition) d.appendChild(el("p", "", e.definition));
    if (e.note) { const p = el("p", ""); p.appendChild(el("i", "", e.note)); d.appendChild(p); }
    td.appendChild(d);
  }
  return td;
}
function draw() {
  const st = $("f-status").value, gr = $("f-group").value, app = $("f-app").value, lang = $("f-lang").value, q = $("f-q").value.trim().toLowerCase();
  const langs = lang ? [lang] : LANGS;
  head(langs);
  const body = $("rows"); body.innerHTML = "";
  let n = 0;
  for (const r of EN) {
    if (st && r.status !== st) continue;
    if (gr && r.group !== gr) continue;
    if (app && !(r.apps || "").split(/\s+/).includes(app)) continue;
    if (q) {
      const hay = [r.term, r.definition, r.id].concat(LANGS.flatMap(l => { const e = TR[l][r.id] || {}; return [e.term, e.short, e.definition].concat(e.alt || []); })).join(" ").toLowerCase();
      if (!hay.includes(q)) continue;
    }
    n++;
    const tr = el("tr", r.status === "coined" ? "coined" : "");
    const en = el("td", "en");
    en.appendChild(el("div", "t", r.term));
    const tags = el("div", "");
    tags.appendChild(el("span", "tag" + (r.status === "coined" ? " c" : ""), r.status));
    tags.appendChild(el("span", "tag", r.group));
    for (const a of (r.apps || "").split(/\s+/).filter(Boolean)) tags.appendChild(el("span", "tag", a));
    en.appendChild(tags);
    if (r.short) en.appendChild(el("div", "s", "label: " + r.short));
    if (r.definition) en.appendChild(el("div", "d", r.definition));
    if (r.avoid) en.appendChild(el("div", "s", "not: " + r.avoid));
    if (r.ref) en.appendChild(el("div", "s", r.ref));
    tr.appendChild(en);
    for (const l of langs) tr.appendChild(cell(r, l));
    body.appendChild(tr);
  }
  const chosen = LANGS.reduce((a, l) => a + Object.keys(picks[l] || {}).length, 0);
  $("count").textContent = n + " of " + EN.length + " terms" + (chosen ? " · " + chosen + " changed" : "");
}
for (const id of ["f-status", "f-group", "f-app", "f-lang"]) $(id).addEventListener("change", draw);
$("f-q").addEventListener("input", draw);
$("clear").addEventListener("click", () => {
  const langs = $("f-lang").value ? [$("f-lang").value] : LANGS;
  if (!confirmClear(langs)) return;
  for (const l of langs) { picks[l] = {}; share(l); }
  save(); draw(); $("exported").hidden = true;
});
let armed = 0;
// a second click within 3 s confirms (no browser dialog)
function confirmClear(langs) {
  const b = $("clear"), now = Date.now();
  if (now - armed < 3000) { armed = 0; b.textContent = "Clear choices"; return true; }
  armed = now; b.textContent = "Click again to clear " + (langs.length === 1 ? META[langs[0]].name : "all languages");
  setTimeout(() => { if (Date.now() - armed >= 3000) b.textContent = "Clear choices"; }, 3100);
  return false;
}
$("export").addEventListener("click", async () => {
  const out = JSON.stringify({ format: "sound-vocabulary-decisions", version: 1, picks }, null, 1);
  let how = "copied to the clipboard";
  try { await navigator.clipboard.writeText(out); } catch (e) {
    if (DB) { $("exported").hidden = false; $("exported").textContent = "Copying is blocked here, but the choices are saved with this page and can be read from it."; return; }
    how = "downloaded as decisions.json";
    const a = el("a"); a.href = URL.createObjectURL(new Blob([out], { type: "application/json" })); a.download = "decisions.json"; document.body.appendChild(a); a.click(); a.remove();
  }
  const n = LANGS.reduce((a, l) => a + Object.keys(picks[l] || {}).length, 0);
  $("exported").hidden = false; $("exported").textContent = n + " choices " + how + ". Apply them with: python3 tools/apply.py decisions.json";
});
for (const l of LANGS) { const s = el("section"); s.appendChild(el("h3", "", META[l].name)); s.appendChild(el("div", "", META[l].notes || "")); $("notes").appendChild(s); }
draw();
</script>
</body>
</html>
"""


def main():
    en, tr, meta = load()
    coined = sum(1 for r in en if r["status"] == "coined")
    counts = f"{len(en)} terms, {coined} of them coined, in English and {len(tr)} languages ({', '.join(meta[l]['name'] for l in tr)})."
    rows = [{k: r[k] for k in ("id", "group", "status", "term", "short", "definition", "avoid", "ref", "apps")} for r in en]
    keep = ("term", "short", "alt", "definition", "note", "gender")
    trs = {l: {k: {f: v[f] for f in keep if f in v} for k, v in t.items()} for l, t in tr.items()}
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    html = PAGE.replace("__COUNTS__", counts).replace("__EN__", js(rows)).replace("__TR__", js(trs)).replace("__META__", js(meta))
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    out = os.path.join(ROOT, "docs", "review.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", os.path.relpath(out, ROOT), "-", counts)


if __name__ == "__main__":
    main()
