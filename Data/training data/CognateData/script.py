import argparse
import csv
import os.path



class Harvester:
	"""
	Named after Dune's spice harvesters, this class handles the extracting of
	words out of the input data file given.
	"""
	
	def __init__(self):
		"""
		Constructor.
		"""
		self.f = None
		self.t = None
		
		self.langs = []
		self.words = []
		self.glosses_order = []
		
		self.matrix = {}
		self.glosses = {}
		self.trans = {}
		self.iso_codes = {}
		self.notes = {}
	
	
	def harvest(self, f, t):
		"""
		Orchestrates the processing of the input file given.
		Populates the self.words list.
		"""
		self.f = f
		self.t = t
		
		self.f.readline()
		self.f.readline()
		self._process_glosses()
		
		self._process_languages()
		
		self.f.readline()
		self.f.readline()
		self._process_matrix()
		
		self._process_transcriptions()
		
		for gloss_id, row in self.matrix.items():
			for key, cognate_class in enumerate(row):
				if cognate_class == 0:
					continue
				
				lang = self.langs[key]
				
				if lang in self.iso_codes:
					iso_code = self.iso_codes[lang]
				else:
					iso_code = ''
				
				if gloss_id not in self.trans[lang]:
					continue
				
				if gloss_id in self.notes[lang]:
					notes = self.notes[lang][gloss_id]
				else:
					notes = ''
				
				self.words.append({
					'language': lang,
					'iso_code': iso_code,
					'gloss': self.glosses[gloss_id],
					'local_id': gloss_id,
					'transcription': self.trans[lang][gloss_id],
					'cognate_class': cognate_class,
					'notes': notes
				})
		
		self.t.test_words(self.words)
	
	
	def _process_glosses(self):
		"""
		Processes the first chunk of the input file.
		Note: Mayan and Athapaskan have slightly different glosses format.
		Note: glosses with ID of 0 are not included in the output but take part
		in the input matrix so these are counted in self.glosses_order.
		"""
		for line in self.f:
			line = line.strip()
			if line == '-1':
				break
			
			if line.find('\t') > 0:
				line = line.split('\t')[0]
				line = line.strip()
			
			pair = line.split(maxsplit=1)
			assert len(pair) == 2
			
			if pair[0].endswith('.'):
				pair[0] = pair[0][:-1]
			gloss_id = int(pair[0])
			
			if gloss_id != 0:
				self.glosses[gloss_id] = pair[1]
			
			self.glosses_order.append(gloss_id)
		
		self.t.test_glosses(self.glosses)
	
	
	def _process_languages(self):
		"""
		Processes the second chunk of the input file.
		"""
		for line in self.f:
			line = line.strip()
			if line == '':
				break
			
			self.langs.append(line)
		
		self.t.test_languages(self.langs)
	
	
	def _process_matrix(self):
		"""
		Processes the third chunk of the input file.
		Note: the matrix format is inconsistent across files, so this is
		outsourced to the Tests classes.
		"""
		matrix_width = len(self.langs) * 2
		
		index = -1
		
		for line in self.f:
			line = line.rstrip()
			if line.strip() == 'X':
				break
			
			index = index + 1
			
			# identify gloss
			gloss_id = self.glosses_order[index]
			
			if gloss_id == 0:
				continue
			
			# process cognacy data
			row = self.t.extract_matrix_row(line)
			
			# add the processed row to our matrix
			self.matrix[gloss_id] = row
		
		self.t.test_matrix(self.matrix)
	
	
	def _process_transcriptions(self):
		"""
		Processes the fourth chunk of the input file.
		Also harvests the notes, if there are such.
		Note: 'XXX' means that the word is not attested.
		Note: Initial '%' denotes a loanword.
		"""
		for lang in self.langs:
			self.trans[lang] = {}
			self.notes[lang] = {}
		
		lang = None
		look_for_iso = False
		
		for line in self.f:
			line = line.strip()
			if line == '':
				continue
			
			# start of language block
			if line.find('{') > 0 and line[-1] == '}':
				lang = line[:line.find('{')]
				look_for_iso = True
				continue
			
			# second line of language block header
			if look_for_iso:
				assert len(line) >= 41
				iso_code = line[38:41].strip()
				if iso_code:
					self.iso_codes[lang] = iso_code
				look_for_iso = False
				continue
			
			# word line
			if line[0].isdigit() and line.find('\t') > 0:
				left, right = line.split('\t')
				
				gloss_id = int(left.split()[0])
				if gloss_id == 0:
					continue
				
				right = right.split('//')
				notes = []
				
				transcription = right[0].strip()
				if transcription == 'XXX':
					continue
				
				if transcription.find(',') > 0:
					transcription, alt = transcription.split(',', 1)
					notes.append('also: ' + alt.strip())
				
				self.trans[lang][gloss_id] = transcription
				
				if len(right) > 1 and right[1].strip() != '':
					notes.append(right[1].strip())
				
				if notes:
					self.notes[lang][gloss_id] = '; '.join(notes)
		
		self.t.test_transcriptions(self.trans)
	
	
	def add_global_gloss_ids(self, glossary_file):
		"""
		Enriches the self.words by adding global_id field.
		The argument is the file handler of the local glossary.
		"""
		glossary = {}  # gloss: (local_id, global_id)
		
		reader = csv.reader(glossary_file, delimiter='\t')
		next(reader)
		
		for line in reader:
			glossary[line[1]] = (int(line[0]), int(line[3]))
		
		for word in self.words:
			assert word['local_id'] == glossary[word['gloss']][0]
			word['global_id'] = glossary[word['gloss']][1]



