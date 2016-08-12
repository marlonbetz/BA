import argparse
import csv
import os.path
import string

sup_digits = dict(zip(string.digits, '⁰¹²³⁴⁵⁶⁷⁸⁹'))



"""
The desired output.
"""
words = []

"""
{} of local_id: gloss. Used for assertions.
"""
glosses = {}



def process_file(f):
	"""
	Processes the abvd2.txt file.
	"""
	lang_names = process_language_names(f)
	
	# number of lines processed
	count = -1
	
	# name and iso code of currently processed language
	lang_name = None
	lang_code = None
	
	# used to process the 3-line language block headers
	in_header = 0
	
	# some languages are not in lang_names, so we should skip these
	skip_lang = True
	
	# the set of languages that have been processed already
	processed_langs = set()
	
	for line in f:
		count += 1
		line = line.strip()
		
		if line == '$':
			break
		
		# start of new language block
		if line.startswith('{'):
			assert in_header == 0
			
			lang_name = line.strip('{}')
			
			if lang_name not in lang_names:
				lang_name = None
				continue
			
			if lang_name in processed_langs:
				lang_name = None
				continue
			
			in_header = 1
			continue
		
		# some language blocks are skipped
		if lang_name is None:
			continue
		
		# process lines 2 and 3 of language block header
		if in_header == 1:
			in_header += 1
			continue
		if in_header == 2:
			lang_code = line
			in_header = 0
			continue
		
		# if it is not a header, it is a word
		process_word(line, lang_name, lang_code)
	
	assert count == (196785 - 399)
	assert_glosses()



def process_language_names(f):
	"""
	Extracts the 397 language names into a set.
	"""
	languages = set()
	count = -1
	
	for line in f:
		count += 1
		line = line.strip()
		
		if line == '$':
			break
		languages.add(line)
	
	assert count == 397
	assert len(languages) == 397
	
	assert 'Rurutuan' in languages
	assert 'Rapanui (Easter Island)' in languages
	assert 'Ifira-Mele (Mele-Fila)' in languages
	assert 'Saaroa' in languages
	assert 'Siraya' in languages
	
	return languages



def process_word(line, lang_name, lang_code):
	"""
	Processes the given word data line (no endings).
	Creates new word entry if the line is complete.
	"""
	word = {}
	
	word['language'] = lang_name
	word['iso_code'] = lang_code
	word['notes'] = ''
	
	line = line.split('\t', 2)
	
	try:
		assert len(line) == 3
		int(line[0])
	except (AssertionError, ValueError):
		return
	
	word['local_id'] = int(line[0])
	word['gloss'] = line[1]
	
	# ensure glosses are consistent throughout the data
	if word['local_id'] not in glosses:
		glosses[word['local_id']] = word['gloss']
	else:
		assert word['gloss'] == glosses[word['local_id']]
	
	# transcription and cognate_class
	rest = line[2].split(';')
	
	for index, pair in enumerate(rest):
		if index == 0:
			pair = pair.split('\t')
			if len(pair) != 2:
				return
			word['transcription'], word['notes'] = process_transcription(pair[0], word['language'])
			word['cognate_class'] = pair[1]
		else:
			pair = pair.split('\t')
			if len(pair) != 2:
				continue
			if len(word['notes']):
				word['notes'] += '; '
			word['notes'] += pair[0] +' '+ pair[1]
	
	words.append(word)



def process_transcription(trans_raw, language):
	"""
	Returns a (transcription, notes) tuple.
	"""
	is_ok = True
	trans = trans_raw
	
	# replaces
	repl = {'\\C3 ': 'à', 'ţ': 'ʈ', 'ố': 'o'}
	for char in repl.keys():
		if trans.find(char) >= 0:
			is_ok = False
			trans = trans.replace(char, repl[char])
	
	if trans.find('\'') >= 0:
		is_ok = False
		if language in ('Nese', 'Araki (Southwest Santo)'):
			trans = trans.replace('\'', '')
		else:
			trans = trans.replace('\'', 'ʔ')
	
	# splitters
	for char in ('+', '/'):
		if trans.find(char) >= 0:
			is_ok = False
			trans = trans.split(char)[0].strip()
		assert trans.find(char) == -1
	
	# brackets
	while trans.find('(') >= 0:
		is_ok = False
		left = trans.find('(')
		right = trans.find(')')
		assert right > left
		trans = trans[:left].strip() + trans[right+1:]
	assert trans.find('(') == -1
	assert trans.find(')') == -1
	
	if trans.find('[') >= 0 or trans.find(']') >= 0:
		is_ok = False
		trans = trans.replace('[', '')
		trans = trans.replace(']', '')
	assert trans.find('[') == -1
	assert trans.find(']') == -1
	
	# digits
	for char in string.digits:
		if trans.find(char) >= 0:
			is_ok = False
			trans = trans.replace(char, sup_digits[char])
			trans = trans.replace(' ', '')  # only Hainan Cham affected
		assert trans.find(char) == -1
	
	# non-IPA and ambiguous chars
	for char in ['...', '%', '’', '?']:
		if trans.find(char) >= 0:
			is_ok = False
			trans = trans.replace(char, '')
		assert trans.find(char) == -1
	
	if trans.lower() != trans:
		is_ok = False
		trans = trans.lower()
	
	if is_ok:
		return (trans_raw, '')
	else:
		return (trans.strip(), trans_raw)



def assert_glosses():
	"""
	Assertions.
	"""
	assert len(glosses) == 210
	assert glosses[1] == 'hand'
	assert glosses[2] == 'left'
	assert glosses[3] == 'right'
	assert glosses[53] == 'person/human being'
	assert glosses[101] == 'to fly'
	assert glosses[123] == 'to flow'
	assert glosses[166] == 'correct, true'
	assert glosses[209] == 'One Hundred'
	assert glosses[210] == 'One Thousand'



def assert_words():
	"""
	Assertions.
	"""
	assert {'language': 'Bali', 'iso_code': 'ban',
			'gloss': 'hand', 'local_id': 1, 'global_id': 1277,
			'transcription': 'lima', 'cognate_class': '1', 'notes': 'limə 1' } in words
	assert {'language': 'Bali', 'iso_code': 'ban',
			'gloss': 'dirty', 'local_id': 10, 'global_id': 1230,
			'transcription': 'daki', 'cognate_class': '1', 'notes': '' } in words
	assert {'language': 'Bali', 'iso_code': 'ban',
			'gloss': 'mosquito', 'local_id': 109, 'global_id': 1509,
			'transcription': 'legu', 'cognate_class': '44', 'notes': 'ləgu 44' } in words
	assert {'language': 'Bali', 'iso_code': 'ban',
			'gloss': 'feather', 'local_id': 99, 'global_id': 1201,
			'transcription': 'bulu', 'cognate_class': '1', 'notes': '' } in words
	
	assert {'language': 'Siraya', 'iso_code': 'fos',
			'gloss': 'hand', 'local_id': 1, 'global_id': 1277,
			'transcription': 'rima', 'cognate_class': '1', 'notes': 'li-ma 1' } in words
	assert {'language': 'Siraya', 'iso_code': 'fos',
			'gloss': 'wing', 'local_id': 100, 'global_id': 1257,
			'transcription': 'papalis', 'cognate_class': '2', 'notes': 'paparyl 2' } in words
	assert {'language': 'Siraya', 'iso_code': 'fos',
			'gloss': 'to dig', 'local_id': 90, 'global_id': 1418,
			'transcription': 'kari', 'cognate_class': '1', 'notes': 'kmari 1' } in words
	assert {'language': 'Siraya', 'iso_code': 'fos',
			'gloss': 'bird', 'local_id': 97, 'global_id': 937,
			'transcription': 'ayam', 'cognate_class': '2', 'notes': 'aiam 2; ajajam 2' } in words
	
	assert {'language': 'Tagalog', 'iso_code': 'tgl',
			'gloss': 'hand', 'local_id': 1, 'global_id': 1277,
			'transcription': 'kamáy', 'cognate_class': '28', 'notes': '' } in words
	assert {'language': 'Tagalog', 'iso_code': 'tgl',
			'gloss': 'to live, be alive', 'local_id': 76, 'global_id': 1422,
			'transcription': 'búhay', 'cognate_class': '14', 'notes': '' } in words
	assert {'language': 'Tagalog', 'iso_code': 'tgl',
			'gloss': 'bird', 'local_id': 97, 'global_id': 937,
			'transcription': 'ībon', 'cognate_class': '73', 'notes': '' } in words
	assert {'language': 'Tagalog', 'iso_code': 'tgl',
			'gloss': 'egg', 'local_id': 98, 'global_id': 744,
			'transcription': 'itlóg', 'cognate_class': '24', 'notes': '' } in words
	
	assert {'language': 'Saaroa', 'iso_code': 'sxr',
			'gloss': 'hand', 'local_id': 1, 'global_id': 1277,
			'transcription': 'ramoco', 'cognate_class': '4', 'notes': 'ramucho 4' } in words
	assert {'language': 'Saaroa', 'iso_code': 'sxr',
			'gloss': 'head', 'local_id': 24, 'global_id': 1256,
			'transcription': 'boŋoʔo', 'cognate_class': '2', 'notes': 'bangou 2?' } in words
	assert {'language': 'Saaroa', 'iso_code': 'sxr',
			'gloss': 'tongue', 'local_id': 32, 'global_id': 1205,
			'transcription': 'ʔabasə', 'cognate_class': '5', 'notes': '' } in words
	assert {'language': 'Saaroa', 'iso_code': 'sxr',
			'gloss': 'feather', 'local_id': 99, 'global_id': 1201,
			'transcription': 'ʔalapoŋo', 'cognate_class': '3', 'notes': '' } in words
	
	for word in words:
		assert len(word['language']) > 0
		assert len(word['iso_code']) in (0, 3)
		assert len(word['gloss']) > 0
		assert type(word['local_id']) is int
		assert type(word['global_id']) is int
		assert len(word['transcription']) > 0
		assert len(word['cognate_class']) > 0



