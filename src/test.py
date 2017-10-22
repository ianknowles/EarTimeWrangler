import os
import wrangler
import CSV


def test_task():
	db_pathname = 'test.sqlite'
	wrangler.logging_setup()
	total = 0

	wrangler.create_meeting_table(db_pathname)
	wrangler.create_source_table(db_pathname)

	# w.pack()

	data_path = os.path.join(wrangler.path, 'data')
	#total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-expenses-january-march-2015.pdf'))
	#total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-expenses-july-september-2014.pdf'))
	# process_file(db_pathname, os.path.join(data_path, 'moj', '2015q1.pdf'))

	# total += process_path2(db_pathname, data_path, 0)
	#total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'ago', '2015_0103.pdf'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'ago', '2010_0507.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'ago', '2011_1012.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'wo', '2010-wo-Q2 (may-july) (1) USoS.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'clg', '2011q2.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'dfe', '2016-dfe-Q3 (july-september) 16-12-2016.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'clg', '2012q4.csv'))
	#TODO has a weird multi-line format that isn't captured
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'clg', '2014q2.csv'))
	#co 2010q4
	wrangler.logger.info(str(total) + ' total meetings committed')
	# root.mainloop()


if __name__ == '__main__':
	test_task()
