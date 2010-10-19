import Point
import math, pygame
class CanonConfig:
	"""Data for CanonModels"""

	def __init__(self, skinFile, damage, radius, lifetime, speed, cooldown):
		self.skinFile = skinFile
		self.damage = damage
		self.radius = radius
		self.lifetime = lifetime
		self.speed = speed
		self.cooldown = cooldown
		self.selectable = False
	

class CanonShot:
	"""flying shot"""
	def __init__(self, canon, position, velocity, rotation):
		self.canon = canon
		self.config = canon.config
		self.rotation = rotation
		self.lifetime = canon.config.lifetime
		self.velocity = Point.Point(math.sin(rotation) * canon.config.speed, math.cos(rotation) * canon.config.speed) + velocity
		self.position = position
		self._sprite = None
		self.accelframe = False
		self.blinkframe = False
		self.selected = False
	
	def tick(self, clk):
		"""Flying. Returns true if bullet's lifetime isn't over yet"""
		self.lifetime -= clk
		if self.lifetime <= 0:
			return False
		self.position += self.velocity.resize(clk)
		return True
		
	def _getSurface(self):
		"""Returns rotated sprite image"""
		surf = pygame.image.load(self.canon.config.skinFile)
		#surf = pygame.transform.chop(surf, (0, 0, 2, 3))
		return pygame.transform.rotate(surf, self.rotation * 180 / math.pi)

	def getSprite(self):
		"""Returns Sprite"""
		if self._sprite == None:
			self._sprite = pygame.sprite.Sprite()
			self._sprite.image = self._getSurface()
		self._sprite.rect = self._sprite.image.get_rect()
		self._sprite.rect.center = (self.position.x, self.position.y)
		return self._sprite
		
	
class Canon:
	"""Canon Model"""
	cooltime = 0
	vehicle = None
	def __init__(self, canonConfig):
		self.config = canonConfig
	
	def shoot(self):
		"""Let's shoot that Canon! Returns None if cooldown wasn't over yet. \n
		Returns shot object otherwise."""
		if self.cooltime == 0:
			shot = CanonShot(self, self.vehicle.position, self.vehicle.velocity, self.vehicle.rotation)
			self.cooltime = self.config.cooldown
			return shot
		return None
	
	def attachOnTo(self, vehicle):
		if not self.vehicle:
			self.vehicle = vehicle
			vehicle.addCanon(self)
			return True
		return False
	
	def tick(self, clk):
		"""Per-round calculations concerning cannon as in cooldown, etc."""
		if self.cooltime > 0:
			self.cooltime -= clk