class AthapaskanHarvester(Harvester):
	"""
	Athapaskan data is sufficiently different to have a Harvester on its own.
	"""
	
	def harvest(self, f, t):
		"""
		Orchestrates the processing of the input file given.
		Populates the self.words list.
		"""
		self.f = f
		self.t = t
		
		self.f.readline()
		self.f.readline()
		self._process_glosses()
		
		self._process_languages()
		
		self.f.readline()
		self.f.readline()
		self._process_matrix()
		
		self._process_transcriptions()
		
		for gloss_id, row in self.matrix.items():
			for cognate_class, cognate_langs in enumerate(row):
				for lang in cognate_langs:
					if lang in self.iso_codes:
						iso_code = self.iso_codes[lang]
					else:
						iso_code = ''
					
					if gloss_id not in self.trans[lang]:
						continue
					
					if gloss_id in self.notes[lang]:
						notes = self.notes[lang][gloss_id]
					else:
						notes = ''
					
					self.words.append({
						'language': lang,
						'iso_code': iso_code,
						'gloss': self.glosses[gloss_id],
						'local_id': gloss_id,
						'transcription': self.trans[lang][gloss_id],
						'cognate_class': cognate_class,
						'notes': notes
					})
		
		self.t.test_words(self.words)
	
	
	def _process_matrix(self):
		"""
		Processes the third chunk of the input file.
		"""
		data = {}  # (lang, lang): [gloss_id, ...]
		sets = {}  # gloss_id: [] of set(lang, ...)
		
		# extract the data
		for lang_one in self.langs:
			for lang_two in self.langs:
				if lang_one == lang_two:
					continue
				
				if (lang_two, lang_one) in data.keys():
					continue
				
				head = (lang_one, lang_two)
				
				line = self.f.readline()
				line = line.rstrip()
				
				assert line[0].upper() in (lang_one[0], ' ')
				assert line[1].upper() == lang_two[0]
				assert (len(line) - 2) % 3 == 0
				
				row = []
				for i in range(2, len(line) -2, 3):
					gloss_id = int(line[i:i+3])
					if gloss_id in self.glosses:
						row.append(gloss_id)
				
				data[head] = row
		
		self.t.test_matrix_data(data)
		
		# construct the matrix
		for gloss_id in self.glosses:
			sets[gloss_id] = []
			
			for pair in data:
				if gloss_id not in data[pair]:
					continue
				
				for s in sets[gloss_id]:
					if pair[0] in s:
						s.add(pair[1])
						break
					if pair[1] in s:
						s.add(pair[0])
						break
				else:
					sets[gloss_id].append(set(pair))
		
		self.matrix = sets
		self.t.test_matrix(self.matrix)



"""
Each input file has its own Tests class which contains its assertions and
format specifics. These classes are not supposed to be instantiated.
"""
class MixeZoqueTests:
	"""
	Number of words with cognate class zero: 7.
	"""
	def extract_matrix_row(line):
		cognacy_data = line[-20:]
		assert len(cognacy_data) == 20
		
		row = []
		for i in range(0, 20, 2):
			row.append(int(cognacy_data[i:i+2]))
		
		assert len(row) == 10
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 100
		assert glosses[1] == 'I'
		assert glosses[9] == 'all'
		assert glosses[89] == 'yellow'
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 10
		assert langs[0] == 'NORTH_HIGHLAND_MIXE'
		assert langs[9] == 'CHIAPAS_ZOQUE'
	
	def test_matrix(matrix):
		assert len(matrix) == 100
		for index, line in matrix.items():
			assert len(line) == 10
		
		assert matrix[1] == [1, 1, 1, 1, 1, 1, 1, 1, 2, 1]
		assert matrix[9] == [1, 2, 2, 3, 4, 5, 6, 7, 8, 5]
		assert matrix[89] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		assert matrix[100] == [1, 1, 1, 2, 1, 2, 2, 2, 2, 2]
	
	def test_transcriptions(trans):
		assert len(trans) == 10
		for lang in trans:
			assert len(trans[lang]) <= 100
		
		assert trans['NORTH_HIGHLAND_MIXE'][1] == '3c'
		assert trans['NORTH_HIGHLAND_MIXE'][9] == 'n3hum'
		assert trans['NORTH_HIGHLAND_MIXE'][89] == 'puc'
		assert trans['NORTH_HIGHLAND_MIXE'][100] == 'S3'
		
		assert trans['CHIAPAS_ZOQUE'][1] == '3h'
		assert trans['CHIAPAS_ZOQUE'][9] == 'mumu'
		assert trans['CHIAPAS_ZOQUE'][89] == 'puc3'
		assert trans['CHIAPAS_ZOQUE'][100] == 'n3y'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) == 3
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'NORTH_HIGHLAND_MIXE', 'iso_code': 'mto',
				'gloss': 'I', 'local_id': 1,
				'transcription': '3c', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'NORTH_HIGHLAND_MIXE', 'iso_code': 'mto',
				'gloss': 'all', 'local_id': 9,
				'transcription': 'n3hum', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'NORTH_HIGHLAND_MIXE', 'iso_code': 'mto',
				'gloss': 'yellow', 'local_id': 89,
				'transcription': 'puc', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'NORTH_HIGHLAND_MIXE', 'iso_code': 'mto',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'S3', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'CHIAPAS_ZOQUE', 'iso_code': 'zoc',
				'gloss': 'I', 'local_id': 1,
				'transcription': '3h', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'CHIAPAS_ZOQUE', 'iso_code': 'zoc',
				'gloss': 'all', 'local_id': 9,
				'transcription': 'mumu', 'cognate_class': 5, 'notes': '' } in words
		assert {'language': 'CHIAPAS_ZOQUE', 'iso_code': 'zoc',
				'gloss': 'yellow', 'local_id': 89,
				'transcription': 'puc3', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'CHIAPAS_ZOQUE', 'iso_code': 'zoc',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'n3y', 'cognate_class': 2, 'notes': '' } in words



