import sqlite3
import os
import csv

if __name__ == '__main__':
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	date = '2017-09-19'
	db_path = os.path.normpath(os.path.join(BASE_DIR, '..', 'meet_' + date + '.sqlite'))

	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c1 = conn.cursor()

	discards = 0
	meetings = 0
	with open('source-report' + date + '.csv', 'w', newline='') as csvfile:
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

	with open('meetings-export' + date + '.csv', 'w', newline='') as file:
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
