import csv
import datetime
import hashlib
import json
import logging.config
import os
import sqlite3
import time
import tkinter
import tkinter.font

import CSV.table_transform
import PDF.table_transformer

root_logger = logging.getLogger('meeting_parser')
logger = logging.getLogger('meeting_parser').getChild(__name__)

file_path = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(file_path, '..')
log_path = os.path.join(path, 'log')
logging_config_filename = os.path.join(file_path, 'log_config.json')
meet_count = 0
#root = tkinter.Tk()
#w = tkinter.Canvas(root, width=1024, height=768)

def logging_setup():
	# This should not be neccessary but pdfminer3k does not log properly
	# Supressing propagation stops the duplication of our log messages
	# Setting the root logger to error stops its warning spam
	logging.propagate = False
	logging.getLogger().setLevel(logging.ERROR)
	if not root_logger.hasHandlers():
		try:
			with open(logging_config_filename, 'r') as file:
				# todo catch some exceptions and print some error messages
				config_dict = json.load(file)
				time_stamp_string = datetime.datetime.now().isoformat().replace(':', '.')
				time_stamp_filename = config_dict['handlers']['file']['filename'].replace('%', time_stamp_string)
				config_dict['handlers']['file']['filename'] = os.path.join(log_path, time_stamp_filename)
				logging.config.dictConfig(config_dict)
		except EnvironmentError:
			logger.error('Logging config is missing, please provide {logging_config_filename} before continuing'.format(**locals()))
			raise
	logger.info('Log file initialised')

# table for source files and metadata
# table for reps
# table for orgs
# table for repaliases
# table for orgaliases
# table for tableheaders?


# Probably want a table object that gets destroyed with commit and close, we then dont need to reconnect all the time
def create_meeting_table(db_pathname):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	# department
	c.execute('''CREATE TABLE IF NOT EXISTS meeting (
	meetingid INTEGER PRIMARY KEY,
	rep TEXT,
	date TEXT,
	org TEXT,
	purpose TEXT,
	department TEXT,
	meetingsource INTEGER,
	FOREIGN KEY (meetingsource) REFERENCES source(sourceid))''')
	# source, source page
	conn.commit()
	conn.close()


def create_source_table(db_pathname):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	# department
	c.execute('''CREATE TABLE IF NOT EXISTS source (
	sourceid  INTEGER PRIMARY KEY,
	insert_time INTEGER,
	dept TEXT,
	filename TEXT,
	filetype TEXT,
	filesize INTEGER,
	filehash TEXT,
	discards INTEGER)''')
	# source, source page
	conn.commit()
	conn.close()


def check_table_exists(c, tablename):
	# c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tablename,))
	print()


def insert_table_rows(db_pathname, table):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	tuplelist = []
	for row in table:
		# if len(row) == 1:
		#    print(row)
		#   break
		tuplelist.append(tuple(row))
	#print(tuplelist)

	count = 0
	#c.executemany('INSERT INTO meeting VALUES (NULL,?,?,?,?,?)', tuplelist)
	for rowtuple in tuplelist:
		if len(rowtuple) == 6:
			c.execute('INSERT INTO meeting VALUES (NULL,?,?,?,?,?,?)', rowtuple)
			count += 1
		else:
			logger.warning('Incorrect length for insert into DB, catch this before getting here. Row=' + str(rowtuple))

	conn.commit()
	conn.close()
	logger.info('Committed ' + str(count) + ' meetings')
	return count


def insert_table_row(db_pathname, tuple):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	c.execute('INSERT INTO meeting VALUES (NULL,?,?,?,?,?,?)', tuple)
	conn.commit()
	conn.close()


def insert_source_file(db_pathname, tuple):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	c.execute('INSERT INTO source VALUES (NULL,?,?,?,?,?,?,?)', tuple)
	conn.commit()
	conn.close()
	return c.lastrowid


# most of the metadata is gathered in other funcs, do we need this convenience func?
def add_file_to_db(db_pathname, pathname, discards):
	basename = os.path.basename(pathname)
	filename, file_type = "", ""
	if basename.count('.'):
		filename, file_type = basename.rsplit('.', maxsplit=1)
	file_size = os.path.getsize(pathname)
	file_hash = ""
	date = int(time.time())
	with open(pathname, 'rb') as file:
		file_hash = hashlib.sha256(file.read()).hexdigest()
	# need to check if entry already exists before inserting
	dept = os.path.basename(os.path.dirname(pathname))
	logger.info('Added a ' + file_type + ' to the db. ' + basename + ' ' + str(file_size) + ' bytes sha256: ' + file_hash)
	return insert_source_file(db_pathname, (date, dept, basename, file_type, file_size, file_hash, discards))


files = []