def globalise(glossary_file):
	"""
	Adds global_id to each word in the words list.
	The argument is the file name of the local glossary.
	"""
	id_dict = {}
	
	with open(glossary_file, 'r') as f:
		reader = csv.reader(f, delimiter='\t')
		next(reader)
		
		for line in reader:
			local_id = int(line[0])
			global_id = int(line[3])
			id_dict[local_id] = global_id
	
	assert len(id_dict) == len(glosses)
	
	for word in words:
		word['global_id'] = id_dict[word['local_id']]



def write_splits(words, output_dir):
	"""
	Creates four additional files in the output dir.
	The first 3 contain 100 langs each, the 4th one the remainder.
	"""
	file_names = ['abvd2-part'+str(i)+'.tsv' for i in range(1, 5)]
	file_names = [os.path.join(output_dir, s) for s in file_names]
	
	langs = []
	for word in words:
		if word['language'] not in langs:
			langs.append(word['language'])
	langs = [langs[100*i:100*(i+1)] for i in range(0, 4)]
	
	chunks = []
	for i in range(0, 4):
		chunks.append([])
		for word in words:
			if word['language'] in langs[i]:
				chunks[i].append(word)
	
	for i in range(0, 4):
		with open(file_names[i], 'w', newline='', encoding='utf-8') as f:
			writer = csv.writer(f, delimiter='\t')
			writer.writerow([
				'language', 'iso_code',
				'gloss', 'global_id', 'local_id',
				'transcription', 'cognate_class', 'notes'
			])
			for word in chunks[i]:
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



def check_splits(words, output_dir):
	"""
	Tries to assert that combining the splits in the output dir will give the
	given words.
	"""
	li = []
	
	for i in range(1, 5):
		file_name = 'abvd2-part'+str(i)+'.tsv'
		file_name = os.path.join(output_dir, file_name)
		assert os.path.exists(file_name)
		
		with open(file_name) as f:
			reader = csv.reader(f, delimiter='\t')
			header = tuple(next(reader))
			for line in reader:
				li.append(tuple(line))
	
	words_ = []
	for word in words:
		words_.append(tuple([str(word[key]) for key in header]))
	
	assert len(li) == len(words) == len(words_)
	assert set(li) == set(words_)



"""
Opens the abvd2.txt file and inits its processing.
No error/assertion handling; the intended usage is command-line.
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'Harvests the data of the abvd2 data set.'
	))
	parser.add_argument('--split', action='store_true', help=(
		'Also splits the output into four more or less equally '
		'sized files. The original output file is preserved.'
	))
	args = parser.parse_args()
	
	dir_name = os.path.dirname(os.path.realpath(__file__))
	file_name = os.path.join(dir_name, 'input', 'abvd2.txt')
	
	with open(file_name, 'r', encoding='utf-8') as f:
		process_file(f)
	
	print(str(len(words)) + ' words extracted')
	
	
	file_name = os.path.join(dir_name, 'glossary_local.tsv')
	globalise(file_name)
	
	assert_words()
	
	
	file_name = os.path.join(dir_name, 'output', 'abvd2.tsv')
	
	with open(file_name, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter='\t')
		writer.writerow([
			'language', 'iso_code',
			'gloss', 'global_id', 'local_id',
			'transcription', 'cognate_class', 'notes'
		])
		for word in words:
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
	
	if args.split:
		write_splits(words, os.path.join(dir_name, 'output'))
		check_splits(words, os.path.join(dir_name, 'output'))



