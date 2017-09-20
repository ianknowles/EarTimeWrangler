import logging
import math
import os
from collections import defaultdict

import pdfminer
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser, PDFDocument

import PDF.rectangles

logger = logging.getLogger('meeting_parser').getChild(__name__)


def extract_table(pdf_path):
	layouts = get_page_layouts(pdf_path)
	tables = [page_to_tables(page_layout) for page_layout in layouts]
	stitched = new_stitch(tables)
	return table_review(stitched)

def new_stitch(tables):
	main_table = []

	for page in tables:
		for n, table in enumerate(page):
			# try to join lines that run over table breaks
			if (n == 0 and
					    len(table['title']) == 0 and
					    # len(list(filter(lambda s: s == '', table[1][0]))) > 0 and
					    len(main_table) > 0):
				logger.info('Stitching rows:' + str(main_table[-1]) + str(table))
				if any(map(lambda x: x == '', table['cells'][0])):
					for i in range(min(len(main_table[-1]['cells'][-1]), len(table['cells'][0]))):
						main_table[-1]['cells'][-1][i] += ' '
						main_table[-1]['cells'][-1][i] += table['cells'][0][i]
					main_table[-1]['cells'] += table['cells']
				else:
					main_table[-1]['cells'] += table['cells']
				logger.info('Stitched result:' + str(main_table[-1]))
			else:
				main_table.append(table)
	return main_table

def table_review(tables):
	for table in tables:
		# can we do this without copying the cells? pointer to first row is easy, pointer to the rest?
		cells = list(table['cells'])
		table['header'] = cells.pop(0)
		table['rows'] = cells
		table['tabletype'] = 'unknown'
		first = table['header'][0].lower()
		print(first)
		finds = table['header'][0].lower().find('date')

		if table['header'][0].lower().find('date') >= 0 or (table['header'][0].lower() == 'date of meeting'):
			#if len(main_table2[-1]['rows']) > 0:
			#	if 'title' not in main_table2[-1]:
			#		main_table2[-1]['title'] = ['']
			#		logger.warning('Warning could not find title:' + str(main_table2[-1]))
			#	main_table2.append({})
			#	main_table2[-1]['title'] = main_table2[-2]['title']
			#	main_table2[-1]['header'] = []
			#	main_table2[-1]['rows'] = []
			#	main_table2[-1]['tabletype'] = main_table2[-2]['tabletype']

			if len(table['header']) >= 3:
				if table['header'][2].lower().strip() == 'purpose of meeting':
					logger.info('Probably found a meeting header row:' + str(table['header']))
					table['tabletype'] = 'meeting'

		#for row in table['rows']:
		#	if all(map(lambda s: s == '', row)):
		#		logger.debug('Discarded empty row')
		#		table['rows']
		table['rows'] = list(filter(lambda r: not all(map(lambda s: s == '', r)), table['rows']))
		#elif len(list(filter(lambda s: s == '', row))) > 0:
		#	logger.warning('Discarded partial row, need to review:' + str(row))
		#elif len(row) == 1:
		#	logger.info('Probably found a title:' + str(row))
		#	if len(main_table2[-1]['rows']) > 0:
		#		main_table2.append({})
		#		main_table2[-1]['header'] = main_table2[-2]['header']
		#		main_table2[-1]['rows'] = []
		#		main_table2[-1]['tabletype'] = main_table2[-2]['tabletype']
		#	main_table2[-1]['title'] = row
		#else:
		#	main_table2[-1]['rows'].append(row)
		if 'title' not in table or table['title'] == "":
			table['title'] = ''
			logger.warning('Warning could not find title:' + str(table))
	return tables

# old funcs
def get_tables(pdf_path):
	dept = os.path.basename(os.path.dirname(pdf_path))
	return [page_to_table(page_layout) for page_layout in get_page_layouts(pdf_path)]


