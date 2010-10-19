import random, pygame
import Point

class Star:
	"""Class Star delivers functional one-pixel Stars"""
	def __init__(self, parent):
		"""@param: parent - a pygame-surface"""
		self.minz, self.maxz = 1, 16
		self.parent = parent
		self.x = random.randint(0, parent.get_width())
		self.y = random.randint(0, parent.get_width())
		self.z = random.randint(self.minz, self.maxz)
		self.fieldw = parent.get_width()
		self.fieldh = parent.get_height()
		rand = 32 + 223 * self.z / self.maxz
		self.color = pygame.Color(rand, rand, rand, 255)

	def genMove(self):
		"""Generates Motion of a star or comet"""
		move = Point.Point(random.random()*2-1, random.random()*2-1)
		return move.resize(4/self.z)
	
	def render(self, dx, dy):
		"""Renders the Star"""
		newx = (self.x + dx/self.z)%self.fieldw
		newy = (self.y + dy/self.z)%self.fieldh
		self.parent.set_at((newx, newy), self.color)


class StarLayer:
	"""A group of stars with almost equal distance to the viewer"""
	
	def __init__(self, parent, ammount, z):
		"""@param: parent - a pygame-surface"""
		self.parent = parent
		self.visible_size = parent.get_size()
		self.pos = Point.Point(self.visible_size[0], self.visible_size[1])
		self.z = z
		tmp = pygame.Surface(self.visible_size, parent.get_flags())
		#tmp.fill(pygame.Color("black"))
		#tmp.set_colorkey(pygame.Color("black"), pygame.RLEACCEL)
		for i in range(ammount):
			Star(tmp).render(0, 0)
		bigsize = (self.visible_size[0]*2, self.visible_size[1]*2)
		self.surf = pygame.Surface(bigsize, parent.get_flags())
		self.surf.fill(pygame.Color("black"))
		self.surf.set_colorkey(pygame.Color("black"), pygame.RLEACCEL)
		self.surf.blit(tmp, (0, 0))
		self.surf.blit(tmp, (self.visible_size[0], 0))
		self.surf.blit(tmp, (0, self.visible_size[1]))
		self.surf.blit(tmp, (self.visible_size[0], self.visible_size[1]))
		self.surf = self.surf.convert(self.surf)
	
	def render(self, dx, dy):
		"""Renders the star layer"""
		size = (self.visible_size[0]*2, self.visible_size[1]*2)
		newpos = (self.pos - Point.Point(dx, dy)/self.z).vmod(Point.Point(*size)/2)
		self.parent.blit(self.surf, (0, 0), newpos.tuplize()+size)#, pygame.BLEND_RGB_MAX)