def process_file(db_pathname, pathname):
	with open(pathname, 'rb') as file:
		file_hash = hashlib.sha256(file.read()).hexdigest()
	if file_hash in files:
		logger.info('Duplicate file skipped ' + pathname)
		return 0
	else:
		files.append(file_hash)
	filename, file_type = os.path.splitext(os.path.basename(pathname))
	if file_type == '.csv':
		return CSV.table_transform.process(db_pathname, pathname)
	elif file_type == '.pdf':
		return process_pdf(db_pathname, pathname)
	return 0


def process_path(db_pathname, path, count):
	# instead of recursing use os.walk?
	total_count = count
	with os.scandir(path) as dir_contents:
		for entry in dir_contents:
			if not entry.name.startswith('.') and entry.is_file():
				#print(entry.name)
				total_count += process_file(db_pathname, entry.path)
			elif entry.is_dir():
				total_count += process_path(db_pathname, entry.path, total_count)
	return total_count


def process_path2(db_pathname, path, count):
	# instead of recursing use os.walk?
	total_count = count
	for (dirpath, dirnames, filenames) in os.walk(path):
		for filename in filenames:
			name, file_type = os.path.splitext(filename)
			if file_type == '.csv':
				total_count += CSV.table_transform.process(db_pathname, os.path.join(dirpath, filename))
			elif file_type == '.pdf':
				total_count += process_pdf(db_pathname, os.path.join(dirpath, filename))
	return total_count


def draw_rect(r, colour):
	x0, y0, x1, y1 = r.bbox
	#w.create_rectangle(x0,  768 - y0, x1,  768 - y1, outline=colour)


def draw_char(c, colour):
	arial = tkinter.font.Font(family='Arial',
	                     size=int(c.size) - 1, weight='bold')
	#canvas_id = w.create_text(c.x0, 768 - c.y1, anchor="nw", fill=colour, font=arial)
	#w.itemconfig(canvas_id, text=c._text)


def draw_rect_groups(g):
	colours = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "brown", "black"]
	i = 0
	for group in g:
		for r in group:
			draw_rect(r, colours[i])
		i += 1
		if i >= len(colours):
			i = 0


def draw_char_groups(g):
	colours = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "brown", "black"]
	i = 0
	for group in g:
		for r in group:
			draw_char(r, colours[i])
		i += 1
		if i >= len(colours):
			i = 0

def process_pdf(db_pathname, pdf_pathname):
	logger.info('Starting to process pdf ' + pdf_pathname)

	#tables = PDF.table_parser.get_tables(pdf_pathname)
	#stitched_tables = PDF.table_parser.stitch_together_tables(tables)

	tables = PDF.table_transformer.extract_table(pdf_pathname)
	#tables[0].identify()

	#rects = PDF.table_transformer.get_rects()
	#chars = PDF.table_transformer.get_chars()
	#draw_char_groups(chars)
	#draw_rect_groups(rects)
	#for r in rects[0][1]:
	#	draw_rect(r, "red")

	dept = os.path.basename(os.path.dirname(pdf_pathname))

	meetings = list(filter(lambda x: x.tabletype == 'meeting' and len(x.rows) > 0, tables))
	not_meetings = list(filter(lambda x: x.tabletype == 'unknown' and len(x.rows) > 0, tables))

	discards = 0
	for table in not_meetings:
		discards += len(table.rows)
	file_id = add_file_to_db(db_pathname, pdf_pathname, discards)
	if len(meetings) == 0:
		return 0

	db_rows = []
	for table in meetings:
		for row in table.rows:
			db_rows.append([table.title] + row + [dept] + [file_id])
			print(db_rows)

	return insert_table_rows(db_pathname, db_rows)


def ago_task():
	db_pathname = 'ago.sqlite'

	create_meeting_table(db_pathname)
	create_source_table(db_pathname)

	data_path = os.path.join(path, 'Ministerial Meetings', 'ago')

	total = process_path2(db_pathname, data_path, 0)
	logger.info(str(total) + ' total meetings committed')


def data_task():
	date = datetime.date.today().isoformat()
	db_filename = 'meet_' + date + '.sqlite'
	db_pathname = os.path.join(path, 'output', db_filename)

	create_meeting_table(db_pathname)
	create_source_table(db_pathname)

	data_path = os.path.join(path, 'data')

	total = process_path2(db_pathname, data_path, 0)
	logger.info(str(total) + ' total meetings committed')


def main_task():

	logging_setup()

	start = datetime.datetime.now()

	data_task()

	end = datetime.datetime.now()
	logger.info('Finished at {}'.format(end.isoformat()))
	logger.info('Duration {}'.format(end - start))

	# table of orgs
	# table of ministers


def task():
	print("hello")
	# root.after(2000, main_task)  # reschedule event in 2 seconds


if __name__ == '__main__':
	#w.pack()

	#w.create_rectangle(50, 20, 150, 80, fill="#476042")
	#w.create_rectangle(65, 35, 135, 65, fill="yellow")
	#root.after(2000, main_task)
	#root.mainloop()
	main_task()

