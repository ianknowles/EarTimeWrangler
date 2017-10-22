import csv
import logging
import os

import table
import wrangler

logger = logging.getLogger('meeting_parser').getChild(__name__)


def find_header_match(keys, candidates):
	#todo need to strip lower both
	for key in candidates:
		key = key.strip().lower()
		try:
			keys.remove(key)
		except ValueError:
			continue
		else:
			return key
	return None


def csv_identify(db_pathname, csv_pathname, header, rows):
	t = table.Table('', header)
	discards = 0
	if t.tabletype == 'Unknown':
		logger.error('Aborted csv parse because of unrecognised header: ' + str(header))
		discards = rows

	wrangler.add_file_to_db(db_pathname, csv_pathname, discards)


def header_type(header):
	t = table.Table('', [header.split(',')])
	return t.tabletype


def find_header1():
	header_detected = csv.Sniffer().has_header(sample)
	skips = 0
	seek_dist = 0
	while not header_detected and (skips < 10):
		skips += 1
		try:
			header_detected = csv.Sniffer().has_header(sample.split('\n', maxsplit=skips)[-1])
		except csv.Error:
			logger.debug('csv parse issue')
			header_detected = False
			break
	if header_detected:
		header_str = sample
		if skips > 0:
			header_str = sample.split('\n', maxsplit=skips + 1)[-2]
		logger.info('found a header ' + header_str)
	#	logger.warning('CSV file missing header row, might be a format issue')
	#	fieldnames = ['Date of meeting', 'Minister', 'Name of organisation', 'Purpose of meeting']
	csvfile.seek(0)
	#skipped = 0
	##for line in csvfile:
	#	skipped += 1
	#	seek_dist += len(line)
	#	if skipped == skips:
	#		break
	#csvfile.seek(seek_dist)
	if header_detected:
		for i in range(skips):
			next(csvfile)


def find_header(csvfile):
	skips = 0

	for row in csvfile:
		if header_type(row) == 'meeting':
			break
		else:
			skips += 1

		if skips > 10:
			break

	csvfile.seek(0)
	if skips <= 10:
		for i in range(skips):
			next(csvfile)


def process(db_pathname, csv_pathname):
	logger.info('Starting to process csv ' + csv_pathname)
	dept = os.path.basename(os.path.dirname(csv_pathname))
	with open(csv_pathname) as csvfile:
		discards = 0
		sample = csvfile.read(1024)
		csvfile.seek(0)
		try:
			dialect = csv.Sniffer().sniff(sample)
		except csv.Error:
			logger.error('Aborted csv parse because of unrecognised format: ' + csv_pathname)
			wrangler.add_file_to_db(db_pathname, csv_pathname, -1)
			return 0

		fieldnames = None

		find_header(csvfile)

		reader = csv.DictReader(csvfile, fieldnames, dialect)
		db_rows = []
		if reader.fieldnames is None:
			#TODO problem with bis-ministerial-gifts-april-to-june.csv
			#csvfile.seek(0)
			#csv_identify(db_pathname, csv_pathname, next(csvfile), discards)
			wrangler.add_file_to_db(db_pathname, csv_pathname, discards)
			return 0
		reader.fieldnames = list(map(lambda s: s.strip().lower(), reader.fieldnames))

		csv_keys = reader.fieldnames.copy()
		keymap = {}

		# complete generic method taking the csv_keys and the list of candidate lists
		rep_keys = ['Minister', 'prime minister']
		keymap['rep'] = find_header_match(csv_keys, rep_keys)
		#if keymap['rep'] is None:
		#	for row in reader:
		#		discards += 1
		#	csv_identify(db_pathname, csv_pathname, reader.fieldnames, discards)
		#	return 0

		date_keys = ['Date of meeting', 'Date']
		keymap['date'] = find_header_match(csv_keys, date_keys)
		if keymap['date'] is None:
			for row in reader:
				discards += 1
			csv_identify(db_pathname, csv_pathname, reader.fieldnames, discards)
			return 0

		org_keys = ['Name of organisation', 'Organisation', 'Name of External Organisation', 'Name of External Organisation*', 'Name of organisation or individual']
		keymap['org'] = find_header_match(csv_keys, org_keys)
		if keymap['org'] is None:
			for row in reader:
				discards += 1
			csv_identify(db_pathname, csv_pathname, reader.fieldnames, discards)
			return 0

		meet_keys = ['Purpose of meeting', 'purpose of meeting²', 'purpose of meeting_']
		keymap['meet'] = find_header_match(csv_keys, meet_keys)
		if keymap['meet'] is None:
			for row in reader:
				discards += 1
			csv_identify(db_pathname, csv_pathname, reader.fieldnames, discards)
			return 0

		#keymap['org'] = difflib.get_close_matches('organisation', csv_keys, n=1, cutoff=0.6)[0]
		#csv_keys.remove(keymap['org'])
		#keymap['date'] = difflib.get_close_matches('date', csv_keys, n=1, cutoff=0.3)[0]
		#csv_keys.remove(keymap['date'])
		#keymap['rep'] = difflib.get_close_matches('Minister', csv_keys, n=1, cutoff=0.6)[0]
		#csv_keys.remove(keymap['rep'])
		#keymap['meet'] = difflib.get_close_matches('Purpose', csv_keys, n=1, cutoff=0.6)[0]
		rep = 'Unknown'
		for row in reader:
			#if all(map(lambda x: row[x] is None or row[x] == '', keymap.values())):
			if keymap['rep'] is None or row[keymap['rep']] == '':
				row[keymap['rep']] = rep
			else:
				rep = row[keymap['rep']]

			if row[keymap['date']] == '' and row[keymap['org']] == '' and row[keymap['meet']] == '':
				# logger.debug('Discarded partial csv row: ' + str(row))
				continue
			elif row[keymap['date']] == '' and row[keymap['meet']] == '':
				db_rows[-1][3] += ', '
				db_rows[-1][3] += row[keymap['org']]
			elif row[keymap['date']] is None or row[keymap['rep']] is None or row[keymap['org']] is None or row[keymap['meet']] is None:
				logger.warning('Discarded partial csv row: ' + str(row))
				discards += 1
			elif row[keymap['date']] == '' or len(row[keymap['date']]) > 20:
				logger.warning('Discarded partial csv row: ' + str(row))
				discards += 1
			else:
				db_rows.append([row[keymap['rep']], row[keymap['date']], row[keymap['org']], row[keymap['meet']], dept])

		file_id = wrangler.add_file_to_db(db_pathname, csv_pathname, discards)
		for row in db_rows:
			row.append(file_id)
		return wrangler.insert_table_rows(db_pathname, db_rows)