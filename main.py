import sys
import time
import random

import pygame

# look for joysticks
pygame.init()
numJoysticks = pygame.joystick.get_count()
print("Detected num Joysticks: ", numJoysticks)

from Tank import Tank
from Tank import Bullet
from Tank import Rock

WIDTH = 1000
HEIGHT = 1000

cornerOffset = 200

tank_1 = Tank("tank2", (cornerOffset, cornerOffset), WIDTH, HEIGHT, 1)
tank_2 = Tank("tank2", (WIDTH-cornerOffset, cornerOffset), WIDTH, HEIGHT, 2)
tank_2.angle = 180.0
tank_3 = Tank("tank2", (cornerOffset, HEIGHT-cornerOffset), WIDTH, HEIGHT, 3)
tank_4 = Tank("tank2", (WIDTH-cornerOffset, HEIGHT-cornerOffset), WIDTH, HEIGHT, 4)
tank_4.angle = 180.0

tanks = [tank_1, tank_2, tank_3, tank_4]

bullets = []

rubble = []

# make a wall going down the middle
brick = Actor("lego_brick", (700, 200))
bWidth = brick.width
# bricks = [brick]
bricks = []
for i in range(1, 37):
    yPos = 10 + (bWidth*i)
    xPos = (WIDTH/2) - (bWidth/2)
    brick = Actor("lego_brick", (xPos, yPos))
    bricks.append(brick)
    xPos = (WIDTH/2) + (bWidth/2)
    brick = Actor("lego_brick", (xPos, yPos))
    bricks.append(brick)

# make another wall
for i in range(1, 37):
    xPos = 10 + (bWidth*i)

    yPos = (HEIGHT/2) - (bWidth/2)
    brick = Actor("lego_brick", (xPos, yPos))
    bricks.append(brick)
    yPos = (HEIGHT/2) + (bWidth/2)
    brick = Actor("lego_brick", (xPos, yPos))
    bricks.append(brick)

#tank1._surf = pygame.transform.scale(tank1._surf, (50, 50))
# tank1._update_pos()
# tank1.angle = 0
# tank2.angle = 0


def explode(rubble, x, y):

    nRocks = random.randint(10,15)

    for n in range(nRocks):    
        rock = Rock('little_rock', (x, y))
        rock.speed = random.randint(3, 8)
        rock.angle = 360.0 * random.random()

        rubble.append(rock)

def getTankById(tanks, id):
    "We are using a list of tanks; a dict might be more appropriate"
    for tank in tanks:
        if tank.id == id:
            return tank
    return None

def controlTank(tank, bullets, forward, backward, cw, ccw, shoot):
    if forward or backward:
        if forward:
            tank.moveForward()
        else:
            tank.moveBackward()    
    else:   
        tank.stop()

    if ccw:
        tank.rotateCCW()

    if cw:
        tank.rotateCW()

    if shoot:

        if tank.canShoot():   
            bullet = Bullet("bullet1", (tank.gunX, tank.gunY), tank.id)
            bullet.angle = tank.angle
            bullets.append(bullet)

def draw():
    global bullets, bricks, tanks, rubble

    # screen.blit("background", (0,0))
    screen.fill((128,0,0))

    for tank in tanks:
        tank.draw()
    for bullet in bullets:
        bullet.draw()
    for brick in bricks:
        brick.draw() 
    for rock in rubble:
        rock.draw()       

def update(time_interval):
    global bullets, tanks, rubble

    now = time.time()

    if keyboard.escape:
        sys.exit()



    # *** Tank 1 Controls
    tank1 = getTankById(tanks, 1)
    if tank1 is not None:
        controlTank(
            tank1,
            bullets,
            keyboard.up,
            keyboard.down,
            keyboard.right,
            keyboard.left,
            keyboard.space)

        # if keyboard.up or keyboard.down:
        #     if keyboard.up:
        #         tank1.moveForward()
        #     else:
        #         tank1.moveBackward()    
        # else:   
        #     tank1.stop()

        # if keyboard.left:
        #     tank1.rotateCCW()

        # if keyboard.right:
        #     tank1.rotateCW()

        # if keyboard.space:

        #     if tank1.canShoot():   
        #         bullet = Bullet("bullet1", (tank1.gunX, tank1.gunY), tank1.id)
        #         bullet.angle = tank1.angle
        #         bullets.append(bullet)

    # *** End Tank1 Controls

    # *** Tank 2 Controls
    tank2 = getTankById(tanks, 2)
    if tank2 is not None:
        controlTank(
            tank2,
            bullets,
            keyboard.w,
            keyboard.s,
            keyboard.d,
            keyboard.a,
            keyboard.z)

        # if keyboard.w or keyboard.s:
        #     if keyboard.w:
        #         tank2.moveForward()
        #     else:
        #         tank2.moveBackward()    
        # else:   
        #     tank2.stop()

        # if keyboard.a:
        #     tank2.rotateCCW()

        # if keyboard.d:
        #     tank2.rotateCW()

        # if keyboard.z:

        #     if tank2.canShoot():   
        #         bullet = Bullet("bullet1", (tank2.gunX, tank2.gunY), tank2.id)
        #         bullet.angle = tank2.angle
        #         bullets.append(bullet)

    # *** End Tank2 Controls

    tank3 = getTankById(tanks, 3)
    if tank3 is not None:
        controlTank(
            tank3,
            bullets,
            keyboard.i,
            keyboard.k,
            keyboard.j,
            keyboard.l,
            keyboard.m)

    tank4 = getTankById(tanks, 4)
    if tank4 is not None:
        controlTank(
            tank4,
            bullets,
            keyboard.t,
            keyboard.g,
            keyboard.h,
            keyboard.f,
            keyboard.v)

    # keep tanks off bricks
    for brick in bricks:
        for tank in tanks:
            if brick.colliderect(tank):
                tank.bounceOff(brick)

    # remove bullets offscreen
    for i, bullet in enumerate(bullets):
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.pop(i)
            
    # remove bullets and tanks that collide
    for i, bullet in enumerate(bullets):
        for k, tank in enumerate(tanks):
            if bullet.tankId != tank.id and bullet.colliderect(tank):
                print("bullet hit tank!", tank, tank.id)
                explode(rubble, tank.x, tank.y)
                bullets.pop(i)
                tanks.pop(k)
                # this bullet is done, move to next one
                continue
        for j, brick in enumerate(bricks):
            if bullet.colliderect(brick):
                explode(rubble, brick.x, brick.y)    
                bricks.pop(j)    
                if bullets != []:
                    bullets.pop(i)

    # remove rubble that's too old
    for r, rock in enumerate(rubble):
        if rock.isOld():
            rubble.pop(r)

    # *** final updates        
    for tank in tanks:
        tank.update()    
    for bullet in bullets:
        bullet.update()
    for rock in rubble:
        rock.update()    
    # for brick in bricks:
        # brick.update()    