def stitch_together_tables(tables):
	main_table = []
	main_table2 = []
	for page in tables:
		for n, line in enumerate(page):
			# try to join lines that run over table breaks
			if (n == 0 and
					    len(line) > 1 and
					    len(list(filter(lambda s: s == '', line))) > 0 and
					    len(main_table) > 0):
				logger.info('Stitching rows:' + str(main_table[-1]) + str(line))
				for i in range(min(len(main_table[-1]), len(line))):
					main_table[-1][i] += ' '
					main_table[-1][i] += line[i]
				logger.info('Stitched result:' + str(main_table[-1]))
			else:
				main_table.append(line)

	tabletype = ''
	main_table2.append({})
	main_table2[-1]['header'] = []
	main_table2[-1]['rows'] = []
	main_table2[-1]['tabletype'] = 'unknown'
	for row in main_table:
		if row[0].lower().find('date') >= 0 or (row[0].lower() == 'date of meeting'):
			if len(main_table2[-1]['rows']) > 0:
				if 'title' not in main_table2[-1]:
					main_table2[-1]['title'] = ['']
					logger.warning('Warning could not find title:' + str(main_table2[-1]))
				main_table2.append({})
				main_table2[-1]['title'] = main_table2[-2]['title']
				main_table2[-1]['header'] = []
				main_table2[-1]['rows'] = []
				main_table2[-1]['tabletype'] = main_table2[-2]['tabletype']

			if len(row) >= 3:
				if row[2].lower() == 'purpose of meeting':
					logger.info('Probably found a meeting header row:' + str(row))
					main_table2[-1]['tabletype'] = 'meeting'
					main_table2[-1]['header'].append(row)
				else:
					logger.info('Probably found a header row:' + str(row))
					main_table2[-1]['header'].append(row)
			else:
				logger.info('Probably found a header row:' + str(row))
				main_table2[-1]['header'].append(row)

		elif all(map(lambda s: s == '', row)):
			logger.debug('Discarded empty row')
		elif len(list(filter(lambda s: s == '', row))) > 0:
			logger.warning('Discarded partial row, need to review:' + str(row))
		elif len(row) == 1:
			logger.info('Probably found a title:' + str(row))
			if len(main_table2[-1]['rows']) > 0:
				main_table2.append({})
				main_table2[-1]['header'] = main_table2[-2]['header']
				main_table2[-1]['rows'] = []
				main_table2[-1]['tabletype'] = main_table2[-2]['tabletype']
			main_table2[-1]['title'] = row
		else:
			main_table2[-1]['rows'].append(row)
	if 'title' not in main_table2[-1]:
		main_table2[-1]['title'] = ['']
		logger.warning('Warning could not find title:' + str(main_table2[-1]))
	return main_table2


def get_page_layouts(pdf_pathname):
	try:
		with open(pdf_pathname, 'rb') as fp:
			parser = PDFParser(fp)
			doc = PDFDocument()
			parser.set_document(doc)
			doc.set_parser(parser)

			doc.initialize("")

			if not doc.is_extractable:
				raise PDFTextExtractionNotAllowed

			resource_manager = PDFResourceManager()
			device = PDFPageAggregator(resource_manager, laparams=LAParams())
			interpreter = PDFPageInterpreter(resource_manager, device)

			layouts = []
			for page in doc.get_pages():
				interpreter.process_page(page)
				layouts.append(device.get_result())
			logger.debug('Opened PDF with ' + str(len(layouts)) + ' pages')
			return layouts
	except EnvironmentError:
		logger.error('Invalid PDF file: ' + pdf_pathname)
		return []
	except TypeError:
		logger.error('Invalid PDF file causes problems with pdfminer: ' + pdf_pathname)
		return []


def parse_test(pdfpath):
	page_layouts = get_page_layouts(pdfpath)

	print(len(page_layouts))
	print(page_layouts)

	objects_on_page = set(type(o) for o in page_layouts[3])
	print(objects_on_page)

	current_page = page_layouts[3]

	texts = []
	rects = []

	# seperate text and rectangle elements
	for e in current_page:
		if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
			texts.append(e)
		elif isinstance(e, pdfminer.layout.LTRect):
			rects.append(e)

	# sort them into
	characters = extract_characters(texts)
	print(characters)


TEXT_ELEMENTS = [
	pdfminer.layout.LTTextBox,
	pdfminer.layout.LTTextBoxHorizontal,
	pdfminer.layout.LTTextLine,
	pdfminer.layout.LTTextLineHorizontal
]


def flatten(lst):
	"""Flattens a list of lists"""
	return [subelem for elem in lst for subelem in elem]


def extract_characters(element):
	"""
	Recursively extracts individual characters from
	text elements.
	"""
	if isinstance(element, pdfminer.layout.LTChar):
		return [element]

	if any(isinstance(element, i) for i in TEXT_ELEMENTS):
		return flatten([extract_characters(e) for e in element])

	if isinstance(element, list):
		return flatten([extract_characters(l) for l in element])

	return []


