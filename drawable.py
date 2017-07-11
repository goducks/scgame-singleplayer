import sdl2
import sdl2.ext
import localmath as lm
import spritedrawer
from random import randint
from abc import ABCMeta, abstractmethod
import sdl2.sdlmixer as sdlmixer
import os

class GameObject():
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, time):
        pass

class Drawable(GameObject):
    # the "static" draw list
    drawList = list()

    if (sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO) < 0):
        exit(1)
    if (sdlmixer.Mix_OpenAudio(22050, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024) < 0):
        print "Mix_OpenAudio: %s\n", sdlmixer.Mix_GetError()
        exit(2);

    def __init__(self, renderer, width, height, x = 0, y = 0, filename = ""):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.create_texture_sprite(renderer, size=(width, height))
        self.filename = filename
        self.renderer = renderer
        self.sprite = sprite
        self.sprite.height = height
        self.sprite.width = width
        self.sprite.position = x, y
        # set a random color
        self.sprite.color = sdl2.ext.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        # add to global drawList
        Drawable.drawList.append(self)

    # on class instance destroy, remove from drawList
    def delete(self):
        # print "removing from drawlist"
        Drawable.drawList.remove(self)

    # force clear drawList contents
    @staticmethod
    def clearAll():
        del Drawable.drawList[:]

    def update(self, time):
        pass

    def getWidth(self):
        pass

    def getHeight(self):
        pass

    def getX(self):
        pass

    def getY(self):
        pass


class filledRect(Drawable):

    def __init__(self, renderer, width, height, x = 0, y = 0, filename = ""):
        factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
        sprite = factory.create_texture_sprite(renderer, size=(width, height))
        self.filename = filename
        self.renderer = renderer
        self.sprite = sprite
        self.sprite.height = height
        self.sprite.width = width
        self.sprite.position = x, y
        # set a random color
        self.sprite.color = sdl2.ext.Color(randint(0, 255), randint(0, 255), randint(0, 255), 255)
        # add to global drawList
        Drawable.drawList.append(self)

    def update(self, time):
        pass

    def render(self):
        self.renderer.color = self.sprite.color
        # for now, we're only drawing filled rectangles. we can specialize this function as necessary
        # draw_rect will draw outline only, fill fills them in
        # renderer.draw_rect([(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)])
        self.renderer.fill([(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)])

    def getHeight(self):
        return self.sprite.height

    def getWidth(self):
        return self.sprite.width

    def getX(self):
        return self.sprite.x

    def getY(self):
        return self.sprite.y

class Player(spritedrawer.spriteMaker, Drawable):

    def __init__(self, renderer, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        playerwidth, playerheight = lm.SC(width, height)
        playerposx, playerposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        playerposx -= playerheight + playerheight / 2
        playerposy -= playerheight + 10
        super(Player, self).__init__(renderer, int(playerposx), int(playerposy), int(playerwidth), int(playerheight),
                                     "ship.png", None, False)
        Player.renderer = renderer
        Player.score = 0
        Player.vx = 0
        Player.width = playerwidth
        Player.height = playerheight
        Player.maxwidth = wwidth
        Player.maxheight = wheight
        Player.bullets = list()
        Player.lives = 3
        Player.bulletcount = 5
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'shoot.wav')
        Player.shootsound = sdlmixer.Mix_LoadWAV(path)
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'explosion.wav')
        Player.hitsound = sdlmixer.Mix_LoadWAV(path)

    def delete(self):
        super(Player, self).delete()

    def fire(self):
        for bullet in self.bullets:
            if bullet.sprite.y < -16:
                self.bullets.remove(bullet)
        if self.bulletcount >= .5:
            self.bulletcount = 0
            self.bullets.append(Bullet(Player.renderer, int(self.x + self.width / 2),
                                       self.y, self.maxwidth, self.maxheight))
            sdlmixer.Mix_PlayChannel(-1, self.shootsound, 0)

    def getInput(self, event):
        if sdl2.SDL_HasScreenKeyboardSupport:
            if event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.vx = -.75
                if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.vx = .75
                if event.key.keysym.sym == sdl2.SDLK_SPACE:
                    self.fire()
            elif event.type == sdl2.SDL_KEYUP:
                if event.key.keysym.sym in (sdl2.SDLK_LEFT, sdl2.SDLK_RIGHT):
                    self.vx = 0

    def lostlife(self):
        sdlmixer.Mix_PlayChannel(-1, self.hitsound, 0)
        self.lives -= 1

    def update(self, time):
        self.bulletcount += time
        # width and height of sprite so it can stay in bounds
        swidth, sheight = self.width, self.height
        # move sprite
        self.x += lm.NDCToSC_x(self.vx * time, self.maxwidth)
        # checks if sprite is past the min (0)
        self.x = max(0, self.x)
        # position + sprite size
        posx = self.x + swidth
        # if the position + sprite size extends past max, stop it there
        if posx > self.maxwidth:
            self.x = self.maxwidth - swidth

