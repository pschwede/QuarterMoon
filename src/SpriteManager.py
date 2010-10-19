import pygame, math

class SpriteManager:
	"""Keeps used Surfaces in the RAM"""
	def __init__(self, saverads=0):
		self.archive = {}
		self.saverads = saverads		# integer of how many rotated images shall be saved
		self.cakeparts = (2 * math.pi / self.saverads)		# needed for calc in line 10
	
	def __reducerad(self, rad):
		return round(rad / self.cakeparts)
		
	def __add(self, filename, accel, blink, rad):
		"""Attention: rad mustn't be reduced!"""
		if filename not in self.archive:
			self.archive[filename] = {}		# filename level
		if (accel, blink) not in self.archive[filename]:
			self.archive[filename][(accel, blink)] = {}		# (accel, blink) level
		if 0 not in self.archive[filename][(accel, blink)]:
			surf = pygame.image.load(filename)
			width = surf.get_rect().w/2
			height = surf.get_rect().h/2
			if accel:
				x = 0
			else:
				x = width
			if blink:
				y = height
			else:
				y = 0
			surf = pygame.transform.chop(surf, (x, y, width, height))
			self.archive[filename][(accel, blink)][0] = surf.copy()		# rad level
		else:
			surf = self.archive[filename][(accel, blink)][0]
		redrad = self.__reducerad(rad)
		surf = pygame.transform.rotate(surf, redrad * 360 / self.saverads)
		if self.saverads and redrad not in self.archive[filename][(accel, blink)]:
			self.archive[filename][(accel, blink)][redrad] = surf
		return self.archive[filename][(accel, blink)][redrad]
	
	def get(self, filename, accel, blink, rad):
		"""@param hash: something like (filename, accel, blink, rad)"""
		if self.saverads:
			try:
				return self.archive[filename][(accel, blink)][self.__reducerad(rad)]
			except KeyError:
				return self.__add(filename, accel, blink, rad)
		else:
			surf = self.archive[filename][(accel, blink)][0]
			return pygame.transform.rotate(surf, math.degrees(rad))
	
	def clear(self):
		self.archive = {}