gui_rects = []
chars = []


def get_rects():
	return gui_rects


def get_chars():
	return chars

def page_to_tables(page_layout):
	texts = []
	rectangles = []
	other = []

	for e in page_layout:
		if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
			texts.append(e)
		elif isinstance(e, pdfminer.layout.LTRect):
			rectangles.append(e)
		else:
			other.append(e)

	characters = extract_characters(texts)

	# Should set the limit from a reference, eg the area of a character in the smallest font
	rects_by_size = filter(lambda r: ((r.height * r.width) > 5), rectangles)
	#rects_by_size = list(filter(lambda x: x.width > 5, rects_by_size))
	#rects_by_size = sorted(rects_by_size, key=lambda r: r.height * r.width, reverse=True)
	rects_by_x = sorted(rects_by_size, key=lambda r: r.x0)

	table_rects = []
	remaining_rects = list(rects_by_x)
	groups = []
	remaining = len(remaining_rects)
	while remaining_rects:
		groups = compact(groups, remaining_rects)
		remaining_rects = list(filter(lambda x: len(x) == 1, groups))
		remaining_rects = flatten(remaining_rects)
		groups = list(filter(lambda x: len(x) != 1, groups))
		if len(remaining_rects) != remaining:
			remaining = len(remaining_rects)
		else:
			break

	# try filter(remaining_rects, intersects) ? keep filtering until len(0) result

	#final_rects = table_rects
	#for r in final_rects
	#groups = []
	#for k, g in itertools.groupby(rects_by_size, lambda x: x[0]):
	#	groups.append(list(g))

	#gui_rects = list(groups)

	#TODO page by page view
	#gui_rects.append(groups)
	bboxs = []

	tables = []
	for group in groups:
		xmin = group[0].x0
		xmax = group[0].x1
		ymin = group[0].y0
		ymax = group[0].y1
		for rect in group:
			xmin = min(rect.x0, xmin)
			xmax = max(rect.x1, xmax)
			ymin = min(rect.y0, ymin)
			ymax = max(rect.y1, ymax)
		bbox = pdfminer.layout.LTRect(1, (xmin, ymin, xmax, ymax))
		table_chars = list(filter(lambda x: PDF.rectangles.intersects(x, bbox), characters))
		#TODO page by page view
		#chars.append(table_chars)
		tables.append([bbox, group, table_chars])
	tables.reverse()

	return list(filter(lambda x: len(x['cells']) > 0, [process_table(table) for table in tables]))