class AthapaskanTests:
	def test_glosses(glosses):
		assert len(glosses) == 34
		assert glosses[1] == 'I'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 15
		assert langs[0] == 'NAVAHO'
		assert langs[14] == 'GALICE'
	
	def test_matrix_data(data):
		assert len(data) == 105
		assert data[('NAVAHO', 'CHIRICAHUA')] == []
		assert data[('SARCEE', 'GALICE')] == [30, 43, 47, 57, 61, 74, 75, 77]
	
	def test_matrix(matrix):
		assert matrix[1] == []
		assert matrix[2] == []
		assert matrix[11] == [
			set(['NAVAHO', 'KATO', 'MATTOLE', 'HUPA_2'])
		]
		assert False
	
	def test_transcriptions(trans):
		assert False
	
	def test_words(words):
		assert False



class AfrasianTests:
	def extract_matrix_row(line):
		line = line.rsplit(maxsplit=1)[0]
		
		line = line[-75:]
		assert len(line) == 75
		
		row = []
		for i in range(0, 75, 3):
			row.append(int(line[i:i+3]))
		
		assert len(row) == 25
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 40
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[30] == 'blood'
		assert glosses[75] == 'water'
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 25
		assert langs[0] == 'AKKADIAN'
		assert langs[24] == 'KAFFA'
	
	def test_matrix(matrix):
		assert len(matrix) == 40
		for index, line in matrix.items():
			assert len(line) == 25
		
		assert 0 not in matrix
		assert matrix[1] == [21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 23, 23, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 24]
		assert 9 not in matrix
		assert matrix[30] == [81, 81, 81, 81, 81, 81, 81, 81, 81, 82, 82, 82, 83, 83, 81, 81, 83, 81, 81, 83, 81, 84, 85, -2, 81]
		assert matrix[75] == [1, 1, 1, 1, 1, 1, 1, -2, 1, 1, 1, 2, 1, 1, 3, 3, 3, 3, 3, 2, 3, 3, 4, 1, 5]
		assert 89 not in matrix
		assert matrix[100] == [81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 81, 82, 82, -1, 81, 81, 81, 81, 81, 81, -2, 83, 84, 85]
	
	def test_transcriptions(trans):
		assert len(trans) == 25
		
		assert len(trans['AKKADIAN']) == 0
		assert len(trans['BIBLICAL_HEBREW']) == 0
		assert len(trans['EGYPTIAN']) == 0
		assert len(trans['COPTIC']) == 0
		
		assert len(trans['SYRIAC_2']) == 40
		assert trans['SYRIAC_2'][1] == 'ena'
		assert trans['SYRIAC_2'][30] == 'd3m'
		assert trans['SYRIAC_2'][75] == 'maye'
		assert trans['SYRIAC_2'][100] == 'S3m'
		
		assert len(trans['KAFFA']) == 40
		assert trans['KAFFA'][1] == 'ta'
		assert trans['KAFFA'][30] == 'damo'
		assert trans['KAFFA'][75] == 'aCo'
		assert trans['KAFFA'][100] == 'Sigo'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
			assert word['language'] not in (
				'AKKADIAN', 'BIBLICAL_HEBREW', 'EGYPTIAN', 'COPTIC'
			)
		
		assert {'language': 'SYRIAC_2', 'iso_code': 'syc',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'ena', 'cognate_class': 21, 'notes': '' } in words
		assert {'language': 'SYRIAC_2', 'iso_code': 'syc',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'd3m', 'cognate_class': 81, 'notes': '' } in words
		assert {'language': 'SYRIAC_2', 'iso_code': 'syc',
				'gloss': 'water', 'local_id': 75,
				'transcription': 'maye', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'SYRIAC_2', 'iso_code': 'syc',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'S3m', 'cognate_class': 81, 'notes': '' } in words
		
		assert {'language': 'KAFFA', 'iso_code': 'kbr',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'ta', 'cognate_class': 24, 'notes': '' } in words
		assert {'language': 'KAFFA', 'iso_code': 'kbr',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'damo', 'cognate_class': 81, 'notes': '' } in words
		assert {'language': 'KAFFA', 'iso_code': 'kbr',
				'gloss': 'water', 'local_id': 75,
				'transcription': 'aCo', 'cognate_class': 5, 'notes': '' } in words
		assert {'language': 'KAFFA', 'iso_code': 'kbr',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'Sigo', 'cognate_class': 85, 'notes': '' } in words



