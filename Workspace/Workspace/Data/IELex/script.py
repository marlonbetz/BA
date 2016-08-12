import argparse
import csv
import os.path



class Harvester:
	"""
	Named after Dune's spice harvesters.
	"""
	
	def __init__(self):
		"""
		Constructor.
		"""
		self.langs = set()
		self.words = []
	
	
	def harvest(self, f):
		"""
		Orchestrates the processing of the input file given.
		Populates the self.words list.
		"""
		f.readline()
		for line in f:
			self._process_line(line.rstrip())
		
		self.filter_poor_langs()
		self.test_words()
	
	
	def _process_line(self, line):
		"""
		Processes a single line of input.
		Words without transcription or cognate class are skipped.
		The word's source form is added to the notes field.
		"""
		line = line.split('\t')
		
		assert len(line) == 9
		for i in (0, 1, 2):
			assert len(line[i]) > 0
		
		word = {}
		
		word['language'] = line[2]
		word['iso_code'] = ''
		
		word['gloss'] = line[1]
		word['global_id'] = ''
		word['local_id'] = line[0]
		
		# transcription
		if len(line[6]) > 0:
			try:
				word['transcription'] = self._clean_ipa(line[6])
			except ValueError:
				return
		else:
			return
		
		# cognate class
		if len(line[7]) > 0:
			word['cognate_class'] = line[7]
		else:
			return
		
		# notes
		if len(line[5]) > 0:
			word['notes'] = 'source form: ' + line[5]
		else:
			word['notes'] = ''
		
		if line[8] == '1':
			word['notes'] += '; loanword'
		
		# remember
		self.langs.add(line[2])
		self.words.append(word)
	
	
	def _clean_ipa(self, ipa):
		"""
		Returns cleaned version of the given IPA transcription. 
		Raises ValueError if the transcription is bad.
		"""
		if ipa == 'брати':
			raise ValueError
		
		repl = {'ε': 'ɛ', 'е': 'e'}
		for char in repl.keys():
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, repl[char])
			assert ipa.find(char) == -1
		
		for char in ('(', ')', '\'', '‘', '’', '‿', ''):
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, '')
			assert ipa.find(char) == -1
		
		if ipa.find('/') >= 0:
			if ipa.find('/') == 0:
				ipa = ipa[1:]
			else:
				ipa = ipa[:ipa.find('/')]
		
		if ipa.find(';') >= 0:
			ipa = ipa[:ipa.find(';')]
		
		return ipa.lower()
	
	
	def _ipa_to_asjp(self, ipa):
		"""
		Converts the given IPA transcription to an ASJP transcription.
		"""
		# print(ipa, ''.join(tokens2class(ipa2tokens(ipa), 'asjp')))
		pass
	
	
	def filter_poor_langs(self):
		"""
		Filters out the languages which have <= 10 glosses.
		Affected languages: Luxembourgish (1 gloss), Ukrainian (1 gloss),
		Romansh (2 glosses), Sanskrit (4 glosses), Punjabi (10 glosses).
		"""
		poor_langs = set()
		
		for lang in self.langs:
			count = sum([1 for w in self.words if w['language'] == lang])
			if count <= 10:
				poor_langs.add(lang)
		
		self.words = [
			w for w in self.words if w['language'] not in poor_langs
		]
	
	
	def test_words(self):
		assert self.words[0] == {'language': 'ASSAMESE', 'iso_code': '',
				'gloss': 'earth/soil', 'local_id': '1.212', 'global_id': '',
				'transcription': 'mati', 'cognate_class': 'ielex-1.212-E',
				'notes': 'source form: mati; loanword'}
		assert self.words[-1] == {'language': 'URDU', 'iso_code': '',
				'gloss': 'wash', 'local_id': '9.36', 'global_id': '',
				'transcription': 'd̪ʰonə', 'cognate_class': 'ielex-9.36-F',
				'notes': 'source form: دھونا'}
	
	
	def add_global_gloss_ids(self, glossary_file):
		"""
		Enriches self.words by filling the global_id field.
		The argument is the file handler of the local glossary.
		"""
		glossary = {}  # gloss: (local_id, global_id)
		
		reader = csv.reader(glossary_file, delimiter='\t')
		next(reader)
		
		for line in reader:
			glossary[line[1]] = (line[0], int(line[3]))
		
		for word in self.words:
			assert word['local_id'] == glossary[word['gloss']][0]
			word['global_id'] = glossary[word['gloss']][1]
	
	
	def add_iso_codes(self, iso_codes_file):
		"""
		Enriches self.words by filling the iso_code field.
		The argument is the file handler of the local iso codes file.
		"""
		languages = {}  # language: iso_code
		
		reader = csv.reader(iso_codes_file, delimiter='\t')
		next(reader)
		
		for line in reader:
			if len(line[1]) == 3:
				languages[line[0]] = line[1]
		
		for word in self.words:
			if word['language'] in languages:
				word['iso_code'] = languages[word['language']]



