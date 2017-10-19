import os
import wrangler


def test_task():
	db_pathname = 'test.sqlite'
	wrangler.logging_setup()
	total = 0

	wrangler.create_meeting_table(db_pathname)
	wrangler.create_source_table(db_pathname)

	# w.pack()

	data_path = os.path.join(wrangler.path, 'data')
	total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-expenses-january-march-2015.pdf'))
	total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-expenses-july-september-2014.pdf'))
	# process_file(db_pathname, os.path.join(data_path, 'moj', '2015q1.pdf'))

	# total += process_path2(db_pathname, data_path, 0)
	total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'ago', '2015_0103.pdf'))
	total += wrangler.process_csv(db_pathname, os.path.join(data_path, 'ago', '2010_0507.csv'))
	total += wrangler.process_csv(db_pathname, os.path.join(data_path, 'ago', '2011_1012.csv'))
	total += wrangler.process_csv(db_pathname, os.path.join(data_path, 'wo', '2010-wo-Q2 (may-july) (1) USoS.csv'))

	wrangler.logger.info(str(total) + ' total meetings committed')
	# root.mainloop()


if __name__ == '__main__':
	test_task()
