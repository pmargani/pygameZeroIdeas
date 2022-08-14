import sys
import time
import random
import math
import configparser

import pygame


from Tank import Tank
from Tank import Bullet
from Tank import Rock

# load config info
config = configparser.ConfigParser()
config.read("Tank.conf")
D = "DEFAULT"

def makeWalls():
    "Read config file to build walls"
    W = 'WALLS'
    numHDblWalls = int(config[W]['numWalls'])
    print("num walls: ", numHDblWalls)
    for i in range(0, numHDblWalls):
        makeWall(i+1)

def makeWall(i):
    "Make a single wall based off line in config file"
    print('makeDblWall: ', i)
    W = 'WALLS'
    start, stop = eval(config[W]['wall%i' % i])
    startX, startY = start
    stopX, stopY = stop

    xStart = startX * WIDTH
    yStart = startY * GAME_HEIGHT
    xStop = stopX * WIDTH
    yStop = stopY * GAME_HEIGHT

    # how long is the wall?
    xDiff = xStop - xStart
    yDiff = yStop - yStart
    length = math.sqrt(xDiff**2 + yDiff**2)
    thetaRads = math.atan2(yDiff, xDiff)

    stepInX = abs(xDiff) > abs(yDiff)
    print("stepInX: ", stepInX)
    stepDiff = xDiff if stepInX else yDiff

    # how many bricks in this wall?
    brickWidth = 25. # how to not hardcode this?
    yStep = brickWidth * math.sin(thetaRads)
    xStep = brickWidth * math.cos(thetaRads)

    numBricks = int( abs(stepDiff) / brickWidth)
    for i in range(numBricks):
        if stepInX:
            xPos = xStart + (i * brickWidth)
            yPos = yStart + (i * yStep)
        else:
            xPos = xStart + (i * xStep)
            yPos = yStart + (i * brickWidth)  
        print("brick at ", xPos, yPos)  
        brick = Actor("wall", (int(xPos), int(yPos)))
        bricks.append(brick)


# look for joysticks
pygame.init()
numJoysticks = pygame.joystick.get_count()
print("Detected num Joysticks: ", numJoysticks)
useJoysticks = numJoysticks != 0

# init all the joysticks we have
joysticks = []
for i in range(numJoysticks):
    j = pygame.joystick.Joystick(i)
    j.init()
    joysticks.append(j)

# Joystick constants
# north button goes forward
USE_JOYSTICK_BTNS = False
JOY_BTN_NORTH = 3     
JOY_BTN_SOUTH = 6    
JOY_BTN_EAST = 5     
JOY_BTN_WEST = 2    
JOY_BTN_CENTER = 4
JOY_BTN_COIN = 0
JOY_BTN_PLAYER = 1



# screen dimensions should be 1600 x 1000, game height of 800
WIDTH = 1600
HEIGHT = 1000

GAME_HEIGHT = 800

# colors
BLACK = (0, 0, 0)
WHITE = (128, 128, 128)
RED = (128, 0, 0)
GREEN = (0, 128, 0)

cornerOffset = 50

# all speeds are relative to the tank's speed
TANK_SPEED = int(config[D]["tankSpeed1"]) if not useJoysticks else int(config[D]["tankSpeed2"])
BULLET_SPEED = TANK_SPEED * 3
ROCK_SPEED = TANK_SPEED * 10

# initialize four players in four corners
tank_1 = Tank("tank1", (cornerOffset, cornerOffset), WIDTH, GAME_HEIGHT, TANK_SPEED, 1)
tank_2 = Tank("tank2", (WIDTH-cornerOffset, cornerOffset), WIDTH, GAME_HEIGHT, TANK_SPEED, 2)
tank_2.angle = 180.0
tank_3 = Tank("tank3", (cornerOffset, GAME_HEIGHT-cornerOffset), WIDTH, GAME_HEIGHT, TANK_SPEED, 3)
tank_4 = Tank("tank4", (WIDTH-cornerOffset, GAME_HEIGHT-cornerOffset), WIDTH, GAME_HEIGHT, TANK_SPEED, 4)
tank_4.angle = 180.0

tanks = [tank_1, tank_2, tank_3, tank_4]

bullets = []

rubble = []

bricks = []


# make walls based off config file
makeWalls()



def explode(rubble, x, y):
    "An Explosion causes random pieces of shrapnel to radiate out"

    # play an explosion sound
    sounds.eep.play()

    # how much shrpanel?
    minShrapnel = int(config[D]['minShrapnel'])
    maxShrapnel = int(config[D]['maxShrapnel'])
    nRocks = random.randint(minShrapnel, maxShrapnel)

    shrapnelLifetime = int(config[D]['shrapnelLifetime'])

    for n in range(nRocks):    
        rock = Rock('shrapnel', (x, y), ROCK_SPEED, lifetime=shrapnelLifetime)
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
            bullet = Bullet("bullet", (tank.gunX, tank.gunY), tank.id, BULLET_SPEED)
            bullet.angle = tank.angle
            bullets.append(bullet)
            # play shooting sound!
            sounds.eep.play()

