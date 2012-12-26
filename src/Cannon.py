import Point

import math
import pygame


class CannonConfig:
    """Data for CannonModels"""
    def __init__(self, skinFile, damage, radius, lifetime, speed, cooldown):
        self.skinFile = skinFile
        self.damage = damage
        self.radius = radius
        self.lifetime = lifetime
        self.speed = speed
        self.cooldown = cooldown
        self.selectable = False


class CannonShot:
    """flying shot"""
    def __init__(self, cannon, position, velocity, rotation):
        self.cannon = cannon
        self.config = cannon.config
        self.rotation = rotation
        self.lifetime = cannon.config.lifetime
        x = math.sin(rotation) * cannon.config.speed
        y = math.cos(rotation) * cannon.config.speed
        self.velocity = Point.Point(x, y) + velocity
        self.position = position.copy()
        self._sprite = None
        self.accelframe = False
        self.blinkframe = False
        self.selected = False
        print self

    """Flying. Returns true if bullet's lifetime isn't over yet"""
    def tick(self, clk):
        self.lifetime -= clk
        if self.lifetime <= 0:
            return False
        print self
        self.position += self.velocity.resize(clk)
        return True

    """Returns rotated sprite image"""
    def _getSurface(self):
        surf = pygame.image.load(self.cannon.config.skinFile)
        #surf = pygame.transform.chop(surf, (0, 0, 2, 3))
        return pygame.transform.rotate(surf, self.rotation * 180 / math.pi)

    """Returns Sprite"""
    def getSprite(self):
        if self._sprite is None:
            self._sprite = pygame.sprite.Sprite()
            self._sprite.image = self._getSurface()
        self._sprite.rect = self._sprite.image.get_rect()
        self._sprite.rect.center = (self.position.x, self.position.y)
        return self._sprite


"""Cannon Model"""
class Cannon:
    cooltime = 0
    vehicle = None

    def __init__(self, canonConfig):
        self.config = canonConfig

    """Let's shoot that Cannon! Returns None if cooldown wasn't over yet. \n
    Returns shot object otherwise."""
    def shoot(self):
        if self.cooltime == 0:
            shot = CannonShot(self, self.vehicle.position, self.vehicle.velocity, self.vehicle.rotation)
            self.cooltime = self.config.cooldown
            return shot
        return None

    def attachOnto(self, vehicle):
        if not self.vehicle:
            self.vehicle = vehicle
            vehicle.addCannon(self)
            return True
        return False

    """Per-round calculations concerning cannon as in cooldown, etc."""
    def tick(self, clk):
        self.cooltime = max(0, self.cooltime - clk)
