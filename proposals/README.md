# Proposed terms

Terms the Playhead translations needed that the vocabulary does not have yet, one file per language:
`english`, the translation, the Playhead keys that use it, and a note. Across the five languages there are about 70
distinct terms; those proposed by most languages come first in line for the next version of `src/terms.en.tsv`:
envelope, pan, timbre, bar line, thumbnail, loop seam, hit, riser, sweep, grain, headroom (all five languages),
stereo width, asset, zero crossing, sound object (four), brightness, chroma, loudness range (three), and spectral flux,
F-measure, harshness factor, predictive information, beat tracker, match loudness, swell, effects bench (two).

Adding one: write its English row (with a definition and, where it exists, the standard that defines it), move the
translations from these files into `translations/<lang>.json`, and run `tools/check.py`.
