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
	total += wrangler.process_pdf(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-expenses-january-march-2015.pdf'))
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
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'clg', '2014q2.csv'))
	#co 2010q4
	#TODO dropping meetings from here due to weird use of line breaks instead of commas
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'ho', '2012q1.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'clg', 'Senior_Officials_meetings_January_to_March_2016.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'bis', 'bis-ministerial-hospitality-jan-mar-2014.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'dwp', '2012q1.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'dcms', '2011q1.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'pmo', '2017-pmo-Q1 (january-march) 30-06-2017.csv'))
	#TODO bad multi-line formatting
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'decc', '2011q3_2.csv'))
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'decc', '2011q3_3.csv'))

	#TODO some meetings have no date attached
	total += CSV.table_transform.process(db_pathname, os.path.join(data_path, 'dft', '2014q1.csv'))

	wrangler.logger.info(str(total) + ' total meetings committed')
	# root.mainloop()


if __name__ == '__main__':
	test_task()
