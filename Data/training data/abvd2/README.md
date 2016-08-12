# abvd2


Some remarks:

* Only words that belong to the languages listed in the input file's header are
  extracted. If a language appears more than once, only the first data block is
  taken into account.
* Words from the input data which lack `transcription` and/or `cognate_class`
  information are not included in the output.
* The `cognate_class` column is an integer but sometimes a question mark is
  appended to the integer in the input data. The output keeps these question
  marks.
* The `notes` column contains the original contents of the transcription column
  when this has been modified by the script (see below).
* The `notes` column contains alternative `transcription`-`cognate_class` pairs
  when such are provided in the input data.
* Languages without `iso_code` are included in the output.

The output file is `.tsv`. If you open that with Libre Office or similar, please
make sure that only the tab is the only delimiter, because some data cells
contain commas and/or semicolons.


## Transcriptions

I have fixed a number of issues directly in the input file. Most of them were
most probably related to encoding issues, e.g. the Nalik for shoulder was
`a표al표ala` instead of `aǥalǥala`.

Nonetheless, the input data transcription field often includes non-IPA symbols
which carry some meta-information or are errors:

* Brackets (); e.g. the Maori for hand, `ringa(ringa)`. The string in the
  brackets and the brackets themselves are excluded from the output.
* Square brackets [], e.g. the Jawe for to think, `[ne]nemi`. The square
  brackets are removed from the output but the rest is left as is.
* Plus signs +; e.g. the Inabaknon for stone `bato +t+d1`. The string to the
  right of the first plus sign (inclusive) is stripped from the output.
* Slashes, e.g. the Megiar for belly, `luwa/n`. The string to the right of the
  slash (inclusive) is stripped from the output.
* Digits, e.g. the Hainan Cham for that, `nan 33`. These are converted to their
  superscript counterparts.
* Apostrophes ', e.g. the Nese for stone, `nav'at`. In Nese and Araki (Southwest
  Santo), apostrophes are used to denote apicolabials (there might be other such
  languages, but I could not find them), and are omitted. In other languages,
  apostrophes are replaced by `ʔ` in the output.
* The following are removed from the output without replacement:
	* Three dots ..., e.g. the Santa Ana for to fall, `apur...`.
	* Percent signs %, e.g. the Bobot for if, `%kalu`.
	* Question mark ?, e.g. the Bilibil for leg/foot, `ni?e`. Comments in the
	  website hint that question marks are not glottal stops.
* Uppercase ASCII chars, e.g. the Motu for 5, `Ima`. These are lowercased in the
  output, based on the assumption that they are errors.
* The char `ţ` is replaced with `ʈ`. The only word affected is the Paiwan
  (Kulalao) for seven, `piţuʔ`.
* The char `ố` is replaced with `o`. The only word affected is the Cebuano for
  blood, `dugố`.

The original transcriptions are accessible in the notes column.