class ModernHarvester(Harvester):
	"""
	Still named after Dune's spice harvesters.
	This one is used to harvest the newer IELex-2016 file, though.
	"""
	
	def harvest(self, f):
		"""
		Orchestrates the processing of the input file given.
		Populates the self.words list.
		"""
		reader = csv.reader(f)
		next(reader)
		for line in reader:
			lang = line[1].upper().replace(' ', '_')
			try:
				ipa = self._clean_ipa(line[3])
			except ValueError:
				continue
			word = {
				'language': lang,
				'iso_code': '',
				'gloss': line[2],
				'global_id': '',
				'local_id': line[2],
				'transcription': ipa,
				'cognate_class': line[5],
				'notes': ''
			}
			self.langs.add(lang)
			self.words.append(word)
		
		self.test_words()
	
	
	def _clean_ipa(self, ipa):
		"""
		Returns cleaned version of the given IPA transcription. 
		Raises ValueError if the transcription is bad.
		"""
		if ipa == 'XXX':
			raise ValueError
		
		repl = {'ε': 'ɛ', 'е': 'e'}
		for char in repl.keys():
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, repl[char])
			assert ipa.find(char) == -1
		
		for char in ('(', ')', '\'', '‘', '’', '‿', ''):
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, '')
			assert ipa.find(char) == -1
		
		for char in ('/', ';', ','):
			if ipa.find(char) >= 0:
				ipa = ipa[:ipa.find(char)]
		
		assert len(ipa) > 0
		
		return ipa.lower()
	
	
	def test_words(self):
		assert {'language': 'ASSAMESE', 'iso_code': '',
				'gloss': 'earth', 'local_id': 'earth', 'global_id': '',
				'transcription': 'mati', 'cognate_class': 'earth:E',
				'notes': ''} in self.words
		assert {'language': 'URDU', 'iso_code': '',
				'gloss': 'wash', 'local_id': 'wash', 'global_id': '',
				'transcription': 'd̪ʰonə', 'cognate_class': 'wash:F',
				'notes': ''} in self.words



"""
Handles the command-line interface.
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'Harvests the data of a IELex data set. '
		'Optionally enriches the harvest by adding global gloss IDs '
		'and language ISO codes.'
	))
	parser.add_argument('input_file', help=(
		'The raw data input file. '
		'Peek in the input dir to see what is for grabs.'
	))
	parser.add_argument('--local', action='store_true', help=(
		'Whether to enrich the harvest with global gloss IDs and '
		'language ISO codes.'
	))
	args = parser.parse_args()
	
	# dirs and files
	set_name = os.path.split(args.input_file)[-1].split('.')[0]
	script_dir = os.path.dirname(os.path.realpath(__file__))
	
	# harvest
	if set_name == 'IELex+ASJP':
		harvester = Harvester()
	elif set_name == 'IELex-2016':
		harvester = ModernHarvester()
	else:
		exit('IELex dataset not found')
	
	with open(args.input_file, 'r', encoding='utf-8') as f:
		harvester.harvest(f)
	
	# enrich
	if not args.local:
		glossary_file = 'glossary_local'
		if set_name == 'IELex-2016':
			glossary_file += '_2016'
		glossary_file = os.path.join(script_dir, glossary_file+'.tsv')
		with open(glossary_file, 'r') as f:
			harvester.add_global_gloss_ids(f)
		
		iso_codes_file = os.path.join(script_dir, 'iso_codes.tsv')
		with open(iso_codes_file, 'r') as f:
			harvester.add_iso_codes(f)
	
	# output
	output_file = os.path.join(script_dir, 'output', set_name +'.tsv')
	
	with open(output_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter='\t')
		
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