class HuonTests:
	def extract_matrix_row(line):
		line = line.rsplit(maxsplit=1)[0]
		
		line = line[-28:]
		assert len(line) == 28
		
		row = []
		for i in range(0, 28, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 14
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 84
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[30] == 'blood'
		assert glosses[31] == 'bone'
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 14
		assert langs[0] == 'KATE'
		assert langs[13] == 'MOMOLILI'
	
	def test_matrix(matrix):
		assert len(matrix) == 84
		for index, line in matrix.items():
			assert len(line) == 14
		
		assert 0 not in matrix
		assert matrix[1] == [1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]
		assert matrix[30] == [1, 2, 1, 1, 1, 1, 1, 1, 3, 1, 1, 4, 1, 1]
		assert matrix[31] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 3, 1]
		assert matrix[100] == [1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 3, 7]
	
	def test_transcriptions(trans):
		assert len(trans) == 14
		
		assert len(trans['KATE']) == 84
		assert trans['KATE'][1] == 'no'
		assert trans['KATE'][30] == 'so7'
		assert trans['KATE'][31] == 'sie7'
		assert trans['KATE'][100] == 'coNe'
		
		assert len(trans['MOMOLILI']) == 84
		assert trans['MOMOLILI'][1] == 'na'
		assert trans['MOMOLILI'][30] == 'sip'
		assert trans['MOMOLILI'][31] == 'siet'
		assert trans['MOMOLILI'][100] == 'kot'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'KATE', 'iso_code': 'kmg',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'no', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'KATE', 'iso_code': 'kmg',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'so7', 'cognate_class': 1, 'notes': 'stem, "its blood"' } in words
		assert {'language': 'KATE', 'iso_code': 'kmg',
				'gloss': 'bone', 'local_id': 31,
				'transcription': 'sie7', 'cognate_class': 1, 'notes': 'stem, "its bone"' } in words
		assert {'language': 'KATE', 'iso_code': 'kmg',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'coNe', 'cognate_class': 1, 'notes': 'stem, "its name"' } in words
		
		assert {'language': 'MOMOLILI', 'iso_code': 'mci',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'na', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'MOMOLILI', 'iso_code': 'mci',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'sip', 'cognate_class': 1, 'notes': 'stem, "its blood"' } in words
		assert {'language': 'MOMOLILI', 'iso_code': 'mci',
				'gloss': 'bone', 'local_id': 31,
				'transcription': 'siet', 'cognate_class': 1, 'notes': 'stem, "its bone"' } in words
		assert {'language': 'MOMOLILI', 'iso_code': 'mci',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'kot', 'cognate_class': 7, 'notes': 'stem, "its name"' } in words



class KadaiTests:
	def extract_matrix_row(line):
		line = line[-24:]
		assert len(line) == 24
		
		row = []
		for i in range(0, 24, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 12
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 40
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 12
		assert langs[0] == 'SIAMESE'
		assert langs[11] == 'LI_BAODING'
	
	def test_matrix(matrix):
		assert len(matrix) == 40
		for index, line in matrix.items():
			assert len(line) == 12
		
		assert 0 not in matrix
		assert matrix[1] == [1, 2, 2, 2, 2, 3, 2, 2, 2, 4, 2, 2]
		assert matrix[2] == [1, 3, 3, 3,-1,-1,-1,-1, 3, 3, 3, 3]
		assert 9 not in matrix
		assert matrix[30] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		assert 89 not in matrix
		assert matrix[100] == [-1,-2,-2,-1, 1, 1, 1, 1, 2, 1, 3, 3]
	
	def test_transcriptions(trans):
		assert len(trans) == 12
		
		assert len(trans['SIAMESE']) == 38
		assert trans['SIAMESE'][1] == 'ku'
		assert trans['SIAMESE'][2] == 'muN'
		assert 9 not in trans['SIAMESE']
		assert trans['SIAMESE'][30] == 'luat'
		assert 89 not in trans['SIAMESE']
		assert trans['SIAMESE'][100] == 'ch~u'
		
		assert len(trans['LI_BAODING']) == 38
		assert trans['LI_BAODING'][1] == 'hou'
		assert trans['LI_BAODING'][2] == 'me3'
		assert 9 not in trans['LI_BAODING']
		assert trans['LI_BAODING'][30] == 'Laty~'
		assert 89 not in trans['LI_BAODING']
		assert trans['LI_BAODING'][100] == 'ph~eN'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'SIAMESE', 'iso_code': 'tha',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'ku', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'SIAMESE', 'iso_code': 'tha',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'muN', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'SIAMESE', 'iso_code': 'tha',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'luat', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'SIAMESE', 'iso_code': 'tha',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'ch~u', 'cognate_class': -1, 'notes': '' } in words
		
		assert {'language': 'LI_BAODING', 'iso_code': 'lic',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'hou', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'LI_BAODING', 'iso_code': 'lic',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'me3', 'cognate_class': 3, 'notes': '' } in words
		assert {'language': 'LI_BAODING', 'iso_code': 'lic',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'Laty~', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'LI_BAODING', 'iso_code': 'lic',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'ph~eN', 'cognate_class': 3, 'notes': '' } in words



