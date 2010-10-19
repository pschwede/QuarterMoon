class Preferences:
	"""Holds all options and preferences"""
	def __init__(self):
		self.interfacecolor = (0, 255, 0)
		self.fps = 33
		self.detail = 32
		self.backgroundRadiation = (17, 17, 17)
		self.interfacecolor = (0, 255, 0)
		self.dimensions = 480, 320
		self.scrollspeed = 0.3
		self.starDensity = .0006
		self.numVisibleStars = 150
		self.sameclicktolerance = 16		# px**2
		self.sameclickcooldown = .4		# seconds
		self.sameclickcooldown = int(self.sameclickcooldown * self.fps)	# frames
