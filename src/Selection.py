import Point, math

class Selection:
	"""Coordinates Selections"""
	def __init__(self, l=[]):
		self.__set = set(l)
		for o in l:
			o.selected = True
		self.xscale = 1
		self.yscale = 1
		self.arrowness = .5
		self.dist = 1
		self.depth = 2
		self.__recalcDist()
		self.position = self.avgPosition()
		self.ctrlmarks = True
	
	def avgPosition(self):
		# get the average point
		#p = reduce(lambda a, b: a+b, [o.position for o in self.__set], Point.Point(0, 0))
		if self.__set:
			p = sum([o.position for o in self.__set])
			p /= len(self.__set)
			return p
		return 0
	
	def __recalcDist(self):
		self.dist = reduce(max, [o.dist for o in self.__set], 1)
	
	def append(self, l):
		self.__set |= set(l)
		self.__recalcDist()
	
	def remove(self, l):
		self.__set -= set(l)
		self.__recalcDist()
	
	def set(self, l):
		self.__set = set(l)
		self.__recalcDist()
	
	def getList(self):
		return self.__set
	
	def __getitem__(self, idx):
		#list(self.__set)[idx].selected = True
		return list(self.__set)[idx]
	
	def __len__(self):
		return len(self.__set)
	
	def setArrowness(self, arrowness):
		self.arrowness = arrowness
	
	def goto(self, target, rad=0, squareddepth=288, override =True):
		"""Propagates goto method to selected objects"""
		if squareddepth != 0:
			self.depth = math.ceil(squareddepth/self.dist/self.dist)
		self.position = target
		l = list(self.__set)
		for i in range(len(l)):
			dist = self.dist
			k = max(1,math.ceil(len(l) / self.depth))
			# line
			t = Point.Point(0, (math.floor(i / k)) * dist * self.yscale)
			# side
			if (i % k - 1) % 2:		# even
				x = math.floor((i%k) / 2)
				t += Point.Point(x * dist * self.xscale, 0)
			else:		#odd
				x = (-math.floor((i%k) / 2) - 1)
				t += Point.Point(x * dist * self.xscale, 0)
			# arrowness
			t += Point.Point(0, abs(x) * self.arrowness * dist)
			l[i].goto(target + t.rotrad(rad), override)
