def find_header_match(keys, candidates):
	for key in candidates:
		key = key.strip().lower()
		try:
			keys.remove(key)
		except ValueError:
			continue
		else:
			return key
	return None


rep_keys = ['Minister', 'prime minister', 'Name of Minister', 'Permanent secretary']
date_keys = ['Date of meeting', 'Date']
meet_keys = ['Purpose of meeting', 'purpose of meeting²', 'purpose of meeting_']
org_keys = ['Name of organisation', 'Organisation', 'Name of External Organisation', 'Name of External Organisation*', 'Name of organisation or individual', 'Person or organisation that meeting was with']


class Table:
	#title = ''
	#header = []
	#rows = []
	#tabletype = 'Unknown'

	def __init__(self, t, cells):
		self.title = t
		self.header = list(cells.pop(0))
		self.rows = list(cells)
		self.tabletype = 'Unknown'
		self.identify()

	def identify(self):
		keys = [h.strip().lower() for h in self.header]

		# complete generic method taking the csv_keys and the list of candidate lists
		rep = find_header_match(keys, rep_keys)
		date = find_header_match(keys, date_keys)
		org = find_header_match(keys, org_keys)
		meet = find_header_match(keys, meet_keys)

		#TODO length checks removed, need to handle empty columns
		if rep and date and org and meet:
			self.tabletype = 'meeting'
		elif date and org and meet:
			self.tabletype = 'meeting'
		elif find_header_match(keys, ['date', 'date gift given']) and find_header_match(keys, ['gift']):
			self.tabletype = 'gift'
		elif find_header_match(keys, ['destination']):
			self.tabletype = 'travel'
		elif find_header_match(keys, ['Date of hospitality']):
			self.tabletype = 'hospitality'