class Bullet(filledRect):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(Bullet, self).__init__(renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        Bullet.maxheight = wheight
        Bullet.vy = -.5

    def delete(self):
        super(Bullet, self).delete()

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        # print "removing bullet"
        self.delete()

class Enemy(spritedrawer.spriteMaker, Drawable):
    def __init__(self, renderer, points, speed, wwidth, wheight, posx=0.0, posy=0.0, width=0.0, height=0.0):
        enemywidth, enemyheight = lm.NDCToSC(width, height, wwidth, wheight)
        enemyposx, enemyposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        name = "enemy" + str(points/10) + ".png"
        super(Enemy, self).__init__(renderer, int(enemyposx), int(enemyposy), int(enemywidth), int(enemyheight),
                                    name, None, False)
        self.points = points
        Enemy.renderer = renderer
        Enemy.width = enemywidth
        Enemy.height = enemyheight
        Enemy.maxwidth = wwidth - lm.NDCToSC_x(.05, wwidth)
        Enemy.minwidth = lm.NDCToSC_x(.05, wwidth)
        Enemy.maxheight = wheight
        Enemy.vx = speed
        Enemy.vy = 0
        Enemy.move = True
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'invaderkilled.wav')
        Enemy.deathsound = sdlmixer.Mix_LoadWAV(path)

    def delete(self):
        super(Enemy, self).delete()

    def update(self, time):
        self.y += lm.NDCToSC_y(Enemy.vy * time, self.maxheight)
        if self.move:
            self.x += lm.NDCToSC_x(Enemy.vx * time, self.maxwidth)

    def shoot(self):
        for bullet in EnemyController.bullets:
            if bullet.sprite.y > self.maxheight:
                EnemyController.bullets.remove(bullet)
        if len(EnemyController.bullets) < 1:
            EnemyController.bullets.append(EnemyBullet(Enemy.renderer, int(self.x + self.width / 2),
                                            self.y, self.maxwidth, self.maxheight))

    def remove(self):
        sdlmixer.Mix_PlayChannel(-1, self.deathsound, 0)
        self.delete()

class EnemyController(GameObject):
    def __init__(self, renderer, wwidth, wheight):
        EnemyController.level = 1
        EnemyController.enemies = self.createEnemies(renderer, wwidth, wheight)
        EnemyController.top = self.enemies[0].y
        EnemyController.left = self.enemies[0].x
        EnemyController.right = self.enemies[-1].x + self.enemies[-1].width
        EnemyController.bottom = self.enemies[-1].y + self.enemies[-1].height
        EnemyController.renderer = renderer
        EnemyController.wwidth = wwidth
        EnemyController.wheight = wheight
        EnemyController.counter = 0
        EnemyController.timer = 0
        EnemyController.bullets = list()
        EnemyController.shoottime = randint(90, 100)
        EnemyController.UFOactive = False
        EnemyController.UFOtime = randint(12, 15)
        EnemyController.UFOcounter = 0
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'fastinvader4.wav')
        EnemyController.sound = sdlmixer.Mix_LoadWAV(path)
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'levup.wav')
        EnemyController.resetsound = sdlmixer.Mix_LoadWAV(path)

    def createEnemies(self, renderer, wwidth, wheight):
        enemies = list()
        yoffset = .06
        xoffset = .09
        scorecountdown = 15
        points = 40
        speed = .25 * self.level
        y = .125
        while y < .45:
            x = .1
            while x < .85:
                if scorecountdown == 0 and not points == 10:
                    points -= 10
                    scorecountdown = 15
                enemy = Enemy(renderer, points, speed, wwidth, wheight, x, y, 0.072, 0.05)
                enemies.append(enemy)
                scorecountdown -= 1
                x += xoffset
            y += yoffset
        return enemies

    def update(self, time):
        Enemy.vy = 0
        if Enemy.move:
            distancemoved = lm.NDCToSC_x(Enemy.vx * time, self.wwidth)
        else:
            distancemoved = 0
        EnemyController.left += distancemoved
        EnemyController.right += distancemoved
        if EnemyController.right > Enemy.maxwidth or EnemyController.left < Enemy.minwidth:
            Enemy.vx = -Enemy.vx
            Enemy.vy = .5
            EnemyController.counter = 15
        if EnemyController.timer == self.shoottime:
            shooter = randint(0, len(self.enemies) - 1)
            self.enemies[shooter].shoot()
            EnemyController.timer = 0
        if EnemyController.UFOcounter >= self.UFOtime and not EnemyController.UFOactive:
            ufo = UFO(self.renderer, self.wwidth, self.wheight)
            EnemyController.UFOactive = True
            EnemyController.UFOcounter = 0
            EnemyController.enemies.append(ufo)
        if EnemyController.counter >= .75:
            Enemy.move = True
            sdlmixer.Mix_PlayChannel(-1, self.sound, 0)
            EnemyController.counter = 0
        else:
            Enemy.move = False
            EnemyController.counter += time
        EnemyController.timer += 1
        EnemyController.UFOcounter += time

    def checkWin(self, player):
        enemyheight = self.enemies[-1].y + self.enemies[0].height
        if enemyheight >= player.y:
            return True
        else:
            return False

    def removebullet(self, bullet):
        EnemyController.bullets.remove(bullet)
        bullet.remove()

    def reset(self):
        EnemyController.level += .8
        del self.enemies[:]
        EnemyController.enemies = self.createEnemies(self.renderer, self.wwidth, self.wheight)
        EnemyController.top = self.enemies[0].y
        EnemyController.left = self.enemies[0].x
        EnemyController.right = self.enemies[-1].x + self.enemies[-1].width
        EnemyController.bottom = self.enemies[-1].y + self.enemies[-1].height
        sdlmixer.Mix_PlayChannel(-1, self.resetsound, 0)

class UFO(spritedrawer.spriteMaker, Drawable):
    def __init__(self, renderer, wwidth, wheight):
        enemywidth, enemyheight = lm.NDCToSC(.108, .05, wwidth, wheight)
        ypos = lm.NDCToSC_y(.075, wheight)
        pickside = randint(0, 1)
        if pickside == 0:
            UFO.vx = -0.25
            xpos = lm.NDCToSC_x(1, wwidth)
        if pickside == 1:
            UFO.vx = 0.25
            xpos = 0
        super(UFO, self).__init__(renderer, int(xpos), int(ypos), int(enemywidth), int(enemyheight),
                                                                 "enemy5.png", None, False)
        UFO.points = 100
        UFO.width = self.width
        if pickside == 1:
            self.x = -self.width
        path = os.path.join(os.path.dirname(__file__), 'resources/sounds', 'ufo_lowpitch.wav')
        UFO.sound = sdlmixer.Mix_LoadWAV(path)
        sdlmixer.Mix_PlayChannel(-1, self.sound, 0)

    def remove(self):
        EnemyController.UFOactive = False
        super(UFO, self).delete()

    def shoot(self):
        pass

    def update(self, time):
        self.x += lm.NDCToSC_x(UFO.vx * time, Enemy.maxwidth)
        if UFO.vx < 0 and self.x < -UFO.width:
            self.delete()
            EnemyController.enemies.remove(self)
            EnemyController.UFOactive = False
        elif UFO.vx > 0 and self.x > Enemy.maxwidth:
            self.delete()
            EnemyController.enemies.remove(self)
            EnemyController.UFOactive = False

class EnemyBullet(filledRect):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        bulletwidth, bulletheight = lm.NDCToSC(.01, .025, wwidth, wheight)
        super(EnemyBullet, self).__init__(renderer, int(bulletwidth), int(bulletheight))
        self.sprite.position = posx, posy
        EnemyBullet.height = bulletheight
        EnemyBullet.maxheight = wheight
        EnemyBullet.vy = .5

    def delete(self):
        super(EnemyBullet, self).delete()

    def update(self, time):
        self.sprite.y += lm.NDCToSC_y(self.vy * time, self.maxheight)

    def remove(self):
        # print "removing enemybullet"
        self.delete()

class Shield(spritedrawer.spriteMaker, Drawable):
    def __init__(self, renderer, posx, posy, wwidth, wheight):
        self.shieldwidth, self.shieldheight = lm.NDCToSC(.135, .08, wwidth, wheight)
        self.shieldposx, self.shieldposy = lm.NDCToSC(posx, posy, wwidth, wheight)
        Shield.health = 6
        self.renderer = renderer
        super(Shield, self).__init__(renderer, int(self.shieldposx), int(self.shieldposy), int(self.shieldwidth),
                                     int(self.shieldheight), "shield6.png", None, False)

    def hit(self):
        self.health -= 1
        name = "shield" + str(self.health) + ".png"
        super(Shield, self).__init__(self.renderer, int(self.shieldposx), int(self.shieldposy), int(self.shieldwidth), int(self.shieldheight),
                                     name, None, False)

    def remove(self):
        self.delete()