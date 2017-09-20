import sqlite3
import os
import csv

if __name__ == '__main__':
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	output_path = os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'output'))
	date = '2017-09-20'
	db_filename = 'meet_' + date + '.sqlite'
	db_path = os.path.join(output_path, db_filename)

	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c1 = conn.cursor()

	discards = 0
	meetings = 0
	#TODO make sure UTF-8 encoded
	source_filename = 'source-report' + date + '.csv'
	source_pathname = os.path.join(output_path, source_filename)
	with open(source_pathname, 'w', newline='') as csvfile:
		w = csv.writer(csvfile)
		headers = []
		for row in c.execute('SELECT * FROM source'):
			r = list(row)
			if not headers:
				headers = list(next(zip(*c.description)))
				headers.append('meetingcount')
				w.writerow(headers)
			r.append(c1.execute('SELECT COUNT(meetingsource) FROM meeting WHERE meetingsource=?', [row[0]]).fetchone()[0])
			discards += r[-2]
			meetings += r[-1]
			w.writerow(r)
	print("total discard:" + str(discards) + ", total meet:" + str(meetings) + ", rough estimate:" + str(meetings/(meetings + discards) * 100) + "%")

	export_filename = 'meetings-export' + date + '.csv'
	export_pathname = os.path.join(output_path, export_filename)
	with open(export_pathname, 'w', newline='') as file:
		wr = csv.writer(file)
		headers = []
		for row in c.execute('SELECT * FROM meeting'):
			r = list(row)
			if not headers:
				headers = list(next(zip(*c.description)))
				wr.writerow(headers)
			wr.writerow(r)

	conn.close()

	#c.execute('SELECT * FROM source ORDER BY price'):
