
def line_intersects1(l1_x0, l1_x1, l1_y, l2_y0, l2_y1, l2_x):
	return (l1_y >= l2_y0) and (l1_y <= l2_y1) and (l2_x >= l1_x0) and (l2_x <= l1_x1)


def intersects1(r1, r2):
	# check if each x side intersects a y side
	return (line_intersects(r1.x0, r1.x1, r1.y0, r2.y0, r2.y1, r2.x0) or
	        line_intersects(r1.x0, r1.x1, r1.y1, r2.y0, r2.y1, r2.x1) or
	        line_intersects(r2.x0, r2.x1, r2.y0, r1.y0, r1.y1, r1.x0) or
	        line_intersects(r2.x0, r2.x1, r2.y1, r1.y0, r1.y1, r1.x1))

def line_intersects(l1, l2):
	return (l1[0] <= l2[1]) and (l2[0] <= l1[1])


def intersects(r1, r2):
	# check if each x side intersects a y side
	# TODO made the intersect function fuzzy but this should happen in the implementing function
	h_intersects = line_intersects((r1.x0 - 1, r1.x1 + 1), (r2.x0 - 1, r2.x1 + 1))
	v_intersects = line_intersects((r1.y0 - 1, r1.y1 + 1), (r2.y0 - 1, r2.y1 + 1))
	return h_intersects and v_intersects


def contains(r1, r2):
	return (r2.x0 >= r1.x0) and (r2.x1 <= r1.x1) and (r2.y0 >= r1.y0) and (r2.y1 <= r1.y1)

import pdfminer.layout
class RectangleGroup:
	rects = []
	bbox = pdfminer.layout.LTRect(1, (0, 0, 0, 0))

	def __init__(self, r):
		self.bbox = r
		self.rects.append(r)


	def intersects(self, r):
		return intersects(self.bbox, r)

	def add_rect(self, r):
		xmin = min(r.x0, self.bbox.x0)
		xmax = max(r.x1, self.bbox.x1)
		ymin = min(r.y0, self.bbox.y0)
		ymax = max(r.y1, self.bbox.y1)
		self.bbox = pdfminer.layout.LTRect(1, (xmin, ymin, xmax, ymax))
		self.rects.append(r)

	def add_intersecting_rects(self, rects):
		match = True
		while match:
			match = False
			for r in rects:
				if self.intersects(r):
					self.add_rect(r)
					rects.remove(r)
					match = True



if __name__ == '__main__':
	import pdfminer.layout
	r1 = pdfminer.layout.LTRect(1, (0, 0, 50, 50))
	r2 = pdfminer.layout.LTRect(1, (50, 0, 100, 50))
	r3 = pdfminer.layout.LTRect(1, (100, 0, 150, 50))
	r4 = pdfminer.layout.LTRect(1, (0, 50, 50, 100))
	r5 = pdfminer.layout.LTRect(1, (50, 50, 100, 100))
	r6 = pdfminer.layout.LTRect(1, (100, 50, 150, 100))
	r7 = pdfminer.layout.LTRect(1, (0, 100, 50, 150))
	r8 = pdfminer.layout.LTRect(1, (50, 100, 100, 150))
	r9 = pdfminer.layout.LTRect(1, (100, 100, 150, 150))
	r = pdfminer.layout.LTRect(1, (0, 0, 150, 150))

	assert contains(r, r1)
	assert contains(r, r2)
	assert contains(r, r3)
	assert contains(r, r4)
	assert contains(r, r5)
	assert contains(r, r6)
	assert contains(r, r7)
	assert contains(r, r8)
	assert contains(r, r9)
	assert not contains(r1, r)
	assert not contains(r2, r)
	assert not contains(r3, r)
	assert not contains(r4, r)
	assert not contains(r5, r)
	assert not contains(r6, r)
	assert not contains(r7, r)
	assert not contains(r8, r)
	assert not contains(r9, r)

	assert not contains(r1, r2)
	assert not contains(r1, r3)

	assert intersects(r, r1)
	assert intersects(r, r2)
	assert intersects(r, r3)
	assert intersects(r, r4)
	assert intersects(r, r5)
	assert intersects(r, r6)
	assert intersects(r, r7)
	assert intersects(r, r8)
	assert intersects(r, r9)

	assert intersects(r1, r)
	assert intersects(r2, r)
	assert intersects(r3, r)
	assert intersects(r4, r)
	assert intersects(r5, r)
	assert intersects(r6, r)
	assert intersects(r7, r)
	assert intersects(r8, r)
	assert intersects(r9, r)

	assert intersects(r1, r1)
	assert intersects(r1, r2)
	assert not intersects(r1, r3)
	assert intersects(r1, r4)
	assert intersects(r1, r5)
	assert not intersects(r1, r6)
	assert not intersects(r1, r7)
	assert not intersects(r1, r8)
	assert not intersects(r1, r9)

	assert intersects(r1, r1)
	assert intersects(r2, r1)
	assert not intersects(r3, r1)
	assert intersects(r4, r1)
	assert intersects(r5, r1)
	assert not intersects(r6, r1)
	assert not intersects(r7, r1)
	assert not intersects(r8, r1)
	assert not intersects(r9, r1)

	assert intersects(r5, r1)
	assert intersects(r5, r2)
	assert intersects(r5, r3)
	assert intersects(r5, r4)
	assert intersects(r5, r5)
	assert intersects(r5, r6)
	assert intersects(r5, r7)
	assert intersects(r5, r8)
	assert intersects(r5, r9)

	assert intersects(r1, r5)
	assert intersects(r2, r5)
	assert intersects(r3, r5)
	assert intersects(r4, r5)
	assert intersects(r5, r5)
	assert intersects(r6, r5)
	assert intersects(r7, r5)
	assert intersects(r8, r5)
	assert intersects(r9, r5)
