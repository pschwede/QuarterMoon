import Point
import math, pygame, random

PI = math.pi
TWOPI = 2*PI

class ShipConfig:
    """Data for ShipModels"""
    def __init__(self, skinFile, name, acceleration, maximumSpeed, rotationSpeed, maxhp, maxsp, selectable=True, controllable=True):
        self.skinFile = skinFile
        self.name = name
        self.acceleration = acceleration		# in px/s/s
        self.maximumSpeed = maximumSpeed		# in px/s
        self.rotationSpeed = rotationSpeed		# in radians/s
        self.blinkRatio = .1
        self.blinkRate = 1 # times per second
        surf = pygame.image.load(self.skinFile)
        self.w = surf.get_width() / 2
        self.h = surf.get_height() / 2
        self.cannons = []
        self.selectable = selectable
        self.controllable = controllable
        self.maxhp = maxhp
        self.maxsp = maxsp

    """Copies ShipModel"""
    def copy(self):
        copy = ShipConfig(self.skinFile, self.name, self.acceleration, self.maximumSpeed, self.rotationSpeed, self.selectable, self.controllable)
        copy.blinkRatio = self.blinkRatio
        copy.blinkRate = self.blinkRate
        copy.w = self.w
        copy.h = self.h
        copy.cannons = self.cannons
        return copy