def draw():
    global bullets, bricks, tanks, rubble

    # screen.blit("background", (0,0))
    screen.fill(BLACK)

    for tank in tanks:
        tank.draw()
    for bullet in bullets:
        bullet.draw()
    for brick in bricks:
        brick.draw() 
    for rock in rubble:
        rock.draw()       

    # draw borders for arean and player stats area
    # white = (128, 128, 128)
    screen.draw.rect(Rect((1,1),(WIDTH-2, GAME_HEIGHT)), WHITE)

    playerBoxWidth = WIDTH / 4
    for i in range(4):
        boxXstart = (playerBoxWidth*i) + 1
        r = Rect((boxXstart, GAME_HEIGHT + 1), (boxXstart + playerBoxWidth - 1, HEIGHT))
        screen.draw.rect(r, WHITE)

        screen.draw.text("Player %d" % (i+1), (boxXstart + 5, GAME_HEIGHT + 5))

        t = getTankById(tanks, i+1)

        txt = "Alive" if t is not None else "Dead"
        color = GREEN if t is not None else RED
        
        screen.draw.text(txt, (boxXstart + 5, GAME_HEIGHT + 20), color=color)
        
        #print kills
        tank = getTankById(tanks, i+1)
        if tank is not None:
            screen.draw.text("Kills: %d" % tank.kills, (boxXstart + 5, GAME_HEIGHT + 40), color=WHITE)

        # print debug info?
        testJoysticks = False
        if i < (numJoysticks-1) and testJoysticks:
            j = joysticks[i]
            ax1txt = "ax 1: %f" % j.get_axis(0)
            ax2txt = "ax 2: %f" % j.get_axis(1)
            screen.draw.text(ax1txt, (boxXstart + 5, GAME_HEIGHT + 35), color=color)
            screen.draw.text(ax2txt, (boxXstart + 5, GAME_HEIGHT + 50), color=color)

            btns = [1, 7, 8, 9]
            for k, btn in enumerate(btns):
                txt = "btn %d: %d" % (btn, j.get_button(btn))
                screen.draw.text(txt, (boxXstart + 5, GAME_HEIGHT + 65 + (k*15)), color=color)

def tankControls(tank, useJoysticks, numJoysticks, keys):

    if tank is None:
        return

    joyId = tank.id - 1
    if useJoysticks and numJoysticks > joyId:
        j = joysticks[joyId]
        if USE_JOYSTICK_BTNS:
            controlTank(
                tank,
                bullets,
                j.get_button(JOY_BTN_NORTH), # forward
                j.get_button(JOY_BTN_SOUTH), # backward
                j.get_button(JOY_BTN_EAST), # cw
                j.get_button(JOY_BTN_WEST), # ccw
                j.get_button(JOY_BTN_CENTER) # shoot         
            ) 
        else: 
            # use actual joystick!!  
            axis1 = j.get_axis(0)
            axis2 = j.get_axis(1)
            forward = backward = cw = ccw = False
            if axis1 >= .8:
                ccw = True
            if axis1 <= -.8:
                cw = True  
            if axis2 >= .8:
                forward = True
            if axis2 <= -.8:
                backward = True                 
            controlTank(
                tank,
                bullets,
                forward,
                backward,
                cw,
                ccw,
                # j.get_button(JOY_AXE_UP),
                # j.get_button(JOY_AXE_DOWN),
                # j.get_button(JOY_AXE_LEFT),
                # j.get_button(JOY_AXE_RIGHT),
                j.get_button(JOY_BTN_CENTER)          
            )     
    else:
        controlTank(
            tank, 
            bullets,
            keys[0],
            keys[1],
            keys[2],
            keys[3],
            keys[4]
        )    
            # keyboard.up,
            # keyboard.down,
            # keyboard.right,
            # keyboard.left,
            # keyboard.space)    

def update(time_interval):
    global bullets, tanks, rubble

    now = time.time()

    # user quitting?
    if keyboard.escape:
        sys.exit()
    if useJoysticks and numJoysticks > 2:
        j = joysticks[1]
        if j.get_button(JOY_BTN_COIN) and j.get_button(JOY_BTN_PLAYER):
            sys.exit()



    # *** Tank 1 Controls
    tank1 = getTankById(tanks, 1)
    if tank1 is not None:
        keys = (
            keyboard.up,
            keyboard.down,
            keyboard.right,
            keyboard.left,
            keyboard.space
        )
        tankControls(tank1, useJoysticks, numJoysticks, keys)



    # *** Tank 2 Controls
    tank2 = getTankById(tanks, 2)
    if tank2 is not None:
        keys = (
            keyboard.w,
            keyboard.s,
            keyboard.d,
            keyboard.a,
            keyboard.b
        )
        tankControls(tank2, useJoysticks, numJoysticks, keys)


    tank3 = getTankById(tanks, 3)
    if tank3 is not None:
        keys = (
            keyboard.i,
            keyboard.k,
            keyboard.j,
            keyboard.l,
            keyboard.m
        )
        tankControls(tank3, useJoysticks, numJoysticks, keys)


    tank4 = getTankById(tanks, 4)
    if tank4 is not None:
        keys = (
            keyboard.t,
            keyboard.g,
            keyboard.h,
            keyboard.f,
            keyboard.v
        )        
        tankControls(tank4, useJoysticks, numJoysticks, keys)
     


    # *** End Tank Controls

    # keep tanks off bricks
    for brick in bricks:
        for tank in tanks:
            if brick.colliderect(tank):
                tank.bounceOff(brick)

    # remove bullets offscreen
    for i, bullet in enumerate(bullets):
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > GAME_HEIGHT:
            bullets.pop(i)
            
    # remove bullets and tanks that collide
    for i, bullet in enumerate(bullets):
        for k, tank in enumerate(tanks):
            if bullet.tankId != tank.id and bullet.colliderect(tank):
                print("bullet hit tank!", tank, tank.id)
                print("Tank ", bullet.tankId, " got a kill.")
                tanks[bullet.tankId-1].kills+=1
                #print("Tank 1 has ", tanks[0].kills, " kills")
                
                explode(rubble, tank.x, tank.y)
                bullets.pop(i)
                tanks.pop(k)
                sounds.eep.play()

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


