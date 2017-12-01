import sqlite3
import os
import csv

if __name__ == '__main__':
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	output_path = os.path.normpath(os.path.join(BASE_DIR, '..', '..', 'output'))
	date = '2017-11-07'
	db_filename = 'meet_' + date + '.sqlite'
	db_path = os.path.join(output_path, db_filename)

	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c1 = conn.cursor()
	c2 = conn.cursor()

	csv_discards = 0
	csv_meetings = 0
	pdf_discards = 0
	pdf_meetings = 0
	#TODO make sure UTF-8 encoded
	source_filename = 'source-report' + date + '.csv'
	source_pathname = os.path.join(output_path, source_filename)
	with open(source_pathname, 'w', newline='', encoding='utf-8') as csvfile:
		w = csv.writer(csvfile)
		headers = []
		for row in c.execute('SELECT * FROM source'):
			r = list(row)
			if not headers:
				headers = list(next(zip(*c.description)))
				headers.append('meetingcount')
				w.writerow(headers)
			r.append(c1.execute('SELECT COUNT(meetingsource) FROM meeting WHERE meetingsource=?', [row[0]]).fetchone()[0])
			if r[3] == 'csv':
				csv_discards += r[-2]
				csv_meetings += r[-1]
			elif r[3] == 'pdf':
				pdf_discards += r[-2]
				pdf_meetings += r[-1]
			w.writerow(r)
	#print("csv discard:" + str(csv_discards) + ", csv meet:" + str(csv_meetings) + ", rough estimate:" + str(csv_meetings/(csv_meetings + csv_discards) * 100) + "%")
	#print("total discard:" + str(pdf_discards) + ", total meet:" + str(pdf_meetings) + ", rough estimate:" + str(pdf_meetings/(pdf_meetings + pdf_discards) * 100) + "%")
	discards = csv_discards + pdf_discards
	meetings = csv_meetings + pdf_meetings
	#print("total discard:" + str(discards) + ", total meet:" + str(meetings) + ", rough estimate:" + str(meetings/(meetings + discards) * 100) + "%")

	export_filename = 'meetings-export' + date + '.csv'
	export_pathname = os.path.join(output_path, export_filename)
	with open(export_pathname, 'w', newline='', encoding='utf-8') as file:
		wr = csv.writer(file)
		headers = []
		for row in c.execute('SELECT * FROM meeting'):
			r = list(row)
			if not headers:
				headers = list(next(zip(*c.description)))
				wr.writerow(headers)
			wr.writerow(r)

	export_filename = 'attendance-export' + date + '.csv'
	export_pathname = os.path.join(output_path, export_filename)
	with open(export_pathname, 'w', newline='', encoding='utf-8') as file:
		wr = csv.writer(file)
		headers = []
		for row in c.execute('SELECT * FROM attendances'):
			r = list(row)
			if not headers:
				headers = list(next(zip(*c.description)))
				wr.writerow(headers)
			wr.writerow(r)

	export_filename = 'combined-export' + date + '.csv'
	export_pathname = os.path.join(output_path, export_filename)
	with open(export_pathname, 'w', newline='', encoding='utf-8') as file:
		wr = csv.writer(file)
		headers = []
		for row in c.execute('SELECT * FROM attendances'):
			r = list(row)
			meeting = c1.execute('SELECT * FROM meeting WHERE meetingid=?', [r[5]]).fetchone()
			source = c2.execute('SELECT * FROM source WHERE sourceid=?', [meeting[6]]).fetchone()
			r = r + list(meeting)[1:] + list(source)[1:]
			if not headers:
				headers = list(next(zip(*c.description)))
				headers = headers + list(next(zip(*c1.description)))[1:] + list(next(zip(*c2.description)))[1:]
				wr.writerow(headers)
			wr.writerow(r)

	conn.close()

	#c.execute('SELECT * FROM source ORDER BY price'):