def process_table(table):
	import matplotlib.pyplot as plt
	bbox = table[0]
	rects = table[1]
	tchars = table[2]
	bottom_line = pdfminer.layout.LTRect(1, (bbox.x0, bbox.y1, bbox.x1, bbox.y1))
	top_line = pdfminer.layout.LTRect(1, (bbox.x0, bbox.y0, bbox.x1, bbox.y0))
	left_line = pdfminer.layout.LTRect(1, (bbox.x0, bbox.y0, bbox.x0, bbox.y1))
	#rects = list(filter(lambda x: x.width > 5, rects))
	bottom_row = list(filter(lambda x: PDF.rectangles.intersects(x, bottom_line), rects))
	bottom_row = sorted(bottom_row, key=lambda r: r.x0)

	top_row = list(filter(lambda x: PDF.rectangles.intersects(x, top_line), rects))
	top_row = sorted(top_row, key=lambda r: r.x0)
	top_row = list(filter(lambda x: x.width > 5, top_row))

	bottom_row2 = list(filter(lambda x: x.y1 >= bbox.y1 - 10, rects))
	bottom_row2 = sorted(bottom_row2, key=lambda r: r.x0)

	top_row2 = list(filter(lambda x: x.y0 <= bbox.y0 + 10, rects))
	top_row2 = sorted(top_row2, key=lambda r: r.x0)

	columns = []
	rows = []
	for c in top_row:
		columns.append(pdfminer.layout.LTRect(1, (c.x0 - 1, bbox.y0 - 1, c.x1 + 1, bbox.y1 + 1)))

	if len(columns) == 0:
		logger.debug("Couldn't find any cols in this table, review")
		return {"title": "", "cells": []}
	first_column = list(filter(lambda x: PDF.rectangles.contains(columns[0], x), rects))
	first_column = list(filter(lambda x: PDF.rectangles.intersects(x, left_line), first_column))
	first_column = list(filter(lambda x: x.width < 5, first_column))
	first_column = sorted(first_column, key=lambda r: r.y0)

	for r in first_column:
		rows.append(pdfminer.layout.LTRect(1, (bbox.x0 - 1, r.y0 - 1, bbox.x1 + 1, r.y1 + 1)))
	rows.reverse()

	if len(rows) == 0:
		logger.debug("Couldn't find any rows in this table, review")
		return {"title": "", "cells": []}

	cell0 = list(filter(lambda x: PDF.rectangles.contains(columns[0], x) and PDF.rectangles.contains(rows[0], x), tchars))
	cell0 = sorted(cell0, key=lambda r: r.y0)
	title_row = ""

	#i, j = 0
	table_cells = []
	for r in rows:
		title = False
		table_row = []
		for c in columns:
			cell_r = pdfminer.layout.LTRect(1, (c.x0 - 2, r.y0 - 2, c.x1 + 2, r.y1 + 2))
			cell_right = pdfminer.layout.LTRect(1, (c.x1 - 2, r.y0 - 2, c.x1 + 2, r.y1 + 2))
			matches = list(filter(lambda x: PDF.rectangles.contains(cell_right, x), rects))
			cell = list(filter(lambda x: PDF.rectangles.contains(c, x) and PDF.rectangles.contains(r, x), tchars))
			cell = sorted(cell, key=lambda x: x.y0)
			cell.reverse()
			import itertools
			strings = []
			for k, g in itertools.groupby(cell, lambda x: x.y0):
				strings.append(list(g))
			string = ""
			for s in strings:
				t = sorted(s, key=lambda x: x.x0)
				string += ''.join(list(map(lambda u: u.get_text(), t)))
			if len(matches) == 0:
				print("missing row end")
				title = True
				break
			else:
				table_row.append(string.strip())

		if title:
			cell = list(filter(lambda x: PDF.rectangles.contains(r, x), tchars))
			cell = sorted(cell, key=lambda x: x.x0)
			string = list(map(lambda s: s.get_text(), cell))
			title_row = ''.join(string).strip()
		else:
			table_cells.append(table_row)

	print(title_row)
	for r in first_column:
		plt.plot(*zip(*r.pts))
		#plt.show()
		print()

	#plt.show()
	print()
	return {"title": title_row, "cells": table_cells}


def compact(groups, remaining_rects):
	while remaining_rects:
		r = remaining_rects.pop()
		for group in groups:
			for rect in group:
				if PDF.rectangles.intersects(r, rect):
					print(str(r) + " intersects " + str(rect))
					group.append(r)
					break
			else:
				continue
			break
		else:
			print("found no existing group, starting a new one")
			groups.append([r])
	return groups

def old_compact_start(rects_by_x, table_rects):
	for rect in rects_by_x:
		rects_by_x.remove(rect)
		found = False
		for r in table_rects:
			for r1 in r:
				if PDF.rectangles.intersects(r1, rect):
					r.append(rect)
					found = True
					break
			if found:
				break
		if not found:
			for rect2 in rects_by_x:
				#if rect == rect2:
				#	continue
				if PDF.rectangles.intersects(rect2, rect):
					table_rects.append([rect, rect2])
					rects_by_x.remove(rect2)

	table_rects, compacted = compact_groups(table_rects)
	while compacted:
		table_rects, compacted = compact_groups(table_rects)


def compact_groups(groups):
	compacted = False
	for group in groups:
		for group2 in groups:
			found = False
			if group2 != group:
				for rect in group:
					for rect2 in group2:
						if PDF.rectangles.intersects(rect2, rect):
							group += group2
							groups.remove(group2)
							found = True
							compacted = True
							break
					if found:
						break

	return groups, compacted

