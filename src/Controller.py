#!/usr/bin/python
import pygame, sys
import SpaceView, ShipModel, Canon, Selection, Point, Preferences

DEBUGGING = False

class Controller:
	"""Controller of the MVC-Pattern.\n
	Handles ingame events and lists of models of the objects in game."""
	
	def __init__(self, config=None):
		"""Nothin yet, but everyone got it."""
		self.ships = set([])
		self.shots = set([])
		self.selection = Selection.Selection()
		self.done = False
		if config:
			self.config = config
		else:
			self.config = Preferences.Preferences()
		
		self.shipfunc = {
				"accel": 	lambda ship: ship.startAcceleration(),
				"accel_":	lambda ship: ship.stopAcceleration(),
				"turn":		lambda ship: ship.startRetrograde(),
				"turn_":	lambda ship: ship.stopRetrograde(),
				"rotl":		lambda ship: ship.startLeftRotation(),
				"rotr":		lambda ship: ship.startRightRotation(),
				"rot_":		lambda ship: ship.stopRotation(),
				"user":		lambda ship: ship.toggleUserControl(),
				"shoot":	lambda ship: self.addShot(ship.shootCanon()),
				"shoot_":	lambda ship: self.addShot(ship.shootCanon()),
				}
	
	def setView(self, view):
		"""Sets the visual user-interface (View in MVC)"""
		self.view = view
	
	def addShip(self, ship):
		"""Adds a ship to the game."""
		self.ships.add(ship)
		self.view.addObject(ship)
	
	def createShip(self, shipConfig, name=""):
		"""Creates a ship by it's config and adds it to the game and returns it"""
		ship = ShipModel.Ship(shipConfig, name)
		self.addShip(ship)
		return ship
	
	def remShip(self, id):
		"""Removes a ship by id"""
		self.ships.remove(id)
		self.view.removeObject(id)
	
	def addShot(self, shot=None):
		"""Adds a shoot particle to the game"""
		if shot:
			self.shots.add(shot)
			self.view.addObject(shot)
	
	def remShot(self, shot):
		"""Removes a shot from the game"""
		self.shots.remove(shot)
		self.view.removeObject(shot)
		
	def framedObjects(self, rect, l=[]):
		"""gathers objects framed by rectOnMaps"""
		rect.normalize()
		return [obj for obj in l if rect.collidepoint(obj.position.tuplize())]
	
	def pointedObjects(self, xy, l=[]):
		return [obj for obj in l if obj.rectangle().collidepoint(xy)]
	
	def selectRect(self, xy, wh, mode=0):
		"""Select units within rect from xy to xy+wh"""
		rectOnMap = pygame.Rect(xy, wh)
		lst = self.framedObjects(rectOnMap, self.ships)
		if mode == 0:
			self.selection.set(lst)
		elif mode == 1:
			self.selection.append(lst)
		else:
			self.selection.remove(lst)
	
	def selectPoint(self, xy, mode=2):
		"""Selects Unit at Point xy"""
		lst = self.pointedObjects(xy, self.ships)
		if lst:
			obj = lst[0]
			if mode == 2:	# toggle
				mode = (1, -1)[obj in self.selection]
			if mode == 0:
				self.selection.set([obj])
			elif mode == -1:
				self.selection.remove([obj])
			else:
				self.selection.append([obj])
	
	def selectType(self, obj, l=[]):
		self.selection.append([s for s in l if s.config.name == obj.config.name])
	
	def selectList(self, l=[], mode=0):
		"""Select units in List"""
		if mode == 1:
			self.selection.append(l)
		elif mode == -1:
			self.selection.remove(l)
		else:
			self.selection.set(l)
	
	def update(self, eve):
		"""Update-func of the MVC-Pattern. Called by View. \n
		Handles actual happenings in game"""
		if eve:
			print eve
			if eve[0] in self.shipfunc:
				map(self.shipfunc[eve[0]], self.selection)
			elif eve[0] == "end":
				self.stop()
			elif eve[0] == "lock":
				self.view.lockAt(self.selection),
			elif eve[0] == "unlck":
				self.view.lockAt([]),
			elif eve[0] == "goto":
				if eve[2].squaredabs() > self.config.sameclicktolerance**2:
					self.selection.goto(eve[1], eve[2].radians(), int(eve[2].squaredabs()))
				else:
					self.selection.goto(eve[1], (self.selection.position-eve[1]).radians(), int(eve[2].squaredabs()))
			elif eve[0] == "goto2":
				if eve[2].squaredabs() > self.config.sameclicktolerance**2:
					self.selection.goto(eve[1], eve[2].radians(), int(abs(eve[2])), False)
				else:
					self.selection.goto(eve[1], (self.selection.position-eve[1]).radians(), int(eve[2].squaredabs()), False)
			elif eve[0] == "select":
				if eve[3]:	# keep the most of selection
					if eve[2].squaredabs() > self.config.sameclicktolerance**2:	# no doubleclick
						self.selectRect(eve[1].tuplize(), eve[2].tuplize(), 1)
					else:
						# it will be removed from selection or added
						self.selectPoint(eve[1].tuplize(), 2)
				else:
					if eve[2].squaredabs() > self.config.sameclicktolerance**2:	# no doubleclick
						self.selectRect(eve[1].tuplize(), eve[2].tuplize(), 0)
					else:
						# selection will be purged before it will be selected
						self.selectPoint(eve[1].tuplize(), 0)
			elif eve[0] == "selectsame":
				pointed = self.pointedObjects(eve[1].tuplize(), self.ships)
				framed = self.ships#self.framedObjects(pygame.Rect(eve[2].tuplize(), eve[3].tuplize()))
				if pointed and framed:
					self.selectType(pointed[0], framed)
			else:
				print "Didn't understand: %s" % eve[0]
	
	def run(self):
		"""Starts the game loop"""
		while not self.done:
			clk = self.view.tick()
			for obj in self.ships:
				obj.tick(clk)
			for obj in [b for b in self.shots if not b.tick(clk)]:
				self.remShot(obj)
		sys.exit()
	
	def stop(self):
		"""Stops the game loop"""
		print "Game over"
		self.done = True

if __name__ == "__main__":
	c = Controller()
	v = SpaceView.SpaceView(c)
	v1 = SpaceView.SpaceView(c)
	c.setView(v)
	s2 = c.createShip(ShipModel.ShipConfig("../gfx/stations/wu_warp.png", "warp", 0, 0, 0.5, 500, 50), "Bob")
	ships = []
	for i in range(5):		# spawn some ships
		ships.append(c.createShip(ShipModel.ShipConfig("../gfx/ships/wu_hunter.png", "hunter", 100, 100, 6.28, 100, 50), "Paul"))
		#ships.append(c.createShip(ShipModel.ShipConfig("../gfx/ships/wu_spion.png", "spy", 100, 50, 6.28, 100, 50), "beep"))
	Canon.Canon(Canon.CanonConfig("../gfx/shots/wu_std.png", 1, 5, 2, 200, 0)).attachOnTo(ships[0])
	Canon.Canon(Canon.CanonConfig("../gfx/shots/wu_std.png", 1, 5, 2, 200, 0)).attachOnTo(ships[2])
	s2.startLeftRotation()
	s2.startAcceleration()
	c.selectList(ships)
	c.update(("goto", Point.Point(0, 64), Point.Point(0, -32)))
	v.lockAt([s2])
	c.run()
