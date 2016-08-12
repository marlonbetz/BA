import argparse
import csv
import os.path
import string

sup_digits = dict(zip(string.digits, '⁰¹²³⁴⁵⁵⁵⁵⁵'))



class Harvester:
	"""
	Named after Dune's spice harvesters, this class handles the extracting of
	words out of the input data file given.
	"""
	
	def __init__(self):
		"""
		Constructor.
		"""
		self.columns = {}  # item: column index
		self.words = []
	
	
	def harvest(self, f):
		"""
		Orchestrates the processing of the input file given.
		Populates the self.words list.
		"""
		reader = csv.reader(f, delimiter='\t')
		
		header = next(reader)
		header = {key: index for index, key in enumerate(header)}
		if 'CLPA_TOKENS' in header:
			header['TOKENS'] = header['CLPA_TOKENS']
		
		for line in reader:
			self.words.append({
				'language': line[header['DOCULECT']],
				'iso_code': '',
				'gloss': line[header['CONCEPT']],
				'local_id': int(line[header['CONCEPTICON_ID']]),
				'global_id': int(line[header['CONCEPTICON_ID']]),
				'transcription': self._clean_ipa(line[header['IPA']]),
				'cognate_class': int(line[header['COGID']]),
				'tokens': line[header['TOKENS']]
			})
	
	
	def _clean_ipa(self, ipa):
		"""
		Cleans non-IPA symbols from the given transcription.
		Only Chinese-180-18 is affected by this function.
		"""
		for char in string.digits:
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, sup_digits[char])
			assert ipa.find(char) == -1
		
		for char in ('❷', '[', ']', '@'):
			if ipa.find(char) >= 0:
				ipa = ipa.replace(char, '')
			assert ipa.find(char) == -1
		
		for char in ('>', '，'):
			if ipa.find(char) >= 0:
				ipa = ipa.split(char)[0].strip()
			assert ipa.find(char) == -1
		
		return ipa.lower()



"""
Handles the command-line interface.
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'Harvests the data of the given input file, '
		'optionally enriches it by adding '
		'global gloss IDs and language ISO codes, '
		'and generates an output file. '
		'Currently only local harvests are supported.'
	))
	parser.add_argument('input_file', help=(
		'The raw data input file.'
	))
	parser.add_argument('--local', action='store_true', help=(
		'Whether to enrich the ouput '
		'with global gloss IDs and language ISO codes.'
	))
	args = parser.parse_args()
	
	set_name = os.path.split(args.input_file)[-1].split('.')[0]
	script_dir = os.path.dirname(os.path.realpath(__file__))
	
	
	# harvest
	with open(args.input_file, 'r', encoding='utf-8') as f:
		harvester = Harvester()
		harvester.harvest(f)
	
	
	# write output
	output_file = os.path.join(script_dir, 'output', set_name + '.tsv')
	
	with open(output_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.writer(f, delimiter='\t')
		writer.writerow([
			'language', 'iso_code',
			'gloss', 'global_id', 'local_id',
			'transcription', 'cognate_class', 'tokens'
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
				word['tokens']
			])



