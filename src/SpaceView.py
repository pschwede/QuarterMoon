import pygame, pygame.gfxdraw, math
import Star, Point, SpriteManager, Preferences

class SpaceView:
	"""Class SpaceView contains the complete visible interface of QM"""
	def __init__(self, controller, config=None):
		"""@param: controller - of a MVC-Pattern"""
		pygame.init()
		if config:
			self.config = config
		else:
			self.config = Preferences.Preferences()
		self._stars = set([])
		self._objs = set([])
		self.size = self.width, self.height = self.config.dimensions
		self.flags = pygame.DOUBLEBUF | pygame.RESIZABLE #| pygame.HWSURFACE
		self.screen = pygame.display.set_mode(self.size, self.flags)
		self.viewX, self.viewY = 0, 0
		self.resetStars()
		self.controller = controller
		self.clock = pygame.time.Clock()
		self.spriteManager = SpriteManager.SpriteManager(self.config.detail)
		self.lastclick = None
		self.lockObj = None
		self.sameclickcooldown = self.config.sameclickcooldown
	
	def addObject(self, obj):
		"""Adds an object to the render list"""
		self._objs.add(obj)
	
	def removeObject(self, obj):
		"""Removes an object from the render list"""
		self._objs.remove(obj)
	
	def centerAt(self, p):
		"""Moves the focus of the viewport to a point"""
		self.viewX = p.x + self.width/2
		self.viewY = p.y + self.height/2
	
	def lockAt(self, objlist):
		"""Sets objects to be observed"""
		self.lockObj = objlist
	
	def resetStars(self):
		"""Generates (new) stars for the background"""
		self._stars = set([])
		for z in range(2,5):
			self._stars.add(Star.StarLayer(self.screen, int(self.width*self.height*self.config.starDensity), z))
	
	def __getMouseOnMap(self, pos):
		return Point.Point(self.viewX - pos[0], self.viewY - pos[1])
	
	def __objCenter(self, obj):
		return (self.viewX - obj.position.x, self.viewY - obj.position.y)
	
	def __drawSelection(self, surf, rect, color):
		pygame.gfxdraw.vline(surf, rect.x, rect.y, rect.y+5, color)
		pygame.gfxdraw.vline(surf, rect.x+rect.w, rect.y+rect.h-5, rect.y+rect.h, color)
		pygame.gfxdraw.hline(surf, rect.x, rect.x+5, rect.y, color)
		pygame.gfxdraw.hline(surf, rect.x+rect.w-5, rect.x+rect.w, rect.y+rect.h, color)
	
	def __renderObj(self, obj):
		# render objects if visible
		surf = self.spriteManager.get(obj.config.skinFile, obj.accelframe, obj.blinkframe, obj.rotation)
		#surf = obj._getSurface()
		rect = surf.get_rect()
		rect.center = self.__objCenter(obj)
		self.screen.blit(surf, rect)
	
	def __renderSel(self, obj):
		rect = pygame.Rect(0, 0, obj.dist, obj.dist)
		rect.center = self.__objCenter(obj)
		self.__drawSelection(self.screen, rect, self.config.interfacecolor)
		pygame.gfxdraw.hline(self.screen, rect.x+2, rect.x+(rect.w-2)*obj.hp/obj.config.maxhp, rect.y+2, (255, 128, 0))
		pygame.gfxdraw.hline(self.screen, rect.x+2, rect.x+(rect.w-2)*obj.sp/obj.config.maxsp, rect.y+rect.h-2, (0, 128, 255))
	
	def tick(self):
		"""Renderloop of everything happening on screen. \n
		Also updates controller about events like mouse clicking and keys..."""
		if self.lockObj:
			# get the average point
			p = reduce(lambda a, b: a+b, [o.position for o in self.lockObj], Point.Point(0, 0))
			p /= len(self.lockObj)
			# focus the average point
			self.centerAt(p)
		self.screen.fill(self.config.backgroundRadiation)
		for star in self._stars:
			star.render(self.viewX, self.viewY)
		for obj in self._objs:
			self.__renderObj(obj)
		for obj in self.controller.selection:
			self.__renderSel(obj)
		if self.sameclickcooldown > 0:
			self.sameclickcooldown -= 1
		for event in pygame.event.get():
			# send messages to controller
			eve = None
			if event.type == pygame.VIDEORESIZE:
				self.size = event.size
				self.width = event.w
				self.height = event.h
				self.screen = pygame.display.set_mode(self.size, self.flags)
				self.resetStars()
			elif event.type == pygame.QUIT:
				eve = ["end"]
			elif event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_q, pygame.K_ESCAPE, ):
					eve = ["end"]
				elif pygame.key.get_mods() & pygame.KMOD_CTRL and event.key in (pygame.K_a, ):
					eve = ["select", self.__getMouseOnMap((0, 0)), Point.Point(-self.width, -self.height), 1]
				elif event.key in (pygame.K_UP, pygame.K_k, pygame.K_w):
					eve = ["accel"]
				elif event.key in (pygame.K_DOWN, pygame.K_j, pygame.K_s):
					eve = ["turn"]
				elif event.key in (pygame.K_LEFT, pygame.K_h, pygame.K_a):
					eve = ["rotl"]
				elif event.key in (pygame.K_RIGHT, pygame.K_l, pygame.K_d):
					eve = ["rotr"]
				elif event.key in (pygame.K_SPACE, ):
					eve = ["shoot"]
				elif event.key in (pygame.K_HOME, ):
					eve = ["lock"]
				elif event.key in (pygame.K_TAB, ):
					eve = ["user"]
			elif event.type == pygame.KEYUP:
				if event.key in (pygame.K_UP, pygame.K_k, pygame.K_w):
					eve = ["accel_"]
				elif event.key in (pygame.K_DOWN, pygame.K_j, pygame.K_s):
					eve = ["turn_"]
				elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_h, pygame.K_l, pygame.K_a, pygame.K_d):
					eve = ["rot_"]
				elif event.key in (pygame.K_SPACE, ):
					eve = ["shoot_"]
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					if self.lastclick:
						w = self.lastclick[0] - event.pos[0]
						h = self.lastclick[1] - event.pos[1]
						if math.sqrt(w * w + h * h) <= self.config.sameclicktolerance and self.sameclickcooldown:
							eve = ["selectsame", self.__getMouseOnMap(self.lastclick), self.__getMouseOnMap((self.viewX, self.viewY)), Point.Point(-self.width, -self.height)]
					if not eve:
						eve = ["select", self.__getMouseOnMap(event.pos), Point.Point(0, 0), pygame.key.get_mods() & pygame.KMOD_CTRL]
				self.lastclick = event.pos
				self.sameclickcooldown = self.config.sameclickcooldown
			elif event.type == pygame.MOUSEBUTTONUP:
				if event.button == 3:
					if pygame.key.get_mods() & pygame.KMOD_SHIFT:
						a = self.__getMouseOnMap(event.pos)
						b = self.__getMouseOnMap(self.lastclick)
						eve = ["goto2", a, b-a]
					else:
						a = self.__getMouseOnMap(event.pos)
						b = self.__getMouseOnMap(self.lastclick)
						eve = ["goto", a, b-a]
			elif event.type == pygame.MOUSEMOTION:
				if event.buttons == (0, 1, 0):
					eve = ["unlck"]
					self.centerAt(Point.Point(self.viewX-self.width/2, self.viewY-self.height/2) + Point.Point(*event.rel)/self.config.scrollspeed)
				elif self.lastclick and event.buttons == (1, 0, 0):
					w = event.pos[0] - self.lastclick[0]
					h = event.pos[1] - self.lastclick[1]
					if w * w + h * h > self.config.sameclicktolerance:
						pygame.gfxdraw.rectangle(self.screen, (self.lastclick, (w, h)), self.config.interfacecolor)
						eve = ["select", self.__getMouseOnMap(self.lastclick), Point.Point(-w, -h), pygame.key.get_mods() & (pygame.KMOD_SHIFT | pygame.KMOD_CTRL)]
			if eve:
				self.controller.update(eve)
		pygame.display.flip()
		return self.clock.tick(self.config.fps) / 1000.
