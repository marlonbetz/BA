# IELex+ASJP


## Transcriptions

Some of the words in this data set have IPA transcriptions and some have ASJP
transcriptions; there are also words with both and no transcription at all. The
words without transcription are naturally excluded from the harvest.

However, almost all the words which have both transcriptions have the problem
that when converting their IPA transcription to ASJP using the LingPy library,
the resulting string does not coincide with their given ASJP transcriptions.
Thus, I decided to keep only one of the two transcriptions, the IPA ones,
because of the distribution of the subsets:

* 7069 words only have IPA transcription;
* 3560 words only have ASJP transcription;
* 1718 words have both IPA and ASJP transcriptions;
* 13325 words have no transcription provided.


### Change log

* The Old Church Slavonic for `fight` has its transcription in Cyrillic. It has
  been excluded from the output.
* When a transcription takes the form `A/B`, only `A` is included in the output.
  There is the exception of the Macedonian for liver, `t͡sr̩n drɔp`.
* Similarly, when a transcription takes the form `A; B`, only `A` is included in
  the output.
* Transcriptions are lowercased (only `nakɐ Kɐn-` is affected).
* The following replacements:
	* `ε` (epsilon) into `ɛ` (Latin epsilon).
	* `е` (Cyrillic) into `e` (Latin).
* The following chars are excluded from the output:
	* `(`, `)`.
	* `'`, `‘`, `’`.
	* `‿`.
	* ``.


## Glosses

Notes:

* The gloss identified as `to lie down` in the data is assigned to the global
  gloss `LIE (REST)` instead of `LIE DOWN`, as the latter means "to assume
  horizontal position" and the former means "to rest in a horizontal position".
  Rationale: the gloss in the Slavic languages, English, and German.


Possible errors:

* The gloss for `rain` in Dutch, German, Italian (and possibly others) is the
  verb, not the noun as it is for the other languages I have knowledge about
  (the Slavic languages, Spanish, Portuguese).


Other:

* Languages which have less than 10 glosses are excluded from the output.
  Affected languages: `UKRAINIAN`, `LUXEMBOURGISH`, `ROMANSH_SURSILVAN`,
  `SANSKRIT`, `PUNJABI_MAJHI`.