class KamasauTests:
	def extract_matrix_row(line):
		line = line[-16:]
		assert len(line) == 16
		
		row = []
		for i in range(0, 16, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 8
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 36
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 8
		assert langs[0] == 'TRING'
		assert langs[7] == 'SAMAP'
	
	def test_matrix(matrix):
		assert len(matrix) == 36
		for index, line in matrix.items():
			assert len(line) == 8
		
		assert 0 not in matrix
		assert matrix[1] == [1, 1, 1, 1, 1, 1, 0, 1]
		assert matrix[2] == [1, 1, 1, 1, 1, 1, 0, 2]
		assert 9 not in matrix
		assert matrix[30] == [1, 1, 1, 1, 2, 1, 1, 2]
		assert 89 not in matrix
		assert matrix[100] == [1, 1, 1, 1, 1, 1, 0, 1]
	
	def test_transcriptions(trans):
		assert len(trans) == 8
		
		assert len(trans['TRING']) == 36
		assert trans['TRING'][1] == 'Ne'
		assert trans['TRING'][2] == 'nu'
		assert 9 not in trans['TRING']
		assert trans['TRING'][30] == 'yab3'
		assert 89 not in trans['TRING']
		assert trans['TRING'][100] == '5amb'
		
		assert len(trans['SAMAP']) == 34
		assert trans['SAMAP'][1] == 'Na'
		assert trans['SAMAP'][2] == 'ninde'
		assert 9 not in trans['SAMAP']
		assert trans['SAMAP'][30] == 'Nainde'
		assert 89 not in trans['SAMAP']
		assert trans['SAMAP'][100] == '5amb'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'TRING', 'iso_code': 'kms',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'Ne', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'TRING', 'iso_code': 'kms',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'nu', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'TRING', 'iso_code': 'kms',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'yab3', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'TRING', 'iso_code': 'kms',
				'gloss': 'name', 'local_id': 100,
				'transcription': '5amb', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'SAMAP', 'iso_code': 'ele',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'Na', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'SAMAP', 'iso_code': 'ele',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'ninde', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'SAMAP', 'iso_code': 'ele',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'Nainde', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'SAMAP', 'iso_code': 'ele',
				'gloss': 'die', 'local_id': 61,
				'transcription': 'gureN nand', 'cognate_class': 2, 'notes': 'also: nita; = "he dies, I die"' } in words
		assert {'language': 'SAMAP', 'iso_code': 'ele',
				'gloss': 'name', 'local_id': 100,
				'transcription': '5amb', 'cognate_class': 1, 'notes': '' } in words



