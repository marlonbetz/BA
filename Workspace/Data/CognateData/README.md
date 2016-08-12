# CognateData


Notes:

* Language names are kept as is, which is the ASJP language IDs (e.g.
  `AMHARIC_3` instead of `Amharic`).
* Languages without ISO codes are included (the `iso_code` column of their words
  equals the empty string).
* Words which are assigned ID of 0 in the input file are not included in the
  output (e.g. see `Lolo-Burmese.txt`).
* Words which are not listed in the input files' language blocks are not
  included in the output.
* Words which are designated as unattested (their transcription is `XXX`) are
  not included in the output.
* Words which have cognate class of zero (which means that they are unattested)
  are not included in the output. Data sets which have such words are:
  Lolo-Burmese (1), Mayan (12), Mixe-Zoque (7), Mon-Khmer (5), Morobe (1).
* Initial `%` in the transcription designates a loanword.
* Where a specific file's notes say that the respective file was changed, this
  means that it has already been changed in the `input` dir. If you want to
  compare with the original file, you can find the latter in the
  `list_length_data` dir.


## Afrasian

Notes:

* The list of languages in the input file header did not correspond to the list
  of languages in the matrix. That is why the following languages were added
  to the header list (taken from `list_length_data/Afrasian.txt`):
	* AKKADIAN
	* BIBLICAL_HEBREW
	* SYRIAC_2
	* ARABIC_QURANIC
	* GEEZ
	* EGYPTIAN
	* COPTIC
* The ISO code `arb` of ARABIC_QURANIC was added to the input file.


## Athapaskan

Not processed. There appear to be problems with this data set:

* It is not explicitly clear whether the numbers of the cognate items in lines
  100-204 refer to the gloss IDs or to key of the gloss list. The lack of any
  item greater than 78 supports the latter hypothesis.
* If we look at item 11, it is not clear why, for example, it does not appear in
  the NAVAHO-CHIRICAHUA list when it appears in both the NAVAHO-KATO and
  CHIRICAHUA-KATO lists.

The source code of the Athapaskan harvester should be otherwise ready.


## Huon

OK.


## Kadai

Notes:

* The input file was converted to utf-8 from its original encoding of latin1.


## Kamasau

OK.


## Lolo-Burmese

Notes:

* The input file contains a lot of glosses with ID of 0, which are not included
  in the output.


Possible errors:

* Naxi is assigned ISO code of `nbf` which is non-existent according to SIL.
  The code should be `nxq` instead.


## Mayan

Possible errors:

* Huastec is assigned ISO code of `hva` which is non-existent according to SIL.
  The code should be `hus` instead.


## Miao-Yao

Notes:

* In contrast with the other input files, this one was missing line 2. The
  latter was added (copied from `Mixe-Zoque.txt`).


## Mixe-Zoque

OK.


## Mon-Khmer

Notes:

* The input file was converted to utf-8 from its original encoding of latin1.


## Morobe

OK.



