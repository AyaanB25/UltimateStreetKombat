#importing modules

import pygame
import random
import math
from pygame.locals import *
from typing import Final, final
#initializing game window
pygame.init()
HEIGHT = 700
WIDTH = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((255, 255, 255))
clock = pygame.time.Clock()
startplayBlue = False
startplayRed = False
statusRed = None
statusBlue = None

#defining fighter1
def pathfind(name):
    return ("./Assets/"+name+".png")

class Fighter(pygame.sprite.Sprite):

    def __init__(
        self,
        pos,
        spritesheet,
        id
    ):
        pygame.sprite.Sprite.__init__(self)

        #image and collision
        self.spritesheet = pathfind(spritesheet)
        self.spritesheet = pygame.image.load(self.spritesheet)
        self.id = id
        self.framesLeft = []
        self.framesRight = []
        for i in range(self.spritesheet.get_width() // 30):
            self.framesLeft.append(
                self.spritesheet.subsurface((i * 30, 0, 30, 45)))
            self.framesLeft[i] = pygame.transform.scale(
                self.framesLeft[i], (80, 120))
        for j in range(self.spritesheet.get_width() // 30):
            self.framesRight.append(
                pygame.transform.flip(self.framesLeft[j], True, False))
        self.image = self.framesLeft[0]
        self.frame = 0
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.side = "left"
        self.mask  = pygame.mask.from_surface(self.image)
        #physics variables
        self.ySpeed = 0
        self.xSpeed = 0
        #if fighter is grounded or not
        self.grounded = False

        self.jumpHeight = 15
        #acceleration of gravity
        self.gravity = 0.7
        #Setting the health value of the fighter
        self.health = 100
        self.dead = False
        self.side = "right"
        self.invincible = False
        self.invincibleTimer = 0
        self.regenTimer = 0
    #movement functions

    def hit(self, damage, knockback):
        
        self.regenTimer = 0
        if not self.invincible:
            self.health -= damage
            print(self.id + ": " + str(self.health))
            if self.health <= 0:
                self.kill()
                self.dead = True
            self.invincible = True
            self.invincibleTimer = 0
            x, y = knockback
            self.xSpeed += x
            self.ySpeed += y

    def moveLeft(self):
        #changing xspeed
        #if top speed is reached, nothing happens
        self.side = "left"
        if self.xSpeed >= -self.topSpeed:
            self.xSpeed -= self.accel
        else:
            self.xSpeed = -self.topSpeed

    def moveRight(self):
        #changing xspeed
        #if top speed is reached, nothing happens
        self.side = "right"
        if self.xSpeed <= self.topSpeed:
            self.xSpeed += self.accel
        else:
            self.xSpeed = self.topSpeed

    def jump(self):
        #decreases y speed to make the fighter jump
        if self.grounded:
            self.ySpeed -= self.jumpHeight

    #handles physics interactions

    def baseUpdate(self, allPlatforms):
        self.frame += 1
        self.regenTimer +=1
        if self.regenTimer >= 300 and self.regenTimer %15 == 0 and self.health<= 99:
                self.health += 1
        if self.side == "left":
            self.image = self.framesLeft[(self.frame // len(self.framesLeft)) %
                                         len(self.framesLeft)]
        else:
            self.image = self.framesRight[(self.frame // len(self.framesRight))
                                          % len(self.framesRight)]

        if abs(self.xSpeed) <= self.accel:
            if self.side == "left":
                self.image = self.framesLeft[0]
            else:
                self.image = self.framesRight[0]
        self.mask  = pygame.mask.from_surface(self.image)
        self.rect.move_ip(self.xSpeed, self.ySpeed)
        self.invincibleTimer += 1
        if self.invincibleTimer >= 20:
            self.invincible = False
        #this line of code is mostly to make the game look better
        #rather than suddenly slowing down movement, this makes it smoothly stop
        self.xSpeed *= 0.9
        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor
        self.grounded = (self.collidePlatform(allPlatforms)
                         or self.collideBoundaries())

        if not self.grounded:
            self.ySpeed += self.gravity

    def collideBoundaries(self):
        returnvalue = False
        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor
        if self.rect.clipline((-WIDTH, HEIGHT), (2 * WIDTH, HEIGHT)):
            if not self.grounded:
                self.ySpeed = 0
            self.grounded = True
            self.rect.bottom = HEIGHT
            returnvalue = True
        else:
            returnvalue = False
        if self.rect.clipline((0, 0), (0, HEIGHT)):
            self.rect.right = WIDTH
        if self.rect.clipline((WIDTH, 0), (WIDTH, HEIGHT)):
            self.rect.left = 0
        return returnvalue

    def collidePlatform(self, allPlatforms):
        returnvalue = False
        for platform in allPlatforms:
            if self.rect.clipline(platform.topline):
                self.rect.bottom = platform.rect.top

                self.ySpeed = 0
                returnvalue = True
            elif self.rect.clipline(platform.bottomline):
                self.rect.top = platform.rect.bottom + 1
                self.ySpeed = 0
            elif self.rect.clipline(platform.leftline):
                self.rect.right = platform.rect.left
                self.xSpeed = 0

            elif self.rect.clipline(platform.rightline):
                self.rect.left = platform.rect.right
                self.xSpeed = 0

        return returnvalue


class Fighter1(Fighter):

    def __init__(self, pos, color,id):

        Fighter.__init__(self, pos, "gunslinger"+color,id)
        #image and collision

        self.timer = 0
        self.cooldown = 12
        self.shootFlag = False
        self.topSpeed = 7
        self.accel = 1.2

        self.bullets = []

    #movement functions

    def attack(self, allSprites):
        if self.shootFlag:
            self.bullets.append(Bullet(self.rect.center, self.side,self))
            allSprites.add(self.bullets[-1])
            self.timer = 0
            self.shootFlag = False

    #handles physics interactions
    def update(self, allPlatforms, allAttacks):

        self.timer += 1
        if self.timer >= self.cooldown:
            self.shootFlag = True

        #applies current x and y speed to the fighter to make it move

        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor

        for bullet in self.bullets:
            if bullet.dead:
                self.bullets.remove(bullet)

        self.baseUpdate(allPlatforms)


class Fighter2(Fighter):

    def __init__(self, pos, color,id):
        Fighter.__init__(self, pos, "knight"+color,id)

        #image and collision

        self.topSpeed = 5
        self.accel = 1

        self.sword = None

        self.side = "right"
        self.health = 100

    #movement functions

    def attack(self, allSprites):
        if self.sword is None or self.sword.dead:
            self.sword = Sword(self.rect.center, self.side,self)
            allSprites.add(self.sword)

    #handles physics interactions
    def update(self, allPlatforms, allAttacks):
        #applies current x and y speed to the fighter to make it move

        #this line of code is mostly to make the game look better
        #rather than suddenly slowing down movement, this makes it smoothly stop

        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor

        if self.sword is not None:
            self.sword.position(self.rect.center)

        if self.sword is not None and self.sword.dead:
            self.sword = None

        self.baseUpdate(allPlatforms)


class Fighter3(Fighter):

    def __init__(self, pos, color,id):
        Fighter.__init__(self, pos, "skelebomber"+color,id)

        self.timer = 0
        self.dropBomb = False
        self.cooldown = 80

        self.bombs = []

        self.pellets = []

        self.topSpeed = 4
        self.accel = 0.9

        self.explosions = []

        self.health = 100

    #movement functions

    def attack(self, allSprites):
        if self.dropBomb:
            self.bombs.append(Bomb(self.rect.center,self))
            allSprites.add(self.bombs[-1])
            self.timer = 0
            self.dropBomb = False

    def update(self, allPlatforms, allAttacks):
        self.timer += 1
        if self.timer >= self.cooldown:
            self.dropBomb = True
        #applies current x and y speed to the fighter to make it move

        #this line of code is mostly to make the game look better
        #rather than suddenly slowing down movement, this makes it smoothly stop

        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor

        for bomb in self.bombs:
            if bomb.dead:

                self.bombs.remove(bomb)
                self.explosions.append(Explosion(bomb.rect.center, 100, 25,self))
                allAttacks.add(self.explosions[-1])
                xlist = "","right","left"
                ylist = "","top","bottom"
                for x in xlist:
                    for y in ylist:
                        if x != "" or y != "":
                            self.pellets.append(Pellet(bomb.rect.center, (x,y),self))
                            allAttacks.add(self.pellets[-1])
                

                
                

        for pellet in self.pellets:
            if pellet.dead:
                self.pellets.remove(pellet)
                self.explosions.append(Explosion(pellet.rect.center, 35, 10,self))
                allAttacks.add(self.explosions[-1])
        for explosion in self.explosions:
            if explosion.dead:
                self.explosions.remove(explosion)
                allAttacks.remove(explosion)

        self.baseUpdate(allPlatforms)


class Fighter4(Fighter):

    def __init__(self, pos, color,id):
        Fighter.__init__(self, pos, "dynaminer"+color,id)

        self.timer = 0
        self.cooldown = 30
        self.bomb = None
        self.dropBomb = True
        self.explosion = None

        self.topSpeed = 4.5
        self.accel = 1

        self.health = 100

    #movement functions

    def attack(self, allSprites):
        if self.bomb is None and self.dropBomb:
            self.bomb = RemoteBomb(self.rect.center,self)

            allSprites.add(self.bomb)

        if self.bomb and self.bomb.primed:
            self.bomb.dead = True
            self.timer = 0
            self.dropBomb = False

    def update(self, allPlatforms, allAttacks):

        self.timer += 1
        if self.timer >= self.cooldown:
            self.dropBomb = True
        #applies current x and y speed to the fighter to make it move

        #this line of code is mostly to make the game look better
        #rather than suddenly slowing down movement, this makes it smoothly stop

        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground

        if self.bomb is not None and self.bomb.dead:

            self.explosion = Explosion(self.bomb.rect.center, 150, 30,self)

            allAttacks.remove(self.bomb)
            self.bomb = None
            allAttacks.add(self.explosion)

        if self.explosion is not None and self.explosion.dead:
            self.explosion = None

        self.baseUpdate(allPlatforms)


class Fighter5(Fighter):

    def __init__(self, pos, color,id):
        Fighter.__init__(self, pos, "alchemist"+color,id)

        self.timer = 0
        self.cooldown = 35
        self.dropPotion = True
        self.potions = []
        self.poisons = []

        self.topSpeed = 5
        self.accel = 1

        self.health = 100

    def attack(self, allSprites):
        if self.dropPotion:
            self.potions.append(Potion(self.side, self.rect.center,self))
            self.timer = 0
            self.dropPotion = False
            allSprites.add(self.potions[-1])

    def update(self, allPlatforms, allAttacks):

        self.timer += 1
        if self.timer >= self.cooldown:
            self.dropPotion = True
        #applies current x and y speed to the fighter to make it move

        #this line of code is mostly to make the game look better
        #rather than suddenly slowing down movement, this makes it smoothly stop

        #this applies gravity to the fighter and sets its state
        #only runs if it is not touching the ground

        #this runs if the figher is touching the ground
        #makes sure that the fighter doesn't clip through the floor

        for potion in self.potions:
            if potion.dead:

                self.poisons.append(Poison(potion.rect.center,self))

                allAttacks.remove(potion)
                self.potions.remove(potion)
                allAttacks.add(self.poisons[-1])
        for poison in self.poisons:
            if poison.dead:
                self.poisons.remove(poison)

        self.baseUpdate(allPlatforms)


class Potion(pygame.sprite.Sprite):

    def __init__(self, side, pos,player):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = pygame.image.load(pathfind("potion"))
        self.frames = []
        for i in range(8):
            self.frames.append(self.spritesheet.subsurface(
                (i * 50, 0, 50, 50)))
            self.frames[i] = pygame.transform.scale(self.frames[i], (50, 50))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.side = side
        if self.side == "right":
            self.speed = 7
        else:
            self.speed = -7
        self.timer = 0
        self.dead = False
        self.lifetime = 600
        self.rect.center = pos
        self.damage = 7
        self.knockback = (0, 0)
        self.frame = 0
        self.mask  = pygame.mask.from_surface(self.image)
        self.player = player
    #def damageDealed(self):
    #   self.damage = 10
    #def knockbackDealed(self):
    #   self.knockback = 10
    #def positioning(self):
    #   self.rect.move_ip(self.speed, 0)
    def update(self, allPlatforms):
        self.frame += 1
        self.image = self.frames[((self.frame // 3) % 8)]
        self.mask  = pygame.mask.from_surface(self.image)
        self.rect.move_ip(self.speed, 0)
        self.timer += 1
        if (self.timer >= self.lifetime):
            self.kill()
            self.dead = True
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.kill()
            self.dead = True
        for platform in allPlatforms:
            if self.rect.colliderect(platform):
                self.kill()
                self.dead = True


class Poison(pygame.sprite.Sprite):

    def __init__(self, pos,player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(pathfind("poison"))
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.mask  = pygame.mask.from_surface(self.image)
        #self.rangeKill = False
        #self.poisonDone = False
        #self.poisoncooldown = 30
        self.dead = False
        self.timer = 0
        self.lifetime = 500
        self.damage = 1
        self.knockback = (0, 0)
        self.player = player
    def poisoning(self):
        if self.rangeKill:
            self.image = pygame.Surface((10, 10))
            self.image.fill("purple")
            self.rangeKill = False

    def update(self, filler1):
        self.timer += 1
        #if self.timer >= 30:
        #self.rangeKill = True
        if self.timer >= self.lifetime:
            self.timer = 0
            self.kill()
            self.dead = True


class Bullet(pygame.sprite.Sprite):

    def __init__(self, pos, side,player):
        pygame.sprite.Sprite.__init__(self)

        if side == "right":
            self.speed = 10
            self.image = pygame.image.load(pathfind("bulletLeft"))
            self.knockback = (7, -4)
        else:
            self.speed = -10
            self.image = pygame.image.load(pathfind("bulletRight"))
            self.knockback = (-7, -4)

        self.rect = self.image.get_rect()
        self.mask  = pygame.mask.from_surface(self.image)
        x, y = pos
        self.rect.center = (x, y + 7)
        self.dead = False
        self.player = player
        self.damage = 8

    def update(self, allPlatforms):
        self.rect.x += self.speed
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.kill()
            self.dead = True
        for platform in allPlatforms:
            if self.rect.colliderect(platform):
                self.kill()
                self.dead = True


class Bomb(pygame.sprite.Sprite):

    def __init__(self, pos,player):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = pygame.image.load(pathfind("bomb"))
        self.frames = []
        for i in range(27):
            self.frames.append(self.spritesheet.subsurface(
                (i * 64, 0, 64, 64)))
            self.frames[i] = pygame.transform.scale(self.frames[i], (40, 40))
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        x, y = pos
        self.rect.center = pos
        self.timer = 0
        self.lifetime = 81
        self.dead = False
        self.frame = 0
        self.player = player
        self.mask  = pygame.mask.from_surface(self.image)
    def update(self, filler1):
        self.image = self.frames[self.frame // 3]
        self.frame += 1
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()
            self.dead = True


class RemoteBomb(pygame.sprite.Sprite):

    def __init__(self, pos,player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(pathfind("dynamite"))
        pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect()
        x, y = pos
        self.rect.center = pos
        self.timer = 0
        self.primed = False
        self.readyTime = 20
        self.dead = False
        self.player = player
        self.mask  = pygame.mask.from_surface(self.image)
    def update(self, filler1):
        self.timer += 1
        if self.timer >= self.readyTime:
            self.primed = True


class Explosion(pygame.sprite.Sprite):

    def __init__(self, pos, size, damage,player):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = pygame.image.load(pathfind("explosion"))
        self.frames = []
        for i in range(12):
            self.frames.append(self.spritesheet.subsurface(
                (i * 96, 0, 96, 96)))
            self.frames[i] = pygame.transform.scale(self.frames[i],
                                                  (size, size))
        self.player = player
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        x, y = pos
        self.rect.center = pos
        self.timer = 0
        self.lifetime = 24
        self.dead = False
        self.damage = damage
        self.frame = 0
        self.knockback = (0, -(self.damage))
        self.mask  = pygame.mask.from_surface(self.image)
    def update(self, filler1):
        self.image = self.frames[self.frame // 2]
        self.frame += 1
        self.mask  = pygame.mask.from_surface(self.image)
        self.timer += 1

        if self.timer >= self.lifetime:
            self.kill()
            self.dead = True
    

class Pellet(pygame.sprite.Sprite):

    def __init__(self, pos, side,player):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(pathfind("pellet"))
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.dead = False
        self.lifetime = 90
        self.xSpeed = 0
        self.ySpeed = 0
        self.player = player
        self.timer = 0
        self.launchSide = side
        self.mask  = pygame.mask.from_surface(self.image)
        
        if self.launchSide[0] == "left":
            self.xSpeed = -3
        
        if self.launchSide[0] == "right":
            self.xSpeed = 3
            
        if self.launchSide[1] == "top":
            
            self.ySpeed = -3
        if self.launchSide[1] == "bottom":
            
            self.ySpeed = 3

    def update(self, filler1):
        self.rect.move_ip(self.xSpeed,self.ySpeed)

        if self.rect.right > WIDTH or self.rect.left < 0 or self.rect.top > HEIGHT or self.rect.bottom < 0:
            self.kill()
            self.dead = True

        self.timer += 1

        if self.timer >= self.lifetime:
            self.kill()
            self.dead = True


class Sword(pygame.sprite.Sprite):

    def __init__(self, pos, side,player):
        pygame.sprite.Sprite.__init__(self)
        self.spritesheet = pygame.image.load(pathfind("sword",))
        self.frames = []
        self.swordSide = side
        self.player = player
        for i in range(10):
            self.frames.append(
                self.spritesheet.subsurface(((i * 35), 0, 35, 50)))
            self.frames[i] = pygame.transform.scale(self.frames[i],
                                                    (35 * 4, 50 * 4))
        if self.swordSide == "left":
            for i in range(10):
                self.frames[i] = pygame.transform.flip(self.frames[i], True,
                                                       False)
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.mask  = pygame.mask.from_surface(self.image)
        x, y = pos
        self.rect.center = pos
        if self.swordSide == "right":
            self.rect.left = x+30
            self.knockback = (15, -7)
        else:
            self.rect.right = x-27
            self.knockback = (-15, -7)
        self.rect.left = x
        self.timer = 0
        self.lifetime = 20
        self.dead = False
        self.damage = 17
        self.frame = 0

    def update(self, filler1):
        self.image = self.frames[self.frame // 2]
        self.frame += 1
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()
            self.dead = True
        self.mask  = pygame.mask.from_surface(self.image)
    def position(self, pos):
        x, y = pos
        self.rect.center = pos
        if self.swordSide == "right":
            self.rect.left = x-30
        else:
            self.rect.right = x+30


class Platform(pygame.sprite.Sprite):

    def __init__(
        self,
        x,
        y,
    ):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(pathfind("platform"))
        self.image = pygame.transform.scale(self.image, (200, 25))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.leftline = (self.rect.topleft), (self.rect.bottomleft)
        self.rightline = (self.rect.topright), (self.rect.bottomright)
        self.topline = (self.rect.topleft), (self.rect.topright)
        self.bottomline = (self.rect.bottomleft), (self.rect.bottomright)


class Button:

    def __init__(self, text, color, x, y, width, height):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.color = color
        self.height = height
        self.sysfont = pygame.font.Font('./Assets/RobotoSlab-Regular.ttf', 20)
        self.renderedText = self.sysfont.render(self.text, True, ((0, 0, 0)))
        self.bg = (225,225,225)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 255, 255))
        
        pygame.draw.rect(self.image,self.bg,(0,0,self.width,self.height),0,20)
        pygame.draw.rect(self.image,self.color,(0,0,self.width,self.height),5,20)
        self.rect = self.image.get_rect()
        textPos = self.renderedText.get_rect()
        textPos = ((self.rect.width-textPos.width)/2), (self.rect.height-textPos.height)/2
        self.image.blit(self.renderedText, textPos )
        self.rect.center = (self.x, self.y)

    def click(self, mousePosition):
        return self.rect.collidepoint(mousePosition)
    def update(self):
        self.image.fill((255, 255, 255))

        pygame.draw.rect(self.image,self.bg,(0,0,self.width,self.height),0,20)
        pygame.draw.rect(self.image,self.color,(0,0,self.width,self.height),5,20)
        
        textPos = self.renderedText.get_rect()
        textPos = ((self.rect.width-textPos.width)/2), (self.rect.height-textPos.height)/2
        self.image.blit(self.renderedText, textPos )
        

class Healthbar():

    def __init__(self, health, spritesheet):
        self.spritesheet = pygame.image.load(pathfind("healthbar"))
        self.frames = []

        for i in range(50):
            self.frames.append(
                self.spritesheet.subsurface(((i * 104), 0, 104, 15)))
            self.frames[i] = pygame.transform.scale(self.frames[i], (104, 15))
        self.health = health
        self.image = pygame.Surface((104 + 30 + 5, 15 + 45))
        self.image.set_colorkey((0, 0, 0))
        self.displayFrame = spritesheet.subsurface((0, 0, 30, 45))
        if health > 1:
            self.image.blit(self.frames[50 - math.ceil(health // 2)], (35, 15))
            
        else:
            self.image.blit(self.frames[49], (35, 15))
        self.image.blit(self.displayFrame, (0, 0))
        self.rect = self.image.get_rect()
        


def startscreenCreate(x, y, width, height):
    buttonlistBlue = []
    buttonlistRed = []
    allButtons = []
    text = ""

    for i in range(5):
        if i == 0:
            text = "Gunslinger"
        elif i == 1:
            text = "Knight"
        elif i == 2:
            text = "Skelebomber"
        elif i == 3:
            text = "Dynaminer"
        elif i == 4:
            text = "Alchemist"

        buttonlistBlue.append(
            Button(text, ((0, 0, 255)), 150, (i * 100) + 200, width, height))
        allButtons.append(buttonlistBlue[-1])
        buttonlistRed.append(
            Button(text, ((255, 0, 0)), WIDTH-150, (i * 100) + 200, width, height))
        allButtons.append(buttonlistRed[-1])

    return allButtons, buttonlistBlue, buttonlistRed


def text(textmessage, x, y):
    font = pygame.font.Font('./Assets/RobotoSlab-Bold.ttf', 32)
    img = font.render(textmessage, True, (0, 0, 0))
    rect= img.get_rect()
    rect.center = (x,y)
    screen.blit(img,rect )


#making player1

#i moved this code to a lower place to make it more organized
"""allButtons, buttonlistBlue, buttonlistRed = startscreenCreate(
    WIDTH - 200, HEIGHT - 200, 200, 50)
startButton = Button("Start", ((0, 255, 0)), WIDTH / 2, HEIGHT - 100, 200, 50)
"""
#
#
#None of this is working because the if staments will only check the state of the buttons for one frame before passing on
#Yuo need to put it in a while loop that checks the state of the buttons every frame
#What i will do is i will pass the playerStatus after the inital for loop has finished.
#
"""if buttonlistBlue[0].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type1list.append(Fighter1((500, 500), "cowboyBlue.png"))
    allSprites.add(type1list[-1])
    allPlayers["player1"] = type1list[-1]
    
elif buttonlistBlue[1].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type2list.append(Fighter2((500, 500),
                              "knightBlue.png"))  #NEED TO CHANGE TO KNIGHT
    allSprites.add(type2list[-1])
    allPlayers["player1"] = type2list[-1]
elif buttonlistBlue[2].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type3list.append(Fighter3((500, 500),
                              "skeletonBlue.png"))  #CHANGE TO SKELETON
    allSprites.add(type3list[-1])
    allPlayers["player1"] = type3list[-1]
    statusBlue = "Fighter3"
elif buttonlistBlue[3].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type4list.append(Fighter4((500, 500), "minerBlue.png"))
    allSprites.add(type4list[-1])
    allPlayers["player1"] = type4list[-1]
elif buttonlistBlue[4].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type5list.append(Fighter5((500, 500), "wizardBlue.png"))
    allSprites.add(type5list[-1])
    allPlayers["player1"] = type5list[-1]

if buttonlistRed[0].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type1list.append(Fighter1((500, 500), "cowboyRed.png"))
    allSprites.add(type1list[-1])
    allPlayers["player2"] = type1list[-1]
elif buttonlistRed[1].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type2list.append(Fighter2((500, 500),
                              "knightRed.png"))  #NEED TO CHANGE TO KNIGHT
    allSprites.add(type2list[-1])
    allPlayers["player2"] = type2list[-1]
elif buttonlistRed[2].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type3list.append(Fighter3((500, 500),
                              "skeletonRed.png"))  #CHANGE TO SKELETON
    allSprites.add(type3list[-1])
    allPlayers["player2"] = type3list[-1]
elif buttonlistRed[3].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type4list.append(Fighter4((500, 500), "minerRed.png"))
    allSprites.add(type4list[-1])
    allPlayers["player2"] = type4list[-1]
elif buttonlistRed[4].click(
        pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
    type5list.append(Fighter5((500, 500), "wizardRed.png"))
    allSprites.add(type5list[-1])
    allPlayers["player2"] = type5list[-1]
"""

#INSIDE OF THE GAME LOOP


def gameLoop(bg, allPlayers, allPlatforms, allAttacks,players):

    run = True
    while run:
        screen.blit(bg, (0, 0))

        keys = pygame.key.get_pressed()

        #keyboard handler
        

        #collision handler

        
        for player in allPlayers:
            if player.id == "player1":
                if keys[pygame.K_LEFT]:
                    player.moveLeft()
                if keys[pygame.K_RIGHT]:
                    player.moveRight()
                if keys[pygame.K_UP]:
                    player.jump()
                if keys[pygame.K_DOWN]:
                    player.attack(allAttacks)
            if player.id ==  "player2":
                if keys[pygame.K_a]:
                    player.moveLeft()
                if keys[pygame.K_d]:
                    player.moveRight()
                if keys[pygame.K_w]:
                    player.jump()
                if keys[pygame.K_s]:
                    player.attack(allAttacks)
            if player.dead:
                print(player.id + " is dead")
                player.kill()
                players.remove(player.id)
            for attack in pygame.sprite.spritecollide(player, allAttacks,False,pygame.sprite.collide_mask):
                #collision good :)
                if player != attack.player:
                    
                    if isinstance(attack,(Potion,Bullet)):
                        player.hit(attack.damage, attack.knockback)
                        attack.kill()
                        attack.dead = True
                        
                    elif isinstance(attack,Pellet):
                        attack.kill()
                        attack.dead = True
                    elif isinstance(attack,(Explosion, Sword,Poison)):
                        player.hit(attack.damage, attack.knockback)
                    

            
            if player.id == "player1":
                screen.blit(Healthbar(player.health,
                                       player.spritesheet).image,(40,25))
            if player.id == "player2":
                screen.blit(Healthbar(player.health,
                                       player.spritesheet).image,(40,75))

        
        #updates and draws all sprites
        allPlayers.update(allPlatforms, allAttacks)
        allAttacks.update(allPlatforms)
        allPlayers.draw(screen)
        allAttacks.draw(screen)
        allPlatforms.draw(screen)
        for event in pygame.event.get():
            #quit program
            if event.type == pygame.QUIT:
                run = False

        #you use this instead of pygame.display.update when using sprites and surfaces
        pygame.display.flip()

        clock.tick(60)


allAttacks = pygame.sprite.Group()

allPlayers = pygame.sprite.Group()



#Ayaan you there
#Yup
#im heere
#have to eat soon though
allPlatforms = pygame.sprite.Group()
allPlatforms.add(Platform(100, 550))
allPlatforms.add(Platform(300, 400))
allPlatforms.add(Platform(500, 250))
allPlatforms.add(Platform(700, 400))
allPlatforms.add(Platform(900, 550))



bg = pygame.image.load("./Assets/background.jpg")

allButtons, buttonlistBlue, buttonlistRed = startscreenCreate(
    WIDTH - 200, HEIGHT - 200, 200, 50)
startButton = Button("Start", ((0, 255, 0)), WIDTH / 2, HEIGHT - 100, 200, 50)

fighterDict = {
    "Gunslinger": Fighter1,
    "Knight": Fighter2,
    "Skelebomber": Fighter3,
    "Dynaminer": Fighter4,
    "Alchemist": Fighter5
}

startplay = False
while not startplay:

    screen.fill((255, 255, 255))

    text("Ultimate Street Kombat", WIDTH/2, 100)
    for event in pygame.event.get():
        #quit program
        if event.type == pygame.QUIT:
            run = False

    for button in buttonlistBlue:
        if button.click(
                pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            statusBlue = button.text
            print("blue")
        if statusBlue == button.text:
            button.bg = button.color
        else:
            button.bg = (225,225,225)
    
    text(statusBlue, 200, 100)

    for button in buttonlistRed:

        if button.click(
                pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            statusRed = button.text
            print("red")
        if statusRed == button.text:
            button.bg = button.color
        else:
            button.bg = (225,225,225)
    text(statusRed, 800, 100)

    for button in allButtons:
        button.update()
        screen.blit(button.image, button.rect)

    screen.blit(startButton.image, startButton.rect)

    if startButton.click(
            pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
        startplay = True

    pygame.display.flip()

if startplay and statusBlue and statusRed:
    players = []
    allPlayers.add(fighterDict[statusBlue]((800, 500), "Blue","player1"))
    players.append("player1")
   
    allPlayers.add(fighterDict[statusRed]((200, 500), "Red","player2"))
    players.append("player2")
    

    gameLoop(bg, allPlayers,allPlatforms,allAttacks,players )
"""
        for person in type1list:
            for bullet in person.bullets:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(
                            bullet.rect):
                        player.hit(bullet.damage, bullet.knockback, name)
                        bullet.kill()
                        bullet.dead = True

        for person in type2list:
            for name, player in dict(allPlayers).items():
                if player != person and person.sword is not None and person.sword.rect.colliderect(
                        player.rect):
                    player.hit(person.sword.damage, person.sword.knockback,
                               name)

        for person in type3list:
            for explosion in person.explosions:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(
                            explosion.rect):
                        player.hit(explosion.damage, explosion.knockback, name)

        for person in type3list:
            for pellet in person.pellets:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(
                            pellet.rect):
                        pellet.kill()
                        pellet.dead = True

        for person in type4list:
            if person.explosion is not None:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(
                            person.explosion):
                        player.hit(person.explosion.damage,
                                   person.explosion.knockback, name)

        for person in type5list:
            for potion in person.potions:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(potion):
                        player.hit(potion.damage, potion.knockback, name)
                        potion.kill()
                        potion.dead = True

        for person in type5list:
            for poison in person.poisons:
                for name, player in dict(allPlayers).items():
                    if player != person and player.rect.colliderect(poison):
                        player.hit(poison.damage, poison.knockback, name)

"""
