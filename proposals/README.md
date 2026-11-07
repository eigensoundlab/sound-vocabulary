# Proposed terms

Terms the Playhead translations needed that the vocabulary does not have yet, one file per language:
`english`, the translation, the Playhead keys that use it, and a note. Envelope, pan, stereo width, headroom, loudness
range, zero crossing, riser, sweep and match loudness (now *loudness matching*) became terms with the DAW, mixing and
DJ groups; about 60 distinct terms are left. Those proposed by most languages come first in line for the next version
of `src/terms.en.tsv`: timbre, bar line, thumbnail, loop seam, hit, grain (all five languages), asset, sound object
(four), brightness, chroma (three), and spectral flux, F-measure, harshness factor, predictive information, beat
tracker, swell, effects bench (two).

Adding one: write its English row (with a definition and, where it exists, the standard that defines it), move the
translations from these files into `translations/<lang>.json`, and run `tools/check.py`.
