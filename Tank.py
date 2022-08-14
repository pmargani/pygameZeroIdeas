import math
import time

from pgzero.actor import Actor

def deg2rad(deg):
    return deg * (math.pi/180.0)

class Obj(Actor):

    """
    Common class for all objects that move on the screen
    """
    def __init__(self, image, pos):
        Actor.__init__(self, image, pos)

        self.speed = 0.0 # pixels / draw

        #self.updateVelocity()

    def updateVelocity(self):
        "determine velocity vector"
        self.vx = math.cos(deg2rad(self.angle)) * self.speed  
        self.vy = -math.sin(deg2rad(self.angle)) * self.speed

    def update(self):
        "update our position according to the velocity vector"
        self.updateVelocity()

        self.x += self.vx
        self.y += self.vy

class Bullet(Obj):

    def __init__(self, image, pos, tankId, speed):
        Obj.__init__(self, image, pos)

        self.tankId = tankId
        self.speed = speed

class Rock(Obj):

    def __init__(self, image, pos, speed, lifetime=None):
        Obj.__init__(self, image, pos)

        self.speed = speed
        self.age = 0
        if lifetime is None:
            self.oldAge = 25
        else:
            self.oldAge = lifetime    

    def update(self):
        Obj.update(self)
        self.age += 1

    def isOld(self):
        return self.age > self.oldAge

class Tank(Obj):

    def __init__(self, image, pos, screenWidth, screenHeight, speed, id):
        Obj.__init__(self, image, pos)

        self.id = id
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        self.kills = 0
        
        self.maxAmmo = 10
        self.numAmmo = 7
        self.ammoCounter = 0
        self.timeUntilAmmo = 1000

        self.absSpeed = speed
        self.speed = 0.0
        self.angle = 0
        self.updateGunPosition()

        self.lastTimeShot = None # secs
        self.secondsPerShot = 1 # secs

    def updateGunPosition(self):
        "This is where the bullets fire from"    

        bulletOffset = 10
        offset = (self.width / 2) + bulletOffset
        offsetX = math.cos(deg2rad(self.angle)) * offset  
        offsetY = -math.sin(deg2rad(self.angle)) * offset

        self.gunX = self.x + offsetX
        self.gunY = self.y + offsetY

    def moveForward(self):
        self.speed = self.absSpeed
        self.updateGunPosition()

    def moveBackward(self):
        self.speed = -1.0 * self.absSpeed
        self.updateGunPosition()

    def stop(self):
        self.speed = 0    

    def rotateCW(self):
        self.angle -= self.absSpeed
        self.updateGunPosition()

    def rotateCCW(self):
        self.angle += self.absSpeed
        self.updateGunPosition()

    def bounceOff(self, obj):
        "We have collided with an object and need to bounce off it"

        pos = (obj.x, obj.y)
        angleToObj = self.angle_to(pos)

        # displace our position by the vector to this angle
        offset = 1.
        offsetX = math.cos(deg2rad(angleToObj)) * offset  
        offsetY = -math.sin(deg2rad(angleToObj)) * offset       

        self.x -= offsetX
        self.y -= offsetY

    def canShoot(self):
        if self.lastTimeShot is None and self.numAmmo > 0:
            # first shot!
            self.lastTimeShot = time.time()
            return True
        else:
            if time.time() - self.lastTimeShot > self.secondsPerShot and self.numAmmo > 0:
                self.lastTimeShot = time.time()
                return True

    def update(self):
        Obj.update(self)
        self.ammoCounter+=1
        if self.ammoCounter > self.timeUntilAmmo:
            if self.numAmmo < self.maxAmmo:
                self.numAmmo+=1
            self.ammoCounter = 0
        # keep tank on screen
        if self.x < 0:
            self.x = 10
        if self.x > self.screenWidth:
            self.x = self.screenWidth - 10
        if self.y < 0:
            self.y = 10
        if self.y > self.screenHeight:
            self.y = self.screenHeight - 10    