import sdl2.ext
import drawable as draw
from optparse import OptionParser
import collision
import timeit as ti
import time
import ui

gameIsActive = True
width = 0
height = 0
renderer = None

# -------------------------------------------------------------------------------
def clear(renderer):
    print "clearing"
    renderer.color = sdl2.ext.Color(0, 0, 0, 255)
    renderer.clear()
    renderer.present()


# -------------------------------------------------------------------------------
def gameover(renderer, player):
    global gameIsActive

    # Empty the current drawlist
    draw.Drawable.clearAll()
    # Add ONLY the gameover text
    # TODO: should also display final score!
    gameover = ui.textMaker(renderer, "GAME OVER", width / 5, (height / 2) - 50, 40,
                            fontname="8-BIT WONDER.TTF")
    text = "SCORE " + str(player.score)
    print type(text)
    score = ui.textMaker(renderer, text, width / 5, (height / 2), 30,
                            fontname="8-BIT WONDER.TTF")
    # Signal update function to end
    gameIsActive = False

# -------------------------------------------------------------------------------
def update(player, lives, score, bullets, enemycontrol, shields, time):
    # our main game loop

    global gameIsActive

    # read remote inputs
    # ...

    # read local inputs & events
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            return False
            break
        player.getInput(event)
    if gameIsActive:
        player.update(time)
        enemycontrol.update(time)
        if enemycontrol.checkWin(player):
            gameover(renderer)
        for enemy in enemycontrol.enemies:
            enemy.update(time)
        for ebullet in enemycontrol.bullets:
            ebullet.update(time)
            for shield in shields:
                hit = collision.checkCollision(ebullet, shield)
                if hit:
                    ebullet.remove()
                    enemycontrol.bullets.remove(ebullet)
                    shield.hit()
                    if shield.health <= 0:
                        shield.remove()
                        shields.remove(shield)
                    break
            hit = collision.checkCollision(ebullet, player)
            if hit:
                # print "enemy hit"
                enemycontrol.removebullet(ebullet)
                player.lostlife()
                lives.updateLives(player.lives)
                if player.lives <= 0:
                    gameover(renderer, player)
                break
        for bullet in bullets:
            bullet.update(time)
            for shield in shields:
                hit = collision.checkCollision(bullet, shield)
                if hit:
                    bullet.remove()
                    bullets.remove(bullet)
                    shield.hit()
                    if shield.health <= 0:
                        shield.remove()
                        shields.remove(shield)
                    break
            for enemy in enemycontrol.enemies:
                hit = collision.checkCollision(bullet, enemy)
                if hit:
                    player.score += enemy.points
                    score.updateScore(player.score)
                    enemy.remove()
                    enemycontrol.enemies.remove(enemy)
                    bullet.remove()
                    bullets.remove(bullet)
                    break
        if len(enemycontrol.enemies) < 1:
            enemycontrol.reset()

    # send local state to remotes

    return True


# -------------------------------------------------------------------------------
def render(renderer):
    # clear to black
    renderer.color = sdl2.ext.Color(0, 0, 0, 255)
    renderer.clear()

    # iterate the global draw list
    for di in draw.Drawable.drawList:
        di.render()

    # test.renderTexture(image, renderer, 0, 0)
    # present renderer results
    renderer.present()


# -------------------------------------------------------------------------------
def main():
    print "--begin game--"

    ###########################################################################
    # set up command line arguments using optparse library
    ###########################################################################
    usage = "usage: %prog [options] arg1 arg2"
    parser = OptionParser(usage, version="%prog 0.1")
    parser.add_option("-x", "--width", type="int", dest="width", default=600,
                      help="set window width [600]")
    parser.add_option("-y", "--height", type="int", dest="height", default=800,
                      help="set window height [800]")
    parser.add_option("-l", "--limitframe", type="float", dest="limitFrameRate",
                      help="limit framerate to specified value [NO DEFAULT]")
    parser.add_option("-d", "--debug", action="store_true", dest="debug",
                      default=False, help="enable debug print output")
    (options, args) = parser.parse_args()

    # extract window size variables
    global width
    global height
    width = options.width
    height = options.height
    print "--window size(%d, %d)--" % (width, height)

    # extract limited framerate settings
    limitFrame = False
    frameRateLimit = 1.0
    if (options.limitFrameRate):
        limitFrame = True
        frameRateLimit = options.limitFrameRate
        print "--frame rate limit(%d)--" % (frameRateLimit)
    ###########################################################################

    ###########################################################################
    # SDL setup
    ###########################################################################
    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    sdl2.ext.init()

    # create window
    window = sdl2.ext.Window("Space Invaders", size=(width, height))
    window.show()

    # create a sprite renderer starting with a base sdl2ext renderer
    global renderer
    renderer = sdl2.ext.Renderer(window)

    ###########################################################################

    ###########################################################################
    # Our game object setup
    ###########################################################################
    # create player object
    player1 = draw.Player(renderer, width, height, 0.25, 1.0, 66, 28.8)
    bullets = player1.bullets

    lives = ui.renderLives(renderer, player1.lives, 5, 5)
    score = ui.renderScore(renderer, player1.score, width - (width / 3) - 25, 5)

    enemycontrol = draw.EnemyController(renderer, width, height)

    # creates shields
    shields = list()
    x = .1
    while x <= .75:
        shield = draw.Shield(renderer, x, .8, width, height)
        shields.append(shield)
        x += .30

    ###########################################################################

    running = True
    minFrameSecs = 1.0 / frameRateLimit
    lastDelta = 0.0
    quitLimit = 2.0
    quitTimer = 0.0
    if options.debug:
        fpsCounter = ui.textMaker(renderer, "FPS: 0", width - 55, height - 14, 12,
                                  fontname="Arial.ttf")

    while running:
        start = ti.default_timer()

        #######################################################################
        # add all per-frame work here
        if not gameIsActive:
            quitTimer += lastDelta
            if (quitTimer >= quitLimit):
                break
        else:
            running = update(player1, lives, score, bullets, enemycontrol, shields, lastDelta)

        # Always render
        render(renderer)
        #######################################################################

        stop = ti.default_timer()
        lastDelta = stop - start
        # Sleep if frame rate is higher than desired
        if (limitFrame and (lastDelta < minFrameSecs)):
            time.sleep(minFrameSecs - lastDelta)
            stop = ti.default_timer()
            lastDelta = stop - start
        if options.debug:
            fpsCounter.setText("FPS: " + str(int(1.0 / lastDelta)))

    # cleanup
    sdl2.ext.quit()

    print "--end game--"


# -------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------------------------------------