"""Ship Model"""
class Ship:	
    def __init__(self, shipConfig, name=""):
        self.name = name
        self.config = shipConfig.copy()
        self._oldconfig = self.config.copy()
        self.sprite = pygame.sprite.Sprite()
        self.velocity = Point.Point(0., 0.)
        self.position = Point.Point(0., 0.)
        self.rotation = 0.0
        self.frame = random.randint(0, 1000)
        self.blinkframe = False
        self.dist = math.sqrt(self.config.w**2 + self.config.h**2)
        self.accelframe = False
        self.rotating = 0
        self.accelerating = False
        self.retrograde = False
        self.way = []
        self.waygone = 0
        self.state = "standby"
        self._surf = None
        self.selected = False
        self.enemypos = None
        self.hp = self.config.maxhp
        self.sp = self.config.maxsp

    def __str__(self):
        return self.name + "@" + str(self.position)

    def __repr__(self):
        return str(self)

    def rectangle(self):
        x = self.position.x-self.config.w/2
        y = self.position.y-self.config.h/2
        return pygame.Rect(x, y, self.config.w, self.config.h)

    def stopall(self):
        self.stopAcceleration()
        self.stopRetrograde()
        self.stopRotation()

    def toggleUserControl(self):
        if self.state != "user" and self.config.controllable:
            self.state = "user"
        else:
            self.stopall()
            self.state = "standby"

    def startAcceleration(self):
        self.accelerating = True
        self.accelframe = True

    def stopAcceleration(self):
        self.accelerating = False
        self.accelframe = False

    def startLeftRotation(self):
        self.rotating = 1

    def startRightRotation(self):
        self.rotating = -1

    def stopRotation(self):
        self.rotating = 0

    def startRetrograde(self):
        self.state = "user"
        self.retrograde = True

    def stopRetrograde(self):
        self.retrograde = False

    def goto(self, point, override=False):
        if self.way:
            if override:
                self.way = [(self.way[-1][0], self.position,), (self.position, point,)]
            else:
                self.way += [(self.way[-1][1], point,)]
        else:
            self.way = [(self.position, point)]

    def addCannon(self, canon):
        if len(self.config.cannons):
            self.config.cannons.append(canon)
        else:
            self.config.cannons = [canon]
        print self.config.cannons

    def shootCannon(self, index=0):
        print self.config.cannons
        if index < len(self.config.cannons):
            return self.config.cannons[index].shoot()
        return None

    def breakway(self, speed=None):
        """speculates the way till standing still"""
        if speed == None:
            speed = abs(self.velocity)
        rotway = PI / self.config.rotationSpeed
        rotway *= speed
        return rotway + speed * speed / 2 / self.config.acceleration

    """makes sure, ship will stand still"""
    def fullThrottle(self, clk):
        if self.velocity.exists() == 0:
            return True
        if self.rotation != (-self.velocity).radians():
            self.retrograde = True
            self.accelerating = False
            self.accelframe = False
        elif abs(self.velocity) > self.config.acceleration * clk:
            self.retrograde = False
            self.accelerating = True
            self.accelframe = True
        else:
            self.velocity = Point.Point(0, 0)
            self.retrograde = False
            self.accelerating = False
            self.accelframe = False
            return True # standing still
        return False # moving

    def turnTo(self, target, clk):
        toturn = target - self.rotation
        if abs(toturn) > abs(toturn - TWOPI):
            toturn -= 2*math.pi
        elif abs(toturn) > abs(toturn + TWOPI):
            toturn += 2*math.pi
        step = self.config.rotationSpeed * clk
        if(abs(toturn) > step):
            target = self.rotation + math.copysign(step,  toturn)

        # limit rotation
        if target > PI:
            target -= 2*TWOPI
        if target <= -TWOPI:
            target += 2*TWOPI
        return target

    def shootAt(self, target, clk):
        if self.rotation != target:
            self.turnTo(target, clk)
        else:
            self.shootCannon()

    def posAndRotOnWay(self, way, clk):
        """@param way: (start, end)"""
        dir = way[1] - way[0]			# direction
        s = abs(dir)		# distance
        try:
            te = s / self.config.maximumSpeed
            t = min(te, self.waygone + clk)		# time now
            pos = way[0].resize(1 - t / te)
            pos += way[1].resize(t / te)
            self.waygone = t
            rot = self.turnTo(dir.radians(), clk)
            accel = True
            return (pos, rot, accel)
        except ZeroDivisionError: 
            return (way[0], 0, False)

    def tick(self, clk):
        """manages changes according the flags; clk is the time since the last frame"""
        self._oldrot = self.rotation
        self.accelframe = self.accelerating
        self._oldaccelframe = self.accelframe
        self._oldblinkframe = self.blinkframe

        # next frame plz!
        self.frame += clk
        if self.frame > 1/ self.config.blinkRate:
            self.frame = 0
        self.blinkframe = self.frame > self.config.blinkRatio / self.config.blinkRate

        if self.accelerating:
            self.velocity = Point.Point(0, self.config.maximumSpeed).rotrad(self.rotation)
        else:
            self.velocity = Point.Point(0, 0)

        #vel = abs(self.velocity)
        #if vel > self.config.maximumSpeed:
        #	self.velocity *= self.config.maximumSpeed / vel

        self.position += self.velocity.resize(clk)
        self.rotation += self.rotating * self.config.rotationSpeed * clk

        if self.retrograde or self.way:
            # autopilot
                #target = self.rotation
                if self.retrograde: # turn back
                    self.rotation = self.turnTo((-self.velocity).radians(), clk)

                if self.enemypos:
                    self.shootAt(self.enemypos, clk)
                elif self.way:
                    target = self.rotation
                    if self.state == "standby": # make sure standing still
                        self.waygone = 0
                        self.velocity = 0
                        self.way[0] = (self.position, self.way[0][1])
                        self.state = "rotate"
                    if self.state == "rotate":
                        target = (self.way[0][1] - self.position).radians()
                        if self.rotation != target:
                            self.rotation = self.turnTo(target, clk)
                        else:
                            self.state = "go"
                    elif self.state == "go": # rotate to target
                        posrot = self.posAndRotOnWay(self.way[0], clk)
                        self.position, self.rotation, self.accelframe = posrot
                        if self.position == self.way[0][1]:
                            self.state = "waypoint done"
                    elif self.state == "waypoint done": # Huston, we landed
                        self.way.remove(self.way[0])
                        self.state = "standby"
                    #self.turnTo(target, clk)

        for canon in self.config.cannons:
            # propagate tick
            canon.tick(clk)