class LoloBurmeseTests:
	"""
	Number of words with cognate class zero: 1.
	"""
	def extract_matrix_row(line):
		line = line[-30:]
		assert len(line) == 30
		
		row = []
		for i in range(0, 30, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 15
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 40
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 15
		assert langs[0] == 'BURMESE'
		assert langs[14] == 'NAXI'
	
	def test_matrix(matrix):
		assert len(matrix) == 40
		for index, line in matrix.items():
			assert len(line) == 15
		
		assert 0 not in matrix
		assert matrix[1] == [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
		assert matrix[2] == [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
		assert 9 not in matrix
		assert matrix[18] == [1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		assert matrix[30] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		assert 89 not in matrix
		assert matrix[100] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
	
	def test_transcriptions(trans):
		assert len(trans) == 15
		
		assert len(trans['BURMESE']) == 40
		assert trans['BURMESE'][1] == 'kyw$antau'
		assert trans['BURMESE'][2] == 'TaN'
		assert 9 not in trans['BURMESE']
		assert trans['BURMESE'][30] == 'sw~e'
		assert 89 not in trans['BURMESE']
		assert trans['BURMESE'][100] == 'ama5'
		
		assert len(trans['NAXI']) == 38
		assert trans['NAXI'][1] == 'N3'
		assert trans['NAXI'][2] == 'nv'
		assert 9 not in trans['NAXI']
		assert trans['NAXI'][30] == 'sa'
		assert 89 not in trans['NAXI']
		assert trans['NAXI'][100] == 'mi'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'BURMESE', 'iso_code': 'mya',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'kyw$antau', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'BURMESE', 'iso_code': 'mya',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'TaN', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'BURMESE', 'iso_code': 'mya',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'sw~e', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'BURMESE', 'iso_code': 'mya',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'ama5', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'NAXI', 'iso_code': 'nbf',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'N3', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'NAXI', 'iso_code': 'nbf',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'nv', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'NAXI', 'iso_code': 'nbf',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'sa', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'NAXI', 'iso_code': 'nbf',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'mi', 'cognate_class': 1, 'notes': '' } in words



class MayanTests:
	"""
	Number of words with cognate class zero: 12.
	"""
	def extract_matrix_row(line):
		line = line[-60:]
		assert len(line) == 60
		
		row = []
		for i in range(0, 60, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 30
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 100
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[9] == 'all'
		assert glosses[89] == 'yellow'
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 30
		assert langs[0] == 'HUASTEC'
		assert langs[29] == 'LACANDON'
	
	def test_matrix(matrix):
		assert len(matrix) == 100
		
		for index, line in matrix.items():
			assert len(line) == 30
		
		assert 0 not in matrix
		assert matrix[1] == [1, 0, 6, 1, 0, 1, 2, 1, 1, 1, 3, 2, 1, 3, 1, 2, 1, 4, 4, 1, 3, 0, 5, 5, 0, 1, 1, 1, 1, 0]
		assert matrix[9] == [5, 0, 6, 1, 7, 8, 1, 1, 2, 9, 2, 2, 3, 3, 3, 3, 3,10,11, 3,12,13,14, 0,15,16,17, 4, 4,18]
		assert matrix[32] == [1, 0, 2,-1, 0,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, 3,-2, 0, 4, 5, 6,-1, 7, 8]
		assert matrix[68] == [3, 0, 4, 5, 6, 7, 1, 1, 8, 9,10, 2, 2, 2,11,12,13, 2,14,15,16,17,18,19,20,21,22,23, 3,24]
		assert matrix[89] == [2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		assert matrix[98] == [7, -1, 1, 8, 1, 9, 6, 6,10, 4, 4,11, 2, 2, 3, 3, 3, 4, 3, 3,12, 0,13,14, 5, 5, 5,15, 5,16]
		assert matrix[100] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 2, 2, 2, 2, 2, 2, 2]
	
	def test_transcriptions(trans):
		assert len(trans) == 30
		
		assert len(trans['HUASTEC']) == 100
		assert trans['HUASTEC'][1] == 'in'
		assert trans['HUASTEC'][9] == 'tala7'
		assert trans['HUASTEC'][89] == 'manu7'
		assert trans['HUASTEC'][100] == 'bih'
		
		assert len(trans['LACANDON']) == 87
		assert 1 not in trans['LACANDON']
		assert trans['LACANDON'][9] == 'puri7'
		assert trans['LACANDON'][89] == 'k"3n'
		assert trans['LACANDON'][100] == 'k"aba7'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'HUASTEC', 'iso_code': 'hva',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'in', 'cognate_class': 1, 'notes': 'also: nana7' } in words
		assert {'language': 'HUASTEC', 'iso_code': 'hva',
				'gloss': 'all', 'local_id': 9,
				'transcription': 'tala7', 'cognate_class': 5, 'notes': 'also: patal' } in words
		assert {'language': 'HUASTEC', 'iso_code': 'hva',
				'gloss': 'yellow', 'local_id': 89,
				'transcription': 'manu7', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'HUASTEC', 'iso_code': 'hva',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'bih', 'cognate_class': 1, 'notes': '' } in words



class MiaoYaoTests:
	def extract_matrix_row(line):
		line = line[-12:]
		assert len(line) == 12
		
		row = []
		for i in range(0, 12, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 6
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 40
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert langs == [	'HMU', 'XIANGXI_HMONG', 'HMONG_NJUA',
							'BUNU', 'SHE_CHINA', 'YAO'	]
	
	def test_matrix(matrix):
		assert len(matrix) == 40
		
		for index, line in matrix.items():
			assert len(line) == 6
		
		assert 0 not in matrix
		assert matrix[1] == [1, 1, 2, 3, 1, 4]
		assert matrix[2] == [1, 1, 2, 2, 1, 1]
		assert 9 not in matrix
		assert matrix[30] == [1, 1, 1, 1, 1, 1]
		assert 89 not in matrix
		assert matrix[96] == [-1, -1, -1, -1, -1, -1]
		assert matrix[100] == [1, 1, 1, 1, 2, 1]
	
	def test_transcriptions(trans):
		assert len(trans) == 6
		
		assert len(trans['HMU']) == 36
		assert trans['HMU'][1] == 'vi'
		assert trans['HMU'][2] == 'mon'
		assert 9 not in trans['HMU']
		assert trans['HMU'][30] == 'Th~n'
		assert 75 not in trans['HMU']
		assert 89 not in trans['HMU']
		assert trans['HMU'][100] == 'zanpi'
		
		assert len(trans['YAO']) == 38
		assert trans['YAO'][1] == 'ye'
		assert trans['YAO'][2] == 'mw~ei'
		assert 9 not in trans['YAO']
		assert trans['YAO'][30] == 'cy~am'
		assert 89 not in trans['YAO']
		assert trans['YAO'][100] == 'meNbw~o'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'HMU', 'iso_code': 'hea',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'vi', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'HMU', 'iso_code': 'hea',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'mon', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'HMU', 'iso_code': 'hea',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'Th~n', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'HMU', 'iso_code': 'hea',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'zanpi', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'YAO', 'iso_code': 'ium',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'ye', 'cognate_class': 4, 'notes': '' } in words
		assert {'language': 'YAO', 'iso_code': 'ium',
				'gloss': 'you', 'local_id': 2,
				'transcription': 'mw~ei', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'YAO', 'iso_code': 'ium',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'cy~am', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'YAO', 'iso_code': 'ium',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'meNbw~o', 'cognate_class': 1, 'notes': '' } in words



class MonKhmerTests:
	"""
	Number of words with cognate class zero: 5.
	"""
	def extract_matrix_row(line):
		line = line[-32:]
		assert len(line) == 32
		
		row = []
		for i in range(0, 32, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 16
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 100
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you'
		assert glosses[9] == 'all'
		assert glosses[30] == 'blood'
		assert glosses[89] == 'yellow'
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 16
		assert langs[0] == 'JEH'
		assert langs[15] == 'MUNDARI'
	
	def test_matrix(matrix):
		assert len(matrix) == 100
		
		for index, line in matrix.items():
			assert len(line) == 16
		
		assert matrix[1] == [1, 2, 2, 3,-1, 2, 2, 4, 0, 2, 1, 1, 1, 2,-2, 2]
		assert matrix[2] == [1, 2, 1, 1, 1, 3, 3, 4, 1, 2, 1, 1, 1, 1, 1, 1]
		assert matrix[9] == [0, 0, 0, 2, 0, 3,-1, 1, 4, 5,-2, 6, 7, 8, 9,-3]
		assert matrix[89] == [1, 1, 2, 8, 8, 2, 3, 9, 0, 4, 9, 5, 9, 9, 6, 7]
		assert matrix[100] == [1,-1, 2, 3,-3,-2, 0, 4, 4, 4, 5,-6,-6, 0, 3, 7]
	
	def test_transcriptions(trans):
		assert len(trans) == 16
		
		assert len(trans['JEH']) == 88
		assert trans['JEH'][1] == 'aut'
		assert 9 not in trans['JEH']
		assert trans['JEH'][89] == 'driN'
		assert trans['JEH'][100] == 't3li7'
		
		assert len(trans['MUNDARI']) == 100
		assert trans['MUNDARI'][1] == 'ain'
		assert trans['MUNDARI'][9] == 'soben'
		assert trans['MUNDARI'][89] == 'sa saN'
		assert trans['MUNDARI'][100] == 'nutum'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'JEH', 'iso_code': 'jeh',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'aut', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'JEH', 'iso_code': 'jeh',
				'gloss': 'yellow', 'local_id': 89,
				'transcription': 'driN', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'JEH', 'iso_code': 'jeh',
				'gloss': 'name', 'local_id': 100,
				'transcription': 't3li7', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'MUNDARI', 'iso_code': 'unr',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'ain', 'cognate_class': 2, 'notes': '' } in words
		assert {'language': 'MUNDARI', 'iso_code': 'unr',
				'gloss': 'all', 'local_id': 9,
				'transcription': 'soben', 'cognate_class': -3, 'notes': '' } in words
		assert {'language': 'MUNDARI', 'iso_code': 'unr',
				'gloss': 'yellow', 'local_id': 89,
				'transcription': 'sa saN', 'cognate_class': 7, 'notes': '' } in words
		assert {'language': 'MUNDARI', 'iso_code': 'unr',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'nutum', 'cognate_class': 7, 'notes': 'also: num' } in words



class MorobeTests:
	"""
	Number of words with cognate class zero: 1.
	"""
	def extract_matrix_row(line):
		line = line[-110:]
		assert len(line) == 110
		
		row = []
		for i in range(0, 110, 2):
			row.append(int(line[i:i+2]))
		
		assert len(row) == 55
		return row
	
	def test_glosses(glosses):
		assert len(glosses) == 38
		assert 0 not in glosses
		assert glosses[1] == 'I'
		assert glosses[2] == 'you (thou)'
		assert glosses[3] == 'we (excl.)'
		assert 9 not in glosses
		assert glosses[30] == 'blood'
		assert 89 not in glosses
		assert glosses[100] == 'name'
	
	def test_languages(langs):
		assert len(langs) == 55
		assert langs[0] == 'WAGAU'
		assert langs[54] == 'GEDAGED'
	
	def test_matrix(matrix):
		assert len(matrix) == 38
		
		for index, line in matrix.items():
			assert len(line) == 55
		
		assert matrix[1] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 5,11,11, 6, 7, 1, 8,13]
		assert matrix[3] == [1, 2, 2, 3, 3, 4, 4, 5, 2, 1, 3, 5, 4, 5, 4, 4, 4, 4, 4,13,14, 0, 0,27, 0, 4,26, 4,28, 4, 4, 6, 7, 8, 9, 3,10,11, 0,15, 7, 1, 0, 0, 0, 0, 0, 0,25,27,16,16,17,18, 7]
		assert matrix[41] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8,11, 8, 8, 7, 7, 8,11,11, 8,11,21,23,11,11, 8, 8, 2, 1, 3, 4, 5, 8,12, 9, 8, 9, 8, 9, 8, 8,10, 8,10,13,14,15,16,22]
		assert matrix[100] == [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 6, 7, 2,17, 2, 2, 2, 2, 2, 2, 2, 3,20,20, 1, 1, 1, 2,20, 8,19,20,19,18,19,21,21,10,22,22, 9,10,11,11,16]
	
	def test_transcriptions(trans):
		assert len(trans) == 55
		
		assert len(trans['WAGAU']) == 38
		assert trans['WAGAU'][1] == 'keh'
		assert trans['WAGAU'][2] == 'oN'
		assert trans['WAGAU'][30] == 'os'
		assert trans['WAGAU'][100] == 'are'
		
		assert len(trans['GEDAGED']) == 38
		assert trans['GEDAGED'][1] == 'Na'
		assert trans['GEDAGED'][2] == 'o'
		assert trans['GEDAGED'][30] == 'daz'
		assert trans['GEDAGED'][100] == 'nean'
	
	def test_words(words):
		for word in words:
			assert len(word['language']) > 0
			assert len(word['iso_code']) in (0, 3)
			assert len(word['gloss']) > 0
			assert type(word['local_id']) is int
			assert len(word['transcription']) > 0
			assert word['transcription'] != 'XXX'
			assert word['transcription'].find(',') == -1
			assert type(word['cognate_class']) is int
			assert word['cognate_class'] != 0
		
		assert {'language': 'WAGAU', 'iso_code': 'bzh',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'keh', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'WAGAU', 'iso_code': 'bzh',
				'gloss': 'you (thou)', 'local_id': 2,
				'transcription': 'oN', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'WAGAU', 'iso_code': 'bzh',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'os', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'WAGAU', 'iso_code': 'bzh',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'are', 'cognate_class': 1, 'notes': '' } in words
		
		assert {'language': 'GEDAGED', 'iso_code': 'gdd',
				'gloss': 'I', 'local_id': 1,
				'transcription': 'Na', 'cognate_class': 13, 'notes': '' } in words
		assert {'language': 'GEDAGED', 'iso_code': 'gdd',
				'gloss': 'you (thou)', 'local_id': 2,
				'transcription': 'o', 'cognate_class': 1, 'notes': '' } in words
		assert {'language': 'GEDAGED', 'iso_code': 'gdd',
				'gloss': 'blood', 'local_id': 30,
				'transcription': 'daz', 'cognate_class': 9, 'notes': '' } in words
		assert {'language': 'GEDAGED', 'iso_code': 'gdd',
				'gloss': 'name', 'local_id': 100,
				'transcription': 'nean', 'cognate_class': 16, 'notes': '' } in words



"""
Handles the command-line interface.
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'Harvests the data of the given input file, '
		'optionally enriches it by adding global gloss IDs, '
		'and generates an output file.'
	))
	parser.add_argument('input_file', help=(
		'The raw data input file.'
	))
	parser.add_argument('--local', action='store_true', help=(
		'Whether to enrich the ouput with global gloss IDs.'
	))
	args = parser.parse_args()
	
	lang_family = os.path.split(args.input_file)[-1].split('.')[0]
	script_dir = os.path.dirname(os.path.realpath(__file__))
	
	
	# harvest
	tester = locals()[lang_family.replace('-', '') + 'Tests']
	
	with open(args.input_file, 'r', encoding='utf-8') as f:
		if lang_family == 'Athapaskan':
			harvester = AthapaskanHarvester()
		else:
			harvester = Harvester()
		
		harvester.harvest(f, tester)
	
	
	# enrich with global ids
	if not args.local:
		glossary_file = os.path.join(
			script_dir,
			'glossary_local',
			lang_family+'_glossary.tsv'
		)
		
		with open(glossary_file, 'r') as f:
			harvester.add_global_gloss_ids(f)
	
	
	# write output
	output_file = os.path.join(
		script_dir,
		'output',
		lang_family + '.tsv'
	)
	
	with open(output_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter='\t')
		
		if args.local:
			writer.writerow([
				'language', 'iso_code',
				'gloss', 'local_id',
				'transcription', 'cognate_class', 'notes'
			])
			for word in harvester.words:
				writer.writerow([
					word['language'],
					word['iso_code'],
					word['gloss'],
					word['local_id'],
					word['transcription'],
					word['cognate_class'],
					word['notes']
				])
		
		else:
			writer.writerow([
				'language', 'iso_code',
				'gloss', 'global_id', 'local_id',
				'transcription', 'cognate_class', 'notes'
			])
			for word in harvester.words:
				writer.writerow([
					word['language'],
					word['iso_code'],
					word['gloss'],
					word['global_id'],
					word['local_id'],
					word['transcription'],
					word['cognate_class'],
					word['notes']
				])



