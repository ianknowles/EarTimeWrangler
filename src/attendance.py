import os
import sqlite3
import opencalais
import time


def create_attendance_table(db_pathname):
	conn = sqlite3.connect(db_pathname)
	c = conn.cursor()
	# department
	c.execute('''CREATE TABLE IF NOT EXISTS attendances (
	attendanceid INTEGER PRIMARY KEY,
	entitytype TEXT,
	entityname TEXT,
	matchtext TEXT,
	matchoffset INTEGER,
	attendancemeeting INTEGER,
	FOREIGN KEY (attendancemeeting) REFERENCES meeting(meetingid))''')
	# source, source page
	conn.commit()
	conn.close()


if __name__ == '__main__':
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	output_path = os.path.normpath(os.path.join(BASE_DIR, '..', 'output'))
	date = '2017-11-07'
	db_filename = 'meet_' + date + '.sqlite'
	db_path = os.path.join(output_path, db_filename)
	create_attendance_table(db_path)

	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c1 = conn.cursor()

	open_calais_connection = opencalais.OpenCalais()
	for row in c.execute('SELECT * FROM meeting'):
		r = list(row)

		result = None
		fails = 0
		matches = []
		while not result and fails < 5:
			try:
				result = open_calais_connection.post_data(r[3])
			except Exception as e:
				fails = fails + 1
				print(e)
			finally:
				time.sleep(1)
		if result:
			matches = opencalais.best_match(result)
		for match in matches:
			m = (match['_type'], match['name'], match['instances'][0]['exact'], match['instances'][0]['offset'], r[0])
			c1.execute('INSERT INTO attendances VALUES (NULL,?,?,?,?,?)', m)
			conn.commit()

	conn.commit()
	conn.close()