def page_to_table(page_layout):
	# todo the table stictching belongs in here
	texts = []
	rects = []
	other = []

	for e in page_layout:
		if isinstance(e, pdfminer.layout.LTTextBoxHorizontal):
			texts.append(e)
		elif isinstance(e, pdfminer.layout.LTRect):
			rects.append(e)
		else:
			other.append(e)

	# convert text elements to characters
	# and rectangles to lines
	characters = extract_characters(texts)
	#chars.append(characters)
	lines = [cast_as_line(r) for r in rects
	         if width(r) < 2 and
	         area(r) > 1]

	# match each character to a bounding rectangle where possible
	box_char_dict = {}
	for c in characters:
		# choose the bounding box that occurs the majority of times for each of these:
		bboxes = defaultdict(int)
		l_x, l_y = c.bbox[0], c.bbox[1]
		bbox_l = find_bounding_rectangle(l_x, l_y, lines)
		bboxes[bbox_l] += 1

		c_x, c_y = math.floor((c.bbox[0] + c.bbox[2]) / 2), math.floor((c.bbox[1] + c.bbox[3]) / 2)
		bbox_c = find_bounding_rectangle(c_x, c_y, lines)
		bboxes[bbox_c] += 1

		u_x, u_y = c.bbox[2], c.bbox[3]
		bbox_u = find_bounding_rectangle(u_x, u_y, lines)
		bboxes[bbox_u] += 1

		# if all values are in different boxes, default to character center.
		# otherwise choose the majority.
		if max(bboxes.values()) == 1:
			bbox = bbox_c
		else:
			bbox = max(bboxes.items(), key=lambda x: x[1])[0]

		if bbox is None:
			continue

		if bbox in box_char_dict.keys():
			box_char_dict[bbox].append(c)
			continue

		box_char_dict[bbox] = [c]

	# look for empty bounding boxes by scanning
	# over a grid of values on the page
	for x in range(100, 550, 10):
		for y in range(50, 800, 10):
			bbox = find_bounding_rectangle(x, y, lines)

			if bbox is None:
				continue

			if bbox in box_char_dict.keys():
				continue

			box_char_dict[bbox] = []

	return boxes_to_table(box_char_dict)


def flatten(lst):
	return [subelem for elem in lst for subelem in elem]


def extract_characters(element):
	if isinstance(element, pdfminer.layout.LTChar):
		return [element]

	if any(isinstance(element, i) for i in TEXT_ELEMENTS):
		elements = []
		for e in element:
			elements += extract_characters(e)
		return elements

	if isinstance(element, list):
		return flatten([extract_characters(l) for l in element])

	return []


def width(rect):
	x0, y0, x1, y1 = rect.bbox
	return min(x1 - x0, y1 - y0)


def length(rect):
	x0, y0, x1, y1 = rect.bbox
	return max(x1 - x0, y1 - y0)


def area(rect):
	x0, y0, x1, y1 = rect.bbox
	return (x1 - x0) * (y1 - y0)


def cast_as_line(rect):
	x0, y0, x1, y1 = rect.bbox

	if x1 - x0 > y1 - y0:
		return (x0, y0, x1, y0, "H")
	else:
		return (x0, y0, x0, y1, "V")


def does_it_intersect(x, xmin, xmax):
	return (x <= xmax and x >= xmin)


def find_bounding_rectangle(x, y, lines):
	v_intersects = [l for l in lines
	                if l[4] == "V"
	                and does_it_intersect(y, l[1], l[3])]

	h_intersects = [l for l in lines
	                if l[4] == "H"
	                and does_it_intersect(x, l[0], l[2])]

	if len(v_intersects) < 2 or len(h_intersects) < 2:
		return None

	v_left = [v[0] for v in v_intersects
	          if v[0] < x]

	v_right = [v[0] for v in v_intersects
	           if v[0] > x]

	if len(v_left) == 0 or len(v_right) == 0:
		return None

	x0, x1 = max(v_left), min(v_right)

	h_down = [h[1] for h in h_intersects
	          if h[1] < y]

	h_up = [h[1] for h in h_intersects
	        if h[1] > y]

	if len(h_down) == 0 or len(h_up) == 0:
		return None

	y0, y1 = max(h_down), min(h_up)

	return (x0, y0, x1, y1)


def chars_to_string(chars):
	if not chars:
		return ""
	rows = sorted(list(set(c.bbox[1] for c in chars)), reverse=True)
	text = ""
	for row in rows:
		sorted_row = sorted([c for c in chars if c.bbox[1] == row], key=lambda c: c.bbox[0])
		text += "".join(c.get_text() for c in sorted_row)
	return text


def boxes_to_table(box_record_dict):
	boxes = box_record_dict.keys()
	rows = sorted(list(set(b[1] for b in boxes)), reverse=True)
	table = []
	for row in rows:
		sorted_row = sorted([b for b in boxes if b[1] == row], key=lambda b: b[0])
		table.append([chars_to_string(box_record_dict[b]).strip() for b in sorted_row])
	return table


def find_tables(rects):
	rects_by_size = sorted(rects, key=lambda r: area(r))