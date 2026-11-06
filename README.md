# Sound vocabulary

The terms of sound analysis, sound design and game audio, defined once in English and translated into Czech, German,
Polish, Russian and Spanish. It is the shared termbase of [Playhead](https://github.com/eigensoundlab/playhead) and
[SFX Workbench](https://github.com/eigensoundlab/SFXWorkbench), and of later apps and documentation, so that a term
means the same thing in every app, every language and every paper.

175 terms in six groups: core (34), psychoacoustics (7), analysis (61), tools (31), Workbench (24) and materials and
shapes (18). 109 are standard terms, 38 are common usage and 28 are coined: new names for things Playhead and Workbench
introduce (a *look*, *spectral surprise*, *widen the tails*), or terms a language has no settled word for.

**[Review sheet](docs/review.html)**: every term in English and each language side by side; the coined terms with
their alternatives to choose from.

## Choosing terms together

The review sheet is also how speakers of a language say which terms they prefer. On GitHub Pages
(`https://eigensoundlab.github.io/sound-vocabulary/`, from the `docs` folder) anyone can click the alternatives they
prefer and **Send my choices to the project**: that opens a prefilled GitHub issue (the *Term choices* form), with room
for whether the language is theirs, their field and why. A workflow (`.github/workflows/tally.yml`, `tools/tally.py`)
counts the choices into `docs/votes.json` after every such issue, one vote per account and term (its latest), and the
sheet shows the counts next to each alternative. Votes are advice: each language's maintainer decides, with the
standards and the field's usage in mind, and records why in the term's note.

Setup, once: **Settings > Pages > Deploy from a branch > main, /docs**, and **Settings > Actions > General > Workflow
permissions > Read and write**.

## Files

| File | What it is |
|---|---|
| `src/terms.en.tsv` | the English source: `id`, `group`, `status` (standard, common, coined), `term`, `short` (a UI label when the term is long), `definition`, `avoid` (words not to use for it, and why), `ref` (the standard or paper that defines it), `apps` |
| `translations/<lang>.json` | one language: for each id a `term`, `short`, `alt` (alternatives; at least two for a coined term), `definition`, `note` (why this term, and what to watch for), `gender`; `_notes` gives the conventions the translation follows |
| `docs/review.html` | the review sheet, built by `tools/review.py` |
| `dist/` | exports for translation tools and apps, built by `tools/export.py` |

## Rules the terms follow

- **One concept, one term**, in every language: loudness (heard) is not level (measured); harshness, sharpness and
  roughness are three things; an onset, an attack and a transient are three things; novelty, spectral surprise and
  surprisal are three things.
- **The established word first.** Standards and their official translations (ITU-R BS.1770, EBU R 128, ISO 532-1,
  DIN 45692), then the language's psychoacoustics literature, then the localised DAWs and editors its sound designers use
  (Audacity, Ardour, Cubase, Logic, Ableton Live). An English loan is the term where the studios of that language use it
  (Foley, preset, one-shot), with the native word in `alt`.
- **Coined terms are proposals.** Each has alternatives and a note; the review sheet is where they are decided.
- **Units and codes are not translated** (dB, LUFS, Hz, acum, asper; look codes such as `lane:harshness`).

## Tools

```sh
python3 tools/check.py translations/*.json   # every id present, coined terms with alternatives, short labels ≤ 22 characters
python3 tools/review.py                      # docs/review.html
python3 tools/apply.py decisions.json        # apply the choices exported from the review sheet
python3 tools/export.py                      # dist/: glossary.tbx, glossary-<lang>.csv, terms-<lang>.json
python3 tools/tally.py                       # docs/votes.json from the "Term choices" issues (needs the GitHub CLI)
```

`glossary.tbx` is a TBX-Basic termbase (ISO 30042) for CAT tools (Trados, memoQ, OmegaT) and Weblate;
`glossary-<lang>.csv` is a glossary for Crowdin, Lokalise or a spreadsheet; `terms-<lang>.json` gives apps the term,
label and definition by id, for help texts and tooltips.

## How the apps use it

The apps translate whole sentences, not words, so the vocabulary is not loaded at run time; it decides which words the
sentences use. Playhead's translations (`i18n/<lang>.json` in the Playhead repository) are written from it, and its
`node tools/i18n.js check` keeps their placeholders and markup intact. SFX Workbench and kurator draw Playhead's strips,
so they get the same labels for curves, looks and tools from `Playhead.localize(table)`, with the tables in Playhead's
`dist/i18n/<lang>.json`. A new app or document starts from `dist/terms-<lang>.json` or the TBX file.

## Adding a language

Copy a translation, replace the terms, definitions and notes, write the conventions you follow in `_notes`, give every
coined term at least two alternatives, and run `tools/check.py`. Cite the standards and localised software you followed
in the notes.

## Licence

Code (`tools/`) under the Apache License 2.0 (`LICENSE`). The terms, definitions and translations (`src/`,
`translations/`, `dist/`) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): use them in any app,
document or translation, with credit to "eigensoundlab sound vocabulary".
