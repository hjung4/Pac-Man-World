import sys, random, copy, os, time, pygame
from tkinter import *
import tkinter.simpledialog
from pygame.locals import *

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_COLOR = (0,0,0)  # black
FONT_COLOR = (255,255,255)  # white
START_FONT_COLOR = (255,255,0)  # yellow

def main():
    global CLOCK, SCREEN, FONT, LARGEFONT, PACMAN, FRUIT, PLAYER_IMAGE, SCORE, LIVES, HIGH_SCORE_MIN, LINES

    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    LARGEFONT = pygame.font.Font("freesansbold.ttf", 30)
    FONT = pygame.font.Font("freesansbold.ttf", 18)
    
    pygame.display.set_caption("Pac-Man")
    pygame.display.set_icon(pygame.image.load("assets/pacmanR.png"))
    
    PACMAN = {"right": pygame.image.load("assets/pacmanR.png"),
              "left": pygame.image.load("assets/pacmanL.png"),
              "up": pygame.image.load("assets/pacmanU.png"),
              "down": pygame.image.load("assets/pacmanD.png"),
              "rightC": pygame.image.load("assets/pacmanR_C.png"),
              "leftC": pygame.image.load("assets/pacmanL_C.png"),
              "upC": pygame.image.load("assets/pacmanU_C.png"),
              "downC": pygame.image.load("assets/pacmanD_C.png")}
    FRUIT = {"cherry": pygame.image.load("assets/cherry.jpg"),
             "strawberry": pygame.image.load("assets/strawberry.jpg"),
             "orange": pygame.image.load("assets/orange.jpg"),
             "apple": pygame.image.load("assets/apple.jpg"),
             "melon": pygame.image.load("assets/melon.jpg"),
             "boss": pygame.image.load("assets/galaxian_boss.jpg"),
             "bell": pygame.image.load("assets/bell.jpg"),
             "key": pygame.image.load("assets/key.jpg")}
    PLAYER_IMAGE = PACMAN["right"]
    SCORE = 0
    LIVES = 3

    # Variables used later to determine high score
    LINES = 0
    HIGH_SCORE_MIN = sys.maxsize

    # calculates HIGH_SCORE_MIN (the lowest score on the high score board, used later to calculate whether the player made high score)
    countNum = 0
    with open("data/save_file_P.txt", "r") as f:
        for line in f:
            LINES += 1
            for s in line.split("     "):
                countNum += 1
                if (countNum-2)%3 == 0 and countNum >= 2:
                    if int(s) < HIGH_SCORE_MIN:
                        HIGH_SCORE_MIN = int(s)
                        
    pygame.mixer.music.load("sounds/beginning.ogg")  # music during start screen
    pygame.mixer.music.play(-1, 0.0)  # beginning music is played
    
    start()  # Start Screen interface

    pygame.mixer.music.stop()

    levels = read("data/levels_P.txt")  # read the level from the text file
                    
    currentLevelIndex = 0  # sets the starting level to Level 1 (Ex. If you set currentLevelIndex to 5, the game will start at level 4)

    while True:  # main loop
        result = runLevel(levels, currentLevelIndex)  # runs the level

        # 1. If finished level (not the last level)
        if result == 1:
            currentLevelIndex += 1
            LIVES += 1  # bonus life is given to Pac-Man

        # 2. If the player lost all 3 lives
        elif result == 2:
            currentLevelIndex = 0  # start over with level 1
            SCORE -= 10000  # deduct the score by 10,000
            if SCORE < 0:  # if the score is negative, make the score 0
                SCORE = 0
            LIVES = 3  # renew number of lives to 3

        # 3. If completed the game (finished the last level)
        elif result == 3:
            # terminate program
            pygame.quit()
            sys.exit()

def runLevel(levels, num):
    """
    Runs the level.

    This function should be called to run the next level.

    @type  levels: dictionary
    @param levels: dictionary that contains info of the level's maze (created from read() function)
    @type  num   : current level index
    @param num   : current level index

    @rtype  1: Integer
    @rparam 1: Finished level (not the last level)
    @rtype  2: Integer
    @rparam 2: Lost all 3 lives (Game Over)
    @rtype  3: Integer
    @rparam 3: Finished last level (finished all levels of the game)

    ------------------------------------------------------------------------------
    The following code are included in the runLevel() function:
    - Code for Pac-Man's movement and collision event handling
    - AI Code for the enemies
    -----------------------------------------------------------------------------
    """
    global PLAYER_IMAGE, SCORE, LIVES, HIGH_SCORE_MIN, LINES

    # Music files
    pygame.mixer.music.load("sounds/chomp.ogg")
    eatFruit = pygame.mixer.Sound("sounds/eatFruit.ogg")
    eatGhost = pygame.mixer.Sound("sounds/eatGhost.ogg")
    extraLife = pygame.mixer.Sound("sounds/extraLife.ogg")
    death = pygame.mixer.Sound("sounds/death.ogg")
    finishedGame = pygame.mixer.Sound("sounds/finishedGame.ogg")
    
    levelDict = levels[num]
    mazeArray = levelDict["mazeArray"]
    gameDict  = copy.deepcopy(levelDict["start"])
    
    mazeRedraw    = True   # screen update boolean value
    scoreDraw     = True   # score update boolean value
    directionP    = ""     # direction of Pac-Man
    start_time    = 0      # integer value used for timed element in game
    fruitOnScreen = 0      # integer value for number of fruits on the screen currently
    quickChange   = False  # boolean value used for Pac-Man animation
    inkyChange    = False  # boolean value for Inky's fickle behavior
    inkyStartTime = 0      # integer value used for timed element for Inky
    X_SIZE        = 35     # size of level tile (x)
    Y_SIZE        = 35     # size of level tile (y)

    # Boolean values used when game is completed
    timeDraw = False
    askName  = False

    # Mouse coordinate values
    mousex = 0
    mousey = 0
    
    # Boolean values used when in reverse mode
    reverseB = reverseP = reverseC = reverseI = False
    blinkB   = blinkP   = blinkC   = blinkI   = False

    # Variables used for release of enemies from enemy box at start of new level
    releaseB = releaseP = releaseI = releaseC = time.time()
    BRelease = True
    PRelease = CRelease = IRelease = False
    Bmove    = Pmove    = Imove    = Cmove = False
    Bexit    = Pexit    = Iexit    = Cexit = False

    # Variables used when enemies start in enemy box
    firstB      = firstP      = firstC      = firstI      = True
    firstBcount = firstPcount = firstCcount = firstIcount = 0

    # Variables used when enemy collided with Pac-Man (enemy pauses for 0.5 seconds before moving again)
    pauseB  = pauseP  = pauseC  = pauseI  = False
    pauseBX = pausePX = pauseCX = pauseIX = 0
    pauseBY = pausePY = pauseCY = pauseIY = 0
    
    # Coordinates for start teleporter and end teleporter (used for limits of the maze map and for teleporting)
    x1, y1 = gameDict["start"]
    x2, y2 = gameDict["end"]
    
    mazeWidth = len(mazeArray) * 50
    mazeHeight = (len(mazeArray[0]) - 1) * 40 + 85

    # Fix size based on level
    if num == 3:  # Level 4 (index num 3) needs smaller tile size to fit on screen
        X_SIZE = 25
        Y_SIZE = 35
    else:
        X_SIZE = 35
        Y_SIZE = 35
    
    SCREEN.fill(SCREEN_COLOR)
    originalScreen = drawOriginal(mazeArray, gameDict, num, levels, X_SIZE, Y_SIZE)
    originalRect = originalScreen.get_rect()
    originalRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    SCREEN.blit(originalScreen, originalRect)  # basic surface is drawn onto the screen
    
    levelIsFinished = False  # boolean value that indicates whether level is finished or not
    
    pygame.mixer.music.play(-1, 0.0)  # background music is played
    
    while True:
        keyPressed = False
        mousePressed = False
        
        Bcollide = Pcollide = Ccollide = Icollide = False  # boolean values used when the enemies collide with other objects
        fruit = 0  # integer value that indicates which fruit should next be shown on screen (1: cherry, 2: strawberry, 3: orange, ...
        playerx, playery = gameDict["player"]  # coordinates of Pac-Man
        pacdots = gameDict["pacdots"]  # array of coordinates of pac-dots
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                keyPressed = True
                    
                if event.key == K_LEFT:
                    if (directionP == "up" and mazeArray[playerx-1][playery] == "#") or (directionP == "down" and mazeArray[playerx-1][playery] == "#"):
                        pass
                    else:
                        PLAYER_IMAGE = PACMAN["left"]
                        directionP = "left"
                elif event.key == K_RIGHT:
                    if (directionP == "up" and mazeArray[playerx+1][playery] == "#") or (directionP == "down" and mazeArray[playerx+1][playery] == "#"):
                        pass
                    else:
                        PLAYER_IMAGE = PACMAN["right"]
                        directionP = "right"
                elif event.key == K_UP:
                    if (directionP == "left" and mazeArray[playerx][playery-1] == "#") or (directionP == "right" and mazeArray[playerx][playery-1] == "#"):
                        pass
                    else:
                        PLAYER_IMAGE = PACMAN["up"]
                        directionP = "up"
                elif event.key == K_DOWN:
                    if (directionP == "left" and mazeArray[playerx][playery+1] == "#") or (directionP == "right" and mazeArray[playerx][playery+1] == "#"):
                        pass
                    else:
                        PLAYER_IMAGE = PACMAN["down"]
                        directionP = "down"
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mousePressed = True

        # HOME button
        if mousex >= 1120 and mousex <= 1200 and mousey >= 670 and mousey <= 700:
            if mousePressed:
                main()  # go back to the start screen

        # Pac-Man animation
        if quickChange == False:
            if directionP == "right":
                PLAYER_IMAGE = PACMAN["rightC"]
            elif directionP == "left":
                PLAYER_IMAGE = PACMAN["leftC"]
            elif directionP == "up":
                PLAYER_IMAGE = PACMAN["upC"]
            elif directionP == "down":
                PLAYER_IMAGE = PACMAN["downC"]
            mazeRedraw = True
            quickChange = True
        else:
            if directionP == "right":
                PLAYER_IMAGE = PACMAN["right"]
            elif directionP == "left":
                PLAYER_IMAGE = PACMAN["left"]
            elif directionP == "up":
                PLAYER_IMAGE = PACMAN["up"]
            elif directionP == "down":
                PLAYER_IMAGE = PACMAN["down"]
            mazeRedraw = True
            quickChange = False

        # Releasing enemies at start of the game
        if BRelease == False:
            if time.time() - releaseB >= 2:
                BRelease = True
        if time.time() - releaseI >= 4:
            IRelease = True
        if time.time() - releaseP >= 6:
            PRelease = True
        if time.time() - releaseC >= 8:
            CRelease = True

        # Reverse Mode (start blinking after 5 seconds, release ghosts after 10 seconds)
        if reverseB == True:
            if time.time() - start_time >= 5:
                blinkB = True
            if time.time() - start_time >= 10:
                reverseB = False
                blinkB = False
        if reverseP == True:
            if time.time() - start_time >= 5:
                blinkP = True
            if time.time() - start_time >= 10:
                reverseP = False
                blinkP = False
        if reverseC == True:
            if time.time() - start_time >= 5:
                blinkC = True
            if time.time() - start_time >= 10:
                reverseC = False
                blinkC = False
        if reverseI == True:
            if time.time() - start_time >= 5:
                blinkI = True
            if time.time() - start_time >= 10:
                reverseI = False
                blinkI = False

        # Enemies should pause for 0.5 seconds after colliding with Pac-Man to allow Pac-Man to escape
        if pauseB == True:
            if time.time() - start_time >= 0.5:
                gameDict["blinky"] = (pauseBX, pauseBY)
                mazeRedraw = True
                pauseB = False
        if pauseP == True:
            if time.time() - start_time >= 0.5:
                gameDict["pinky"] = (pausePX, pausePY)
                mazeRedraw = True
                pauseP = False
        if pauseC == True:
            if time.time() - start_time >= 0.5:
                gameDict["clyde"] = (pauseCX, pauseCY)
                mazeRedraw = True
                pauseC = False
        if pauseI == True:
            if time.time() - start_time >= 0.5:
                gameDict["inky"] = (pauseIX, pauseIY)
                mazeRedraw = True
                pauseI = False

        # Random fruit generator
        if fruitOnScreen < 7:
            n = random.randint(1,36)
            if n == 1:
                fruit = 8
            elif n == 2 or n == 3:
                fruit = 7
            elif n == 4 or n == 5 or n == 6:
                fruit = 6
            elif n == 7 or n == 8 or n == 9 or n == 10:
                fruit = 5
            elif n == 11 or n == 12 or n == 13 or n == 14 or n == 15:
                fruit = 4
            elif n == 16 or n == 17 or n == 18 or n == 19 or n == 20 or n == 21:
                fruit = 3
            elif n == 22 or n == 23 or n == 24 or n == 25 or n == 26 or n == 27 or n == 28:
                fruit = 2
            else:
                fruit = 1
            mazeRedraw = True
            fruitOnScreen += 1

        # Inky's fickle behavior
        if time.time() - inkyStartTime >= 15:
            if inkyChange == False:
                inkyChange = True
            else:
                inkyChange = False
            inkyStartTime = time.time()
        
        # Movement of player and enemies
        if not levelIsFinished:
            # 1. Pac-Man movement
            keys_pressed = pygame.key.get_pressed()
            if keys_pressed[K_UP]:
                if (directionP == "left" and mazeArray[playerx][playery-1] == "#") or (directionP == "right" and mazeArray[playerx][playery-1] == "#"):
                    pass
                else:
                    PLAYER_IMAGE = PACMAN["up"]
                    directionP = "up"
            elif keys_pressed[K_RIGHT]:
                if (directionP == "up" and mazeArray[playerx+1][playery] == "#") or (directionP == "down" and mazeArray[playerx+1][playery] == "#"):
                    pass
                else:
                    PLAYER_IMAGE = PACMAN["right"]
                    directionP = "right"
            elif keys_pressed[K_DOWN]:
                if (directionP == "left" and mazeArray[playerx][playery+1] == "#") or (directionP == "right" and mazeArray[playerx][playery+1] == "#"):
                    pass
                else:
                    PLAYER_IMAGE = PACMAN["down"]
                    directionP = "down"
            elif keys_pressed[K_LEFT]:
                if (directionP == "up" and mazeArray[playerx-1][playery] == "#") or (directionP == "down" and mazeArray[playerx-1][playery] == "#"):
                    pass
                else:
                    PLAYER_IMAGE = PACMAN["left"]
                    directionP = "left"

            addX = addY = 0
            
            if directionP == "up":
                addY = -1
            elif directionP == "right":
                addX = 1
            elif directionP == "down":
                addY = 1
            elif directionP == "left":
                addX = -1
                
            if playerx + addX < len(mazeArray):
                if mazeArray[playerx + addX][playery + addY] not in ("#") and mazeArray[playerx + addX][playery + addY] not in ("-"):  # if player did not collide with wall
                    if (playerx + addX, playery + addY) in pacdots:  # if player made contact with pac-dot
                        gameDict["pacdotCounter"] += 1
                        gameDict["pacdots"].remove((playerx + addX, playery + addY))
                        gameDict["speedCheck"] += 1
                    if (playerx + addX, playery + addY) == gameDict["blinky"]:  # if player made contact with Blinky
                        if reverseB == True:
                            SCORE += 3000
                            scoreDraw = True
                            gameDict["blinky"] = gameDict["startB"]
                            eatGhost.play(0)
                            firstB = True
                            reverseB = False
                            Bexit = False
                            BRelease = False
                            releaseB = time.time()
                    if (playerx + addX, playery + addY) == gameDict["pinky"]:  # if player made contact with Pinky
                        if reverseP == True:
                            SCORE += 3000
                            scoreDraw = True
                            gameDict["pinky"] = gameDict["startP"]
                            eatGhost.play(0)
                            firstP = True
                            reverseP = False
                            Pexit = False
                            PRelease = False
                            releaseP = time.time()
                    if (playerx + addX, playery + addY) == gameDict["inky"]:  # if player made contact with Inky
                        if reverseI == True:
                            SCORE += 3000
                            scoreDraw = True
                            gameDict["inky"] = gameDict["startI"]
                            eatGhost.play(0)
                            firstI = True
                            reverseI = False
                            Iexit = False
                            IRelease = False
                            releaseI = time.time()
                    if (playerx + addX, playery + addY) == gameDict["clyde"]:  # if player made contact with Clyde
                        if reverseC == True:
                            SCORE += 3000
                            scoreDraw = True
                            gameDict["clyde"] = gameDict["startC"]
                            eatGhost.play(0)
                            firstC = True
                            reverseC = False
                            Cexit = False
                            CRelease = False
                            releaseC = time.time()
                    if (playerx + addX, playery + addY) in gameDict["powerPellet"]:  # if player made contact with power-pellet
                        if Bexit == True:
                            reverseB = True
                            blinkB = False
                        if Pexit == True:
                            reverseP = True
                            blinkP = False
                        if Iexit == True:
                            reverseI = True
                            blinkI = False
                        if Cexit == True:
                            reverseC = True
                            blinkC = False
                        start_time = time.time()
                        gameDict["powerPellet"].remove((playerx + addX, playery + addY))
                    if (playerx + addX, playery + addY) in gameDict["cherry"]:   # if player made contact with cherry
                        SCORE += 100
                        scoreDraw = True
                        gameDict["cherry"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["strawberry"]:  # if player made contact with strawberry
                        SCORE += 300
                        scoreDraw = True
                        gameDict["strawberry"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["orange"]:  # if player made contact with orange
                        SCORE += 500
                        scoreDraw = True
                        gameDict["orange"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["apple"]:  # if player made contact with apple
                        SCORE += 700
                        scoreDraw = True
                        gameDict["apple"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["melon"]:  # if player made contact with melon
                        SCORE += 1000
                        scoreDraw = True
                        gameDict["melon"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["boss"]:  # if player made contact with galaxian boss
                        SCORE += 2000
                        scoreDraw = True
                        gameDict["boss"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["bell"]:  # if player made contact with bell
                        SCORE += 3000
                        scoreDraw = True
                        gameDict["bell"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    if (playerx + addX, playery + addY) in gameDict["key"]:  # if player made contact with key
                        SCORE += 5000
                        scoreDraw = True
                        gameDict["key"].remove((playerx + addX, playery + addY))
                        eatFruit.play(0)
                        fruitOnScreen -= 1
                    gameDict["player"] = (playerx + addX, playery + addY)  # reset Pac-Man's coordinates
                    mazeRedraw = True  # update screen

            if gameDict["pacdotCounter"] == gameDict["total_pacdots"]:  # level is finished if all pac-dots are eaten
                levelIsFinished = True
                keyPressed = False

            # 2. Blinky AI: chases Pac-Man
            if gameDict["blinky"] != (None, None):  # if Blinky exists
                enemyxB, enemyyB = gameDict["blinky"]
                addXB = addYB = 0
                if enemyxB >= x1 + 1 and enemyxB <= x2 - 1:
                    if reverseB == True:  # if reverse mode
                        choice = random.randint(1,3)
                        if choice == 1:
                            direction = 0
                        else:
                            direction = enemyWorstMove(mazeArray, gameDict, 1)
                    elif firstB == True:  # if starting in enemy box (needs to navigate out of enemy box)
                        Bexit = True
                        if firstBcount == 0:
                            direction = 1
                        elif firstBcount == 1:
                            direction = 1
                        elif firstBcount == 2:
                            direction = 1
                            firstBcount = 0
                            firstB = False
                    else:  # normal mode
                        direction = enemyBestMove(mazeArray, gameDict, 1)
                if direction == 1: #left
                    addXB = -1
                elif direction == 2: #right
                    addXB = 1
                elif direction == 3: #up
                    addYB = -1
                elif direction == 4: #down
                    addYB = 1
                    
                if enemyxB + addXB < len(mazeArray):
                    if mazeArray[enemyxB + addXB][enemyyB +addYB] not in ("#") and mazeArray[enemyxB + addXB][enemyyB +addYB] not in ("T") and mazeArray[enemyxB + addXB][enemyyB +addYB] not in ("t") and BRelease == True:  # if enemy did not collide with wall
                        if Bexit == True:
                            if mazeArray[enemyxB + addXB][enemyyB + addYB] not in ("-"):
                                Bmove = True
                        else:
                            Bmove = True
                        if Bmove == True:
                            if (enemyxB + addXB, enemyyB + addYB) in pacdots:
                                BcollideX = enemyxB + addXB
                                BcollideY = enemyyB + addYB
                                Bcollide = True
                                gameDict["pacdots"].remove((enemyxB + addXB, enemyyB + addYB))
                            if (enemyxB + addXB, enemyyB + addYB) == gameDict["player"] and reverseB == False:
                                if LIVES > 0:
                                    LIVES -= 1
                                pauseBX = enemyxB + addXB
                                pauseBY = enemyyB + addYB
                                gameDict["blinky"] = (None, None)
                                death.play(0)
                                start_time = time.time()
                                pauseB = True
                            if pauseB == False:
                                gameDict["blinky"] = (enemyxB + addXB, enemyyB + addYB)
                            mazeRedraw = True
                            Bmove = False
                        if firstB == True:
                            firstBcount += 1

                # Teleport Blinky
                if enemyxB + addXB <= x1:
                    gameDict["blinky"] = (x2, y2)
                    mazeRedraw = True
                elif enemyxB + addXB >= x2:
                    gameDict["blinky"] = (x1, y1)
                    mazeRedraw = True

            # 3. Pinky AI: aims for a position in front of Pac-Man's mouth
            if gameDict["pinky"] != (None, None):  # if Pinky exists
                enemyxP, enemyyP = gameDict["pinky"]
                addXP = addYP = 0
                if enemyxP >= x1 + 1 and enemyxP <= x2 - 1:
                    if reverseP == True:  # if reverse mode
                        choice = random.randint(1,3)
                        if choice == 1:
                            direction = 0
                        else:
                            direction = enemyWorstMove(mazeArray, gameDict, 2)
                    elif firstP == True:  # if starting in enemy box (needs to navigate out of enemy box)
                        if firstPcount == 0:
                            direction = 2
                        elif firstPcount == 1:
                            direction = 3
                        elif firstPcount == 2:
                            direction = 3
                            Pexit = True
                        elif firstPcount == 3:
                            direction = 1
                        elif firstPcount == 4:
                            direction = 1
                        elif firstPcount == 5:
                            direction = 1
                            firstPcount = 0
                            firstP = False
                    else:  # normal mode
                        choice = random.randint(1,4)
                        if choice == 1:  # used to make Pinky's speed slower than Pac-Man
                            direction = 0
                        else:
                            direction = enemyFrontMove(mazeArray, gameDict, directionP)
                if direction == 1: #left
                    addXP = -1
                elif direction == 2: #right
                    addXP = 1
                elif direction == 3: #up
                    addYP = -1
                elif direction == 4: #down
                    addYP = 1

                if enemyxP + addXP < len(mazeArray):
                    if mazeArray[enemyxP + addXP][enemyyP +addYP] not in ("#") and mazeArray[enemyxP + addXP][enemyyP +addYP] not in ("T") and mazeArray[enemyxP + addXP][enemyyP +addYP] not in ("t") and PRelease == True:  # if enemy did not collide with wall
                        if Pexit == True:
                            if mazeArray[enemyxP + addXP][enemyyP + addYP] not in ("-"):
                                Pmove = True
                        else:
                            Pmove = True
                        if Pmove == True:
                            if (enemyxP + addXP, enemyyP + addYP) in pacdots:
                                PcollideX = enemyxP + addXP
                                PcollideY = enemyyP + addYP
                                Pcollide = True
                                gameDict["pacdots"].remove((enemyxP + addXP, enemyyP + addYP))
                            if (enemyxP + addXP, enemyyP + addYP) == gameDict["player"] and reverseP == False:
                                if LIVES > 0:
                                    LIVES -= 1
                                pausePX = enemyxP + addXP
                                pausePY = enemyyP + addYP
                                gameDict["pinky"] = (None, None)
                                death.play(0)
                                start_time = time.time()
                                pauseP = True
                            if pauseP == False:
                                gameDict["pinky"] = (enemyxP + addXP, enemyyP + addYP)
                            mazeRedraw = True
                            Pmove = False
                        if firstP == True:
                            firstPcount += 1

                # Teleport Pinky
                if enemyxP + addXP <= x1:
                    gameDict["pinky"] = (x2, y2)
                    mazeRedraw = True
                elif enemyxP + addXP >= x2:
                    gameDict["pinky"] = (x1, y1)
                    mazeRedraw = True

            # 4. Inky AI: "fickle" (sometimes heads towards Pac-Man, and other times away)
            if gameDict["inky"] != (None, None):  # if Inky exists
                enemyxI, enemyyI = gameDict["inky"]
                addXI = addYI = 0
                if enemyxI >= x1 + 1 and enemyxI <= x2 - 1:
                    if reverseI == True:  # if reverse mode
                        choice = random.randint(1,3)
                        if choice == 1:
                            direction = 0
                        else:
                            direction = enemyWorstMove(mazeArray, gameDict, 3)
                    elif firstI == True:  # if starting in enemy box (needs to navigate out of enemy box)
                        if firstIcount == 0:
                            direction = 1
                        elif firstIcount == 1:
                            direction = 3
                        elif firstIcount == 2:
                            direction = 3
                            Iexit = True
                        elif firstIcount == 3:
                            direction = 1
                        elif firstIcount == 4:
                            direction = 1
                        elif firstIcount == 5:
                            direction = 1
                            firstIcount = 0
                            firstI = False
                    else:  # normal mode
                        if inkyChange == False:
                            direction = enemyWorstMove(mazeArray, gameDict, 3)
                        else:
                            direction = enemyBestMove(mazeArray, gameDict, 2)
                if direction == 1: #left
                    addXI = -1
                elif direction == 2: #right
                    addXI = 1
                elif direction == 3: #up
                    addYI = -1
                elif direction == 4: #down
                    addYI = 1

                if enemyxI + addXI < len(mazeArray):
                    if mazeArray[enemyxI + addXI][enemyyI +addYI] not in ("#") and mazeArray[enemyxI + addXI][enemyyI +addYI] not in ("T") and mazeArray[enemyxI + addXI][enemyyI +addYI] not in ("t") and IRelease == True:
                        if Iexit == True:
                            if mazeArray[enemyxI + addXI][enemyyI + addYI] not in ("-"):
                                Imove = True
                        else:
                            Imove = True
                        if Imove == True:
                            if (enemyxI + addXI, enemyyI + addYI) in pacdots:
                                IcollideX = enemyxI + addXI
                                IcollideY = enemyyI + addYI
                                Icollide = True
                                gameDict["pacdots"].remove((enemyxI + addXI, enemyyI + addYI))
                            if (enemyxI + addXI, enemyyI + addYI) == gameDict["player"] and reverseI == False:
                                if LIVES > 0:
                                    LIVES -= 1
                                pauseIX = enemyxI + addXI
                                pauseIY = enemyyI + addYI
                                gameDict["inky"] = (None, None)
                                death.play(0)
                                start_time = time.time()
                                pauseI = True
                            if pauseI == False:
                                gameDict["inky"] = (enemyxI + addXI, enemyyI + addYI)
                            mazeRedraw = True
                            Imove = False
                        if firstI == True:
                            firstIcount += 1

                # Teleport Inky
                if enemyxI + addXI <= x1:
                    gameDict["inky"] = (x2, y2)
                    mazeRedraw = True
                elif enemyxI + addXI >= x2:
                    gameDict["inky"] = (x1, y1)
                    mazeRedraw = True
            
            # 5. Clyde AI: random
            if gameDict["clyde"] != (None, None):  # if Clyde exists
                enemyxC, enemyyC = gameDict["clyde"]
                addXC = addYC = 0
                if enemyxC >= x1 + 1 and enemyxC <= x2 - 1:
                    if firstC == True:  # if starting in enemy box (needs to navigate out of enemy box)
                        if firstCcount == 0:
                            direction = 3
                        elif firstCcount == 1:
                            direction = 3
                            Cexit = True
                        elif firstCcount == 2:
                            direction = 1
                        elif firstCcount == 3:
                            direction = 1
                        elif firstCcount == 4:
                            direction = 1
                            firstCcount = 0
                            firstC = False
                    else:  # normal mode or reverse mode
                        direction = random.randint(1,4)
                if direction == 1: #left
                    addXC = -1
                elif direction == 2: #right
                    addXC = 1
                elif direction == 3: #up
                    addYC = -1
                elif direction == 4: #down
                    addYC = 1

                if enemyxC + addXC < len(mazeArray):
                    if mazeArray[enemyxC + addXC][enemyyC +addYC] not in ("#") and mazeArray[enemyxC + addXC][enemyyC +addYC] not in ("T") and mazeArray[enemyxC + addXC][enemyyC + addYC] not in ("t") and CRelease == True:  # if enemy did not collide with wall
                        if Cexit == True:
                            if mazeArray[enemyxC + addXC][enemyyC + addYC] not in ("-"):
                                Cmove = True
                        else:
                            Cmove = True
                        if Cmove == True:
                            if (enemyxC + addXC, enemyyC + addYC) in pacdots:
                                CcollideX = enemyxC + addXC
                                CcollideY = enemyyC + addYC
                                Ccollide = True
                                gameDict["pacdots"].remove((enemyxC + addXC, enemyyC + addYC))
                            if (enemyxC + addXC, enemyyC + addYC) == gameDict["player"] and reverseC == False:
                                if LIVES > 0:
                                    LIVES -= 1
                                pauseCX = enemyxC + addXC
                                pauseCY = enemyyC + addYC
                                gameDict["clyde"] = (None, None)
                                death.play(0)
                                start_time = time.time()
                                pauseC = True
                            if pauseC == False:
                                gameDict["clyde"] = (enemyxC + addXC, enemyyC + addYC)
                            mazeRedraw = True
                            Cmove = False
                        if firstC == True:
                            firstCcount += 1

                # Teleport Clyde
                if enemyxC + addXC <= x1:
                    gameDict["clyde"] = (x2, y2)
                    mazeRedraw = True
                elif enemyxC + addXC >= x2:
                    gameDict["clyde"] = (x1, y1)
                    mazeRedraw = True

        # Teleport player
        x, y = gameDict["player"]
        if x >= x2:
            gameDict["player"] = (x1, y1)
            mazeRedraw = True
        elif x <= x1:
            gameDict["player"] = (x2, y2)
            mazeRedraw = True

        # Update screen
        if mazeRedraw:  # if screen needs to be updated
            mazeScreen = draw(mazeArray, gameDict, originalScreen, reverseB, reverseP, reverseC, reverseI, blinkB, blinkP, blinkC, blinkI, fruit, X_SIZE, Y_SIZE)  # go to draw() function
            mazeRedraw = False

            # Redraw pac-dots that enemies had collided on, if necessary
            if Bcollide == True:
                gameDict["pacdots"].append((BcollideX, BcollideY))
            if Pcollide == True:
                gameDict["pacdots"].append((PcollideX, PcollideY))
            if Ccollide == True:
                gameDict["pacdots"].append((CcollideX, CcollideY))
            if Icollide == True:
                gameDict["pacdots"].append((IcollideX, IcollideY))

        # Draw the updated surface onto the screen
        mazeRect = mazeScreen.get_rect()
        mazeRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        SCREEN.blit(mazeScreen, mazeRect)

        # Draw the number of lives onto the screen (little Pac-Man images are used for the lives)
        x = 90
        for i in range(LIVES):
            imageRect = PACMAN["left"].get_rect()
            imageRect.center = (x, 680)
            SCREEN.blit(PACMAN["left"], imageRect)
            x += 30
        if LIVES <= 5:
            pygame.draw.rect(SCREEN, (0,0,0), (230,665,30,30), 0)
        if LIVES <= 4:
            pygame.draw.rect(SCREEN, (0,0,0), (200,665,30,30), 0)
        if LIVES <= 3:
            pygame.draw.rect(SCREEN, (0,0,0), (170,665,30,30), 0)
        if LIVES <= 2:
            pygame.draw.rect(SCREEN, (0,0,0), (140,665,30,30), 0)
        if LIVES <= 1:
            pygame.draw.rect(SCREEN, (0,0,0), (110,665,30,30), 0)
        if LIVES == 0:
            pygame.draw.rect(SCREEN, (0,0,0), (80,665,30,30), 0)

        # Update score
        if scoreDraw:  # if score needs to be updated
            pygame.draw.rect(SCREEN, (0,0,0), (SCREEN_WIDTH/2+25,10,150,30), 0)
            scoreScreen = LARGEFONT.render("%s" % (SCORE), 1, FONT_COLOR)
            scoreRect = scoreScreen.get_rect()
            scoreRect.bottomleft = (SCREEN_WIDTH/2+25, 40)
            SCREEN.blit(scoreScreen, scoreRect)
            scoreDraw = False

        # If level is finished (Note: the number of lives remaining must be greater than 0)
        if levelIsFinished and LIVES > 0:
            if num == len(levels) - 1:  # if last level
                pygame.mixer.music.stop()

                if timeDraw == False:
                    finishedGame.play(0)
                
                # Draw completed image onto screen
                SCREEN.fill(SCREEN_COLOR)
                completedRect = pygame.image.load("assets/completed.png").get_rect()
                completedRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                SCREEN.blit(pygame.image.load("assets/completed.png"), completedRect)

                # Draw final score text onto screen              
                scoreScreen = LARGEFONT.render("FINAL SCORE: %s" % (SCORE), 1, FONT_COLOR)
                scoreRect = scoreScreen.get_rect()
                scoreRect.bottomleft = (300, 625)
                SCREEN.blit(scoreScreen, scoreRect)

                # Draw time text onto screen
                if timeDraw == False:  # timeDraw: boolean value used to make sure the block of code is only run once
                    total_time = pygame.time.get_ticks()
                    minutes = 0
                    seconds = (int)(total_time/1000)
                    if (int)(seconds/60) > 0:
                        minutes = (int)(seconds/60)
                        seconds = (int)(seconds%60)
                        
                    timeScreen = LARGEFONT.render("TIME TAKEN: %s minutes, %s seconds" % (minutes, seconds), 1, FONT_COLOR)
                    timeRect = timeScreen.get_rect()
                    timeRect.bottomleft = (300, 660)
                    timeDraw = True
                SCREEN.blit(timeScreen, timeRect)

                # If the player made high score
                if SCORE > HIGH_SCORE_MIN or LINES < 5:
                    if askName == False:  # askName: boolean value used to make sure the block of code is only run once
                        # Input player's name
                        root = Tk()
                        name = tkinter.simpledialog.askstring("High Score!", "You have made high score! Enter your name:")
                        root.destroy()

                        # Read high scores from the text file
                        save_file = open("data/save_file_P.txt", "r")
                        lines = save_file.readlines()
                        save_file.close()

                        save_file = open("data/save_file_P.txt", "w")

                        # If the high score file has 5 scores, the lowest score needs to be deleted
                        if len(lines) >= 5:
                            # Sort the scores in the text file from highest to lowest and store the line number into lineNumList
                            scoreList = []  # array that stores scores from highest to lowest
                            lineNumList = []  # array that stores line numbers from highest score to lowest score
                            countNum = 0   # variable used to determine the 'score' part of the line
                            lineNum = 0   # variable used to determine the line number
                            for line in lines:
                                lineNum += 1
                                for s in line.split("     "):
                                    countNum += 1
                                    if (countNum-2)%3 == 0 and countNum >= 2:
                                        for i in range(lineNum):
                                            if i == lineNum - 1:
                                                scoreList.append(int(s))
                                                lineNumList.append(lineNum)
                                            elif len(scoreList) > 0 and int(s) > scoreList[i]:
                                                scoreList.insert(i,int(s))
                                                lineNumList.insert(i,lineNum)
                                                break

                            # Write all of the original lines back into the text file except for the line containing the lowest score
                            lineNum = 0
                            for line in lines:
                                lineNum += 1
                                if lineNum != lineNumList[len(lineNumList)-1]:
                                    save_file.write(line)

                            # Write the player's high score into the text file
                            if seconds < 10:
                                save_file.write("\n" + name + "     " + (str)(SCORE) + "     " + (str)(minutes) + ":0" + (str)(seconds))
                            else:
                                save_file.write("\n" + name + "     " + (str)(SCORE) + "     " + (str)(minutes) + ":" + (str)(seconds))

                        # If the high score file has less than 5 scores, the player's score can just be written into the file
                        else:
                            # Write all of the original lines back into the text file
                            for line in lines:
                                save_file.write(line)

                            # Write the player's high score into the text file
                            if seconds < 10:
                                save_file.write("\n" + name + "     " + (str)(SCORE) + "     " + (str)(minutes) + ":0" + (str)(seconds))
                            else:
                                save_file.write("\n" + name + "     " + (str)(SCORE) + "     " + (str)(minutes) + ":" + (str)(seconds))
                        
                        save_file.close()
                        askName = True
                
                if keyPressed:
                    return 3

            else:  # if not last level
                # Draw finished image onto screen
                finishedRect = pygame.image.load("assets/finished.png").get_rect()
                finishedRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                SCREEN.blit(pygame.image.load("assets/finished.png"), finishedRect)

                if keyPressed:
                    extraLife.play(0)
                    return 1

        # Game Over
        if LIVES == 0:  # if number of lives is 0
            pygame.mixer.music.stop()

            # Draw gameover image onto the screen
            gameOverRect = pygame.image.load("assets/gameover.png").get_rect()
            gameOverRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            SCREEN.blit(pygame.image.load("assets/gameover.png"), gameOverRect)
            mazeRedraw = True
            
            if keyPressed:
                return 2

        # Update
        pygame.display.update()
        CLOCK.tick(10)

def start():
    """
    Calls the start screen interface to be drawn onto the screen.

    This function should be called at the beginning of the program (Start Screen).

    When returned, the main() function continues where it stopped.

    ------------------------------------------------------------------------------
    There are 3 different screens:
    - Title Screen
    - Instructions Screen
    - High Scores Screen
    ------------------------------------------------------------------------------
    """

    # Boolean values that determine what the current screen is.
    instructions_Screen = False
    highScores_Screen   = False

    mousex = 0
    mousey = 0

    START_FONT = pygame.font.Font("freesansbold.ttf", 40)

    SCREEN.fill(SCREEN_COLOR)  # "Renews" screen (fills screen with black)
    
    # Title image
    title = pygame.image.load("assets/title.png").get_rect()
    title.top = 50
    title.centerx = SCREEN_WIDTH/2
    SCREEN.blit(pygame.image.load("assets/title.png"), title)

    # Draws rectangles for buttons
    pygame.draw.rect(SCREEN, (0,0,255), (630,410,110,60), 0)  # PLAY button
    pygame.draw.rect(SCREEN, (0,0,255), (630,480,320,60), 0)  # INSTRUCTIONS button
    pygame.draw.rect(SCREEN, (0,0,255), (630,550,400,60), 0)  # VIEW HIGH SCORES button
    pygame.draw.rect(SCREEN, (0,0,255), (630,620,230,60), 0)  # EXIT GAME button

    # Draws text for the PLAY button
    text1 = START_FONT.render("PLAY", 1, START_FONT_COLOR)
    textrect1 = text1.get_rect()
    textrect1.top = 420
    textrect1.centerx = 685
    SCREEN.blit(text1, textrect1)

    # Draws text for the INSTRUCTIONS button
    text2 = START_FONT.render("INSTRUCTIONS", 1, START_FONT_COLOR)
    textrect2 = text2.get_rect()
    textrect2.top = 490
    textrect2.centerx = 790
    SCREEN.blit(text2, textrect2)

    # Draws text for the VIEW HIGH SCORES button
    text3 = START_FONT.render("VIEW HIGH SCORES", 1, START_FONT_COLOR)
    textrect3 = text3.get_rect()
    textrect3.top = 560
    textrect3.centerx = 830
    SCREEN.blit(text3, textrect3)

    # Draws text for the EXIT GAME button
    text4 = START_FONT.render("EXIT GAME", 1, START_FONT_COLOR)
    textrect4 = text4.get_rect()
    textrect4.top = 630
    textrect4.centerx = 745
    SCREEN.blit(text4, textrect4)
    
    while True:  # main loop for start screen interface
        mousePressed = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mousePressed = True

        # 1. Title Screen
        if instructions_Screen == False and highScores_Screen == False:  # if current screen is Title Screen
            
            # PLAY button
            if mousex >= 630 and mousex <= 740 and mousey >= 410 and mousey <= 470:
                pygame.draw.rect(SCREEN, (0,155,155), (630, 410, 110, 60), 4)  # highlight around button
                if mousePressed:
                    return
            if mousex < 630 or mousex > 740 or mousey < 410 or mousey > 470: # erase the highlight
                pygame.draw.rect(SCREEN, (0,0,0), (630, 410, 110, 60), 4)

            # INSTRUCTIONS button
            if mousex >= 630 and mousex <= 950 and mousey >= 480 and mousey <= 540:
                pygame.draw.rect(SCREEN, (0,155,155), (630, 480, 320, 60), 4)  # highlight the button
                if mousePressed:  # go to instructions screen
                    mousePressed = False
                    instructions_Screen = True
            if mousex < 630 or mousex > 950 or mousey < 480 or mousey > 540:
                pygame.draw.rect(SCREEN, (0,0,0), (630, 480, 320, 60), 4)  # erase the highlight

            # VIEW HIGH SCORES button
            if mousex >= 630 and mousex <= 1030 and mousey >= 550 and mousey <= 610:
                pygame.draw.rect(SCREEN, (0,155,155), (630,550,400,60), 4)  # highlight the button
                if mousePressed:
                    mousePressed = False
                    highScores_Screen = True
            if mousex < 630 or mousex > 1030 or mousey < 550 or mousey > 610:
                pygame.draw.rect(SCREEN, (0,0,0), (630,550,400,60), 4)  # erase the highlight

            # EXIT GAME button
            if mousex >= 630 and mousex <= 860 and mousey >= 620 and mousey <= 680:
                pygame.draw.rect(SCREEN, (0,155,155), (630, 620, 230, 60), 4)  # highlight around button
                if mousePressed:  # terminate game
                    pygame.quit()
                    sys.exit()
            if mousex < 630 or mousex > 860 or mousey < 620 or mousey > 680:
                pygame.draw.rect(SCREEN, (0,0,0), (630, 620, 230, 60), 4)  # erase the highlight

        # 2. Instructions Screen
        if instructions_Screen == True:  # if current screen is Instructions Screen
            SCREEN.fill(SCREEN_COLOR)  # "renew" screen

            # Instructions text
            Text = ["Arrow keys to move, Esc to quit.",
                    "Get all the pac-dots to go to the next level.",
                    "There are 4 levels in the game. Pac-Man starts with 3 lives.",
                    "Every time you finish a level, Pac-Man gets an extra life.",
                    "Avoid ghosts. You will lose a life if you come into contact with a ghost.",
                    "Eat fruits. You will gain points:",
                    "= 100,    = 300,    = 500,    = 700,    = 1000,    = 2000,    = 3000,    = 5000",
                    "Power pellets allow you to eat ghosts for a limited time.",
                    "If you eat a ghost, you gain 3000 points.",
                    "If you lose all 3 lives, you will lose 10,000 points and start over."]

            # Draw fruits (Fruit images are included in instructions)
            cherry = FRUIT["cherry"].get_rect()
            cherry.top = 475
            cherry.centerx = 85
            SCREEN.blit(FRUIT["cherry"], cherry)
            strawberry = FRUIT["strawberry"].get_rect()
            strawberry.top = 475
            strawberry.centerx = 205
            SCREEN.blit(FRUIT["strawberry"], strawberry)
            orange = FRUIT["orange"].get_rect()
            orange.top = 475
            orange.centerx = 325
            SCREEN.blit(FRUIT["orange"], orange)
            apple = FRUIT["apple"].get_rect()
            apple.top = 475
            apple.centerx = 445
            SCREEN.blit(FRUIT["apple"], apple)
            melon = FRUIT["melon"].get_rect()
            melon.top = 475
            melon.centerx = 565
            SCREEN.blit(FRUIT["melon"], melon)
            boss = FRUIT["boss"].get_rect()
            boss.top = 475
            boss.centerx = 700
            SCREEN.blit(FRUIT["boss"], boss)
            bell = FRUIT["bell"].get_rect()
            bell.top = 475
            bell.centerx = 845
            SCREEN.blit(FRUIT["bell"], bell)
            key = FRUIT["key"].get_rect()
            key.top = 475
            key.centerx = 985
            SCREEN.blit(FRUIT["key"], key)

            # Draw the instructions text onto the screen
            top = 75
            for i in range(len(Text)):
                text = LARGEFONT.render(Text[i], 1, FONT_COLOR)
                instructions = text.get_rect()
                top += 30
                instructions.top = top
                instructions.centerx = SCREEN_WIDTH/2
                top += instructions.height
                SCREEN.blit(text, instructions)

            # Draw rectangle for BACK button
            pygame.draw.rect(SCREEN, (0,0,255), (630, 30, 120, 60), 0)

            # Draw text for BACK button
            text4 = START_FONT.render("BACK", 1, START_FONT_COLOR)
            textrect4 = text4.get_rect()
            textrect4.top = 40
            textrect4.centerx = 690
            SCREEN.blit(text4, textrect4)

            # BACK button
            if mousex >= 630 and mousex <= 750 and mousey >= 30 and mousey <= 90:
                pygame.draw.rect(SCREEN, (0,155,155), (630, 30, 120, 60), 4)  # highlight around the BACK button
                if mousePressed:
                    main()
            if mousex < 630 or mousex > 750 or mousey < 30 or mousey > 90:
                pygame.draw.rect(SCREEN, (0,0,0), (630, 30, 120, 60), 4)  # erase the highlight

        # 3. High Scores Screen
        if highScores_Screen == True:  # if current screen is High Scores Screen
            SCREEN.fill(SCREEN_COLOR)  # "renew" screen
            
            Text = ["HIGH SCORES (TOP 5):","(Format: [NAME] [SCORE] [TIME])", ""]
            ScoresText  = []
            
            scoreList   = []  # array that stores scores from highest to lowest
            lineNumList = []  # array that stores line numbers from highest score to lowest score
            countNum    = 0   # variable used to determine the 'score' part of the line
            lineNum     = 0   # variable used to determine the line number

            # Sort the scores in the text file from highest to lowest and store the line number into lineNumList
            with open("data/save_file_P.txt", "r") as f:
                for line in f:
                    lineNum += 1
                    for s in line.split("     "):
                        countNum += 1
                        if (countNum-2)%3 == 0 and countNum >= 2:
                            for i in range(lineNum):
                                if i == lineNum - 1:
                                    scoreList.append(int(s))
                                    lineNumList.append(lineNum)
                                elif len(scoreList) > 0 and int(s) > scoreList[i]:
                                    scoreList.insert(i,int(s))
                                    lineNumList.insert(i,lineNum)
                                    break

            # read the lines from the text file
            save_file = open("data/save_file_P.txt", "r")
            lines = save_file.readlines()
            save_file.close()

            # Add the lines in correct order to ScoresText
            for i in range(len(lineNumList)):
                line = lines[lineNumList[i]-1].rstrip("\r\n")
                ScoresText.append(str(i+1) + ". " + line)

            # Draw the High Scores intro text onto the screen
            top = 90
            for i in range(len(Text)):
                text = LARGEFONT.render(Text[i], 1, FONT_COLOR)
                scores = text.get_rect()
                top += 30
                scores.top = top
                scores.centerx = SCREEN_WIDTH/2
                top += scores.height
                SCREEN.blit(text, scores)

            # Draw the High Scores onto the screen
            for i in range(len(ScoresText)):
                text = LARGEFONT.render(ScoresText[i], 1, FONT_COLOR)
                scores = text.get_rect()
                top += 30
                scores.top = top
                scores.left = SCREEN_WIDTH/2-200
                top += scores.height
                SCREEN.blit(text, scores)

            # Draw rectangle for BACK button
            pygame.draw.rect(SCREEN, (0,0,255), (630, 30, 120, 60), 0)

            # Draw text for 'BACK'
            text4 = START_FONT.render("BACK", 1, START_FONT_COLOR)
            textrect4 = text4.get_rect()
            textrect4.top = 40
            textrect4.centerx = 690
            SCREEN.blit(text4, textrect4)

            # BACK button 
            if mousex >= 630 and mousex <= 750 and mousey >= 30 and mousey <= 90:
                pygame.draw.rect(SCREEN, (0,155,155), (630, 30, 120, 60), 4)  # highlight around the BACK button
                if mousePressed:
                    main()
            if mousex < 630 or mousex > 750 or mousey < 30 or mousey > 90:
                pygame.draw.rect(SCREEN, (0,0,0), (630, 30, 120, 60), 4)  # erase the highlight

        # Update
        pygame.display.update()
        CLOCK.tick()

def read(file):
    """
    Read the maze from the text file.

    This function should be called at the start of a new level.

    @type  file: text file
    @param file: text file of maze

    @rtype  levels: dictionary
    @rparam levels: dictionary that contains info of the level's maze

    -----------------------------------------------------------
    Key for text file:

    @: Comment (does not get read to the maze array)
    #: Wall
    x: Blank space
    *: Player starting position
    o: Pac-dot
    O: Power-pellet
    B: Blinky starting position (if exists)
    P: Pinky starting position (if exists)
    C: Clyde starting position (if exists)
    I: Inky starting position (if exists)
    T: Start teleporter (linked with the end teleporter)
    t: End teleporter (linked with the start teleporter)
    -----------------------------------------------------------
    """
    maze = open(file, "r")
    content = maze.readlines() + ["\r\n"]
    maze.close()

    levels = []
    levelNum = 0
    mazeLines = []
    mazeArray = []
    
    for i in range(len(content)):
        line = content[i].rstrip("\r\n")

        if "@" in line:
            line = line[:line.find("@")]
        if line != "":
            mazeLines.append(line)

        elif line == "" and len(mazeLines) > 0:
            for x in range(len(mazeLines[0])):
                mazeArray.append([])
            for y in range(len(mazeLines)):
                for x in range(len(mazeLines[0])):
                    mazeArray[x].append(mazeLines[y][x])

            startx = starty = startxB = startyB = startxP = startyP = startxC = startyC = startxI = startyI = TstartX = TstartY = TendX = TendY = Tstart = Tend = None  # starting position for gameDict
            pacdots = []
            powerPellet = []
            cherry = []
            strawberry = []
            orange = []
            apple = []
            melon = []
            boss = []
            bell = []
            key = []
            
            for x in range(len(mazeLines[0])):
                for y in range(len(mazeArray[x])):
                    if mazeArray[x][y] in ("*"):
                        startx = x
                        starty = y
                    elif mazeArray[x][y] in ("o"):
                        pacdots.append((x, y))
                    elif mazeArray[x][y] in ("O"):
                        powerPellet.append((x, y))
                    elif mazeArray[x][y] in ("B"):
                        startxB = x
                        startyB = y
                    elif mazeArray[x][y] in ("P"):
                        startxP = x
                        startyP = y
                    elif mazeArray[x][y] in ("C"):
                        startxC = x
                        startyC = y
                    elif mazeArray[x][y] in ("I"):
                        startxI = x
                        startyI = y
                    elif mazeArray[x][y] in ("T"):
                        TstartX = x
                        TstartY = y
                    elif mazeArray[x][y] in ("t"):
                        TendX = x
                        TendY = y

            gameDict = {"player"       : (startx, starty),
                        "blinky"       : (startxB, startyB),
                        "pinky"        : (startxP, startyP),
                        "clyde"        : (startxC, startyC),
                        "inky"         : (startxI, startyI),
                        "startB"       : (startxB, startyB),
                        "startP"       : (startxP, startyP),
                        "startC"       : (startxC, startyC),
                        "startI"       : (startxI, startyI),
                        "pacdots"      : pacdots,
                        "powerPellet"  : powerPellet,
                        "start"        : (TstartX, TstartY),
                        "end"          : (TendX, TendY),
                        "cherry"       : cherry,
                        "strawberry"   : strawberry,
                        "orange"       : orange,
                        "apple"        : apple,
                        "melon"        : melon,
                        "boss"         : boss,
                        "bell"         : bell,
                        "key"          : key,
                        "pacdotCounter": 0,
                        "total_pacdots": len(pacdots),
                        "speedCheck"   : 0}
            levelDict = {"width"  : len(mazeLines[0]),
                         "height" : len(mazeArray),
                         "mazeArray": mazeArray,
                         "start"  : gameDict}

            levels.append(levelDict)

            # Renew settings for next level
            mazeLines = []
            mazeArray = []
            gameDict = {}
            levelNum += 1
            
    return levels  

def draw(mazeArray, gameDict, mazeScreen, reverseB, reverseP, reverseC, reverseI, blinkB, blinkP, blinkC, blinkI, fruit, X_SIZE, Y_SIZE):  # function to update screen (after player movement, etc.)
    """
    Return the surface of a screen with updates of movement.

    This function should be called when the screen needs to be updated:
    1) whenever the player moves
    2) whenever the enemy moves
    3) whenever a power pellet is eaten and must be removed off the screen
    4) whenever a pac-dot is eaten and must be removed off the screen
    5) whenever a fruit is eaten and must be removed off the screen
    6) when new fruit should be drawn onto the screen.

    @type  mazeArray : array
    @param mazeArray : array of the maze read from the text file
    @type  gameDict  : dictionary
    @param gameDict  : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  mazeScreen: pygame.Surface()
    @param mazeScreen: surface(screen) that will be copied and later returned to be drawn onto the screen
    @type  reverseB  : boolean
    @param reverseB  : determines whether Blinky is in reverse mode or not (if true: Blinky is in reverse mode, if false: Blinky is not in reverse mode)
    @type  reverseP  : boolean
    @param reverseP  : determines whether Pinky is in reverse mode or not (if true: Pinky is in reverse mode, if false: Pinky is not in reverse mode)
    @type  reverseC  : boolean
    @param reverseC  : determines whether Clyde is in reverse mode or not (if true: Clyde is in reverse mode, if false: Clyde is not in reverse mode)
    @type  reverseI  : boolean
    @param reverseI  : determines whether Inky is in reverse mode or not (if true: Inky is in reverse mode, if false: Inky is not in reverse mode)
    @type  blinkB    : boolean
    @param blinkB    : determines whether Blinky needs to blink when in reverse mode (when 5 seconds remain before the enemy is normal again)
    @type  blinkP    : boolean
    @param blinkP    : determines whether Pinky needs to blink when in reverse mode (when 5 seconds remain before the enemy is normal again)
    @type  blinkC    : boolean
    @param blinkC    : determines whether Clyde needs to blink when in reverse mode (when 5 seconds remain before the enemy is normal again)
    @type  blinkI    : boolean
    @param blinkI    : determines whether Inky needs to blink when in reverse mode (when 5 seconds remain before the enemy is normal again)
    @type  fruit     : integer
    @param fruit     : integer value that shows which fruit should next be drawn onto the screen (1: cherry, 2: strawberry, 3: orange, ....)
    @type  X_SIZE    : integer
    @param X_SIZE    : size of tile's x-coordinate length
    @type  Y_SIZE    : integer
    @param Y_SIZE    : size of tile's y-coordinate length

    @rtype  copyScreen: pygame.Surface()
    @return copyScreen: The surface with all updates of movement. This will be drawn onto the screen.
    """
    copyScreen = mazeScreen.copy()
    blitFruit = False
    
    for x in range(len(mazeArray)):
        for y in range(len(mazeArray[x])):
            spaceRect = pygame.Rect(((x+0.2) * X_SIZE, (y+0.2) * Y_SIZE, 50, 85))
            if (x, y) in gameDict["powerPellet"]:
                copyScreen.blit(pygame.image.load("assets/power_pellet.png"), spaceRect)
            elif (x, y) == gameDict["player"]:
                copyScreen.blit(PLAYER_IMAGE, spaceRect)
            elif (x, y) in gameDict["cherry"]:
                copyScreen.blit(FRUIT["cherry"], spaceRect)
            elif (x, y) in gameDict["strawberry"]:
                copyScreen.blit(FRUIT["strawberry"], spaceRect)
            elif (x, y) in gameDict["orange"]:
                copyScreen.blit(FRUIT["orange"], spaceRect)
            elif (x, y) in gameDict["apple"]:
                copyScreen.blit(FRUIT["apple"], spaceRect)
            elif (x, y) in gameDict["melon"]:
                copyScreen.blit(FRUIT["melon"], spaceRect)
            elif (x, y) in gameDict["boss"]:
                copyScreen.blit(FRUIT["boss"], spaceRect)
            elif (x, y) in gameDict["bell"]:
                copyScreen.blit(FRUIT["bell"], spaceRect)
            elif (x, y) in gameDict["key"]:
                copyScreen.blit(FRUIT["key"], spaceRect)
            elif (x, y) in gameDict["pacdots"]:
                copyScreen.blit(pygame.image.load("assets/pacdot.png"), spaceRect)
            elif (x, y) == gameDict["blinky"]:
                if reverseB == True:
                    if blinkB == True:
                        num = random.randint(1,2)
                        if num == 1:
                            image = pygame.image.load("assets/enemy_eaten.jpg")
                        else:
                            image = pygame.image.load("assets/enemy_eaten_blink.jpg")
                    else:
                        image = pygame.image.load("assets/enemy_eaten.jpg")
                    copyScreen.blit(image, spaceRect)
                else:
                   copyScreen.blit(pygame.image.load("assets/blinky.jpg"), spaceRect)
            elif (x, y) == gameDict["pinky"]:
                if reverseP == True:
                    if blinkP == True:
                        num = random.randint(1,2)
                        if num == 1:
                            image = pygame.image.load("assets/enemy_eaten.jpg")
                        else:
                            image = pygame.image.load("assets/enemy_eaten_blink.jpg")
                    else:
                        image = pygame.image.load("assets/enemy_eaten.jpg")
                    copyScreen.blit(image, spaceRect)
                else:
                    copyScreen.blit(pygame.image.load("assets/pinky.jpg"), spaceRect)
            elif (x, y) == gameDict["clyde"]:
                if reverseC == True:
                    if blinkC == True:
                        num = random.randint(1,2)
                        if num == 1:
                            image = pygame.image.load("assets/enemy_eaten.jpg")
                        else:
                            image = pygame.image.load("assets/enemy_eaten_blink.jpg")
                    else:
                        image = pygame.image.load("assets/enemy_eaten.jpg")
                    copyScreen.blit(image, spaceRect)
                else:
                    copyScreen.blit(pygame.image.load("assets/clyde.jpg"), spaceRect)
            elif (x, y) == gameDict["inky"]:
                if reverseI == True:
                    if blinkI == True:
                        num = random.randint(1,2)
                        if num == 1:
                            image = pygame.image.load("assets/enemy_eaten.jpg")
                        else:
                            image = pygame.image.load("assets/enemy_eaten_blink.jpg")
                    else:
                        image = pygame.image.load("assets/enemy_eaten.jpg")
                    copyScreen.blit(image, spaceRect)
                else:
                    copyScreen.blit(pygame.image.load("assets/inky.jpg"), spaceRect)

    if fruit != 0 and blitFruit == False:
        x = y = None
        while (x, y) == (None, None):
            x = random.randint(1, len(mazeArray)-1)
            y = random.randint(1, len(mazeArray[0])-1)
            if mazeArray[x][y] in ("#") or mazeArray[x][y] in ("x") or mazeArray[x][y] in ("-"):
                x = y = None

        fruitRect = pygame.Rect((x * X_SIZE, y * Y_SIZE, 50, 85))
        if fruit == 1:
            copyScreen.blit(FRUIT["cherry"], fruitRect)
            gameDict["cherry"].append((x,y))
        elif fruit == 2:
            copyScreen.blit(FRUIT["strawberry"], fruitRect)
            gameDict["strawberry"].append((x,y))
        elif fruit == 3:
            copyScreen.blit(FRUIT["orange"], fruitRect)
            gameDict["orange"].append((x,y))
        elif fruit == 4:
            copyScreen.blit(FRUIT["apple"], fruitRect)
            gameDict["apple"].append((x,y))
        elif fruit == 5:
            copyScreen.blit(FRUIT["melon"], fruitRect)
            gameDict["melon"].append((x,y))
        elif fruit == 6:
            copyScreen.blit(FRUIT["boss"], fruitRect)
            gameDict["boss"].append((x,y))
        elif fruit == 7:
            copyScreen.blit(FRUIT["bell"], fruitRect)
            gameDict["bell"].append((x,y))
        elif fruit == 8:
            copyScreen.blit(FRUIT["key"], fruitRect)
            gameDict["key"].append((x,y))
        
        blitFruit = True
    
    blackRect = pygame.Rect((SCREEN_WIDTH/4*3 * X_SIZE, (SCREEN_HEIGHT - 30) * Y_SIZE, 50, 85))
    for i in range(gameDict["speedCheck"]):
        copyScreen.blit(pygame.image.load("assets/speed.png"), blackRect)
    
    return copyScreen

def drawOriginal(mazeArray, gameDict, num, levels, X_SIZE, Y_SIZE):
    """
    Return the basic surface of a screen that will not change during the level.

    This function should be called at the start of a new level to draw the basic settings (walls, text(score,level,lives)) onto the screen.

    @type  mazeArray : array
    @param mazeArray : array of the maze read from the text file
    @type  gameDict  : dictionary
    @param gameDict  : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  num       : integer
    @param num       : current level index
    @type  levels    : dictionary
    @param levels    : dictionary that contains info of the level's maze (created from read() function)
    @type  X_SIZE    : integer
    @param X_SIZE    : size of tile's x-coordinate length
    @type  Y_SIZE    : integer
    @param Y_SIZE    : size of tile's y-coordinate length

    @rtype  mazeScreen: pygame.Surface()
    @return mazeScreen: The surface with all basic settings drawn. This screen will not change.
    """
    width = len(mazeArray) * X_SIZE
    height= (len(mazeArray[0]) - 1) * Y_SIZE + 85
    mazeScreen = pygame.Surface((width, height))
    
    mazeScreen.fill(SCREEN_COLOR)

    # Code to draw grid lines
    #
    #for x in range(0, width, X_SIZE):
    #   pygame.draw.line(mazeScreen, (49,79,79), (x,0), (x,height-85))
    #for y in range(0, height-85, Y_SIZE):
    #   pygame.draw.line(mazeScreen, (49,79,79), (0,y), (width,y))

    if X_SIZE == 35 and Y_SIZE == 35:
        wall = pygame.image.load("assets/wall-35.png")
        blank = pygame.image.load("assets/wall_blank-35.png")
        line = pygame.image.load("assets/line-35.png")
    elif X_SIZE == 25 and Y_SIZE == 35:
        wall = pygame.image.load("assets/wall-25x35.png")
        blank = pygame.image.load("assets/wall_blank-25x35.png")
        line = pygame.image.load("assets/line-25x35.png")
    for x in range(len(mazeArray)):
        for y in range(len(mazeArray[x])):
            spaceRect = pygame.Rect((x * X_SIZE, y * Y_SIZE, 50, 85))
            if mazeArray[x][y] == "#":  # wall
                mazeScreen.blit(wall, spaceRect)
            elif mazeArray[x][y] == "x":  # blank space
                mazeScreen.blit(blank, spaceRect)
            elif mazeArray[x][y] == "-":
                mazeScreen.blit(line, spaceRect)

    # Text that shows score
    scoreScreen = LARGEFONT.render("SCORE: ", 1, FONT_COLOR)
    scoreRect = scoreScreen.get_rect()
    scoreRect.bottomleft = (SCREEN_WIDTH/2-100, 40)
    SCREEN.blit(scoreScreen, scoreRect)
    
    # Text that shows the level number
    levelScreen = FONT.render("Level %s of %s" % (num + 1, len(levels)), 1, FONT_COLOR)
    levelRect = levelScreen.get_rect()
    levelRect.bottomleft = (20, SCREEN_HEIGHT - 35)
    SCREEN.blit(levelScreen, levelRect)

    # HOME button
    text = FONT.render("HOME", 1, FONT_COLOR)
    textrect = text.get_rect()
    textrect.top = 675
    textrect.centerx = 1160 
    pygame.draw.rect(SCREEN, (255,0,0), (1120,670,80,30), 0)
    SCREEN.blit(text, textrect)
    
    # Text that shows lives
    livesScreen = FONT.render("Lives: ", 1, FONT_COLOR)
    livesRect = livesScreen.get_rect()
    livesRect.bottomleft = (20, SCREEN_HEIGHT-10)
    SCREEN.blit(livesScreen, livesRect)
    
    return mazeScreen

def enemyBestMove(mazeArray, gameDict, enemy):
    """
    Determines the best move for the enemy to make it closer to Pac-Man.

    This function should be called when the enemy needs to decide which direction to go next.

    @type  mazeArray: array
    @param mazeArray: array of the maze read from the text file
    @type  gameDict : dictionary
    @param gameDict : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  enemy    : integer
    @param enemy    : determines which enemy's move is going to be calculated (1: Blinky, 2: Inky)

    @rtype  bestMove: integer
    @rparam bestMove: direction for the best move (1: left, 2: right, 3: up, 4: down)

    -----------------------------------------------------------
    Logic for the AI:
    1. The enemy first determines what moves are available (up,right,down,left)
    2. Then, the enemy determines which move makes it closer to Pac-Man
    -----------------------------------------------------------
    """
    if enemy == 1:
        xE, yE = gameDict["blinky"]
    elif enemy == 2:
        xE, yE = gameDict["inky"]

    bestMove = 0
    bestMoveNum = sys.maxsize
    right = left = up = down = False  # boolean values that determine which direction is available (not blocked by a wall)
    
    if mazeArray[xE-1][yE] not in ("#"):
        left = True
        if findDistance(mazeArray, gameDict, xE - 1, yE) < bestMoveNum:
            bestMoveNum = findDistance(mazeArray, gameDict, xE - 1, yE)
            bestMove = 1 # left
    if mazeArray[xE+1][yE] not in ("#"):
        right = True
        if findDistance(mazeArray, gameDict, xE + 1, yE) < bestMoveNum:
            bestMoveNum = findDistance(mazeArray, gameDict, xE + 1, yE)
            bestMove = 2 # right
    if mazeArray[xE][yE-1] not in ("#"):
        up = True
        if findDistance(mazeArray, gameDict, xE, yE - 1) < bestMoveNum:
            bestMoveNum = findDistance(mazeArray, gameDict, xE, yE - 1)
            bestMove = 3 # up
    if mazeArray[xE][yE+1] not in ("#"):
        down = True
        if findDistance(mazeArray, gameDict, xE, yE + 1) < bestMoveNum:
            bestMoveNum = findDistance(mazeArray, gameDict, xE, yE + 1)
            bestMove = 4 # down

    if bestMove != 0:
        return bestMove
    else:
        if left == True:
            return 1
        elif right == True:
            return 2
        elif up == True:
            return 3
        elif down == True:
            return 4
        else:
            return random.randint(1,4)

# Escape from Pac-Man (when Pac-Man has eaten power pellet)
def enemyWorstMove(mazeArray, gameDict, enemy):
    """
    Determines the "worse" move for the enemy to make it farther from Pac-Man.

    This function should be called when the enemy is in reverse mode and should try to move away from Pac-Man.

    @type  mazeArray: array
    @param mazeArray: array of the maze read from the text file
    @type  gameDict : dictionary
    @param gameDict : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  enemy    : integer
    @param enemy    : determines which enemy's move is going to be calculated (1: Blinky, 2: Pinky, 3: Inky)

    @rtype  worstMove: integer
    @rparam worstMove: direction for the "worst" move (1: left, 2: right, 3: up, 4: down)

    -----------------------------------------------------------
    Logic for the AI:
    1. The enemy first determines what moves are available (up,right,down,left)
    2. Then, the enemy determines which move makes it farther from Pac-Man
    -----------------------------------------------------------
    """
    if enemy == 1:
        xE, yE = gameDict["blinky"]
    elif enemy == 2:
        xE, yE = gameDict["pinky"]
    elif enemy == 3:
        xE, yE = gameDict["inky"]

    worstMove = 0
    worstMoveNum = 0
    right = left = up = down = False  # boolean values that determine which direction is available (not blocked by a wall)
    
    if mazeArray[xE-1][yE] not in ("#"):
        left = True
        if findDistance(mazeArray, gameDict, xE - 1, yE) > worstMoveNum:
            worstMoveNum = findDistance(mazeArray, gameDict, xE - 1, yE)
            worstMove = 1 # left
    if mazeArray[xE+1][yE] not in ("#"):
        right = True
        if findDistance(mazeArray, gameDict, xE + 1, yE) > worstMoveNum:
            worstMoveNum = findDistance(mazeArray, gameDict, xE + 1, yE)
            worstMove = 2 # right
    if mazeArray[xE][yE-1] not in ("#"):
        up = True
        if findDistance(mazeArray, gameDict, xE, yE - 1) > worstMoveNum:
            worstMoveNum = findDistance(mazeArray, gameDict, xE, yE - 1)
            worstMove = 3 # up
    if mazeArray[xE][yE+1] not in ("#"):
        down = True
        if findDistance(mazeArray, gameDict, xE, yE + 1) > worstMoveNum:
            worstMoveNum = findDistance(mazeArray, gameDict, xE, yE + 1)
            worstMove = 4 # down

    if worstMove != 0:
        return worstMove
    else:
        if left == True:
            return 1
        elif right == True:
            return 2
        elif up == True:
            return 3
        elif down == True:
            return 4
        else:
            return random.randint(1,4)

def findDistance(mazeArray, gameDict, x, y):
    """
    Determines the distance from Pac-Man to the specified (x, y) coordinate

    This function is used in the enemyBestMove() and enemyWorstMove() function.

    @type  mazeArray: array
    @param mazeArray: array of the maze read from the text file
    @type  gameDict : dictionary
    @param gameDict : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  x        : integer
    @param x        : x-coordinate
    @type  y        : integer
    @param y        : y-coordinate

    @rtype : integer
    @rparam: distance from Pac-Man to specified (x, y) coordinate
    """
    xP, yP = gameDict["player"]
    if x >= xP:
        if y >= yP:
            return (x - xP + y - yP)
        else:
            return (x - xP + yP - y)
    else:
        if y >= yP:
            return (xP - x + y - yP)
        else:
            return (xP - x + yP - y)

def enemyFrontMove(mazeArray, gameDict, direction):
    """
    Determines the best move for the enemy to make it closer to the coordinate in front of Pac-Man.

    This function should be called when Pinky needs to decide which direction to go next.
    Pinky's AI is programmed so it aims for a position in front of Pac-Man's mouth.

    @type  mazeArray: array
    @param mazeArray: array of the maze read from the text file
    @type  gameDict : dictionary
    @param gameDict : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  direction: integer
    @param direction: current direction of Pac-Man 

    @rtype  bestMove: integer
    @rparam bestMove: direction for the best move (1: left, 2: right, 3: up, 4: down)

    -----------------------------------------------------------
    Logic for the AI:
    1. The enemy first determines what moves are available (up,right,down,left)
    2. Then, the enemy determines which move makes it closer to the position in front of Pac-Man's mouth
    -----------------------------------------------------------
    """
    xE, yE = gameDict["pinky"]

    bestMove = 0
    bestMoveNum = sys.maxsize
    right = left = up = down = False  # boolean values that determine which direction is available (not blocked by a wall)
    
    if mazeArray[xE-1][yE] not in ("#"):
        left = True
        if findDistanceP(mazeArray, gameDict, xE - 1, yE, direction) < bestMoveNum:
            bestMoveNum = findDistanceP(mazeArray, gameDict, xE - 1, yE, direction)
            bestMove = 1 # left
    if mazeArray[xE+1][yE] not in ("#"):
        right = True
        if findDistanceP(mazeArray, gameDict, xE + 1, yE, direction) < bestMoveNum:
            bestMoveNum = findDistanceP(mazeArray, gameDict, xE + 1, yE, direction)
            bestMove = 2 # right
    if mazeArray[xE][yE-1] not in ("#"):
        up = True
        if findDistanceP(mazeArray, gameDict, xE, yE - 1, direction) < bestMoveNum:
            bestMoveNum = findDistanceP(mazeArray, gameDict, xE, yE - 1, direction)
            bestMove = 3 # up
    if mazeArray[xE][yE+1] not in ("#"):
        down = True
        if findDistanceP(mazeArray, gameDict, xE, yE + 1, direction) < bestMoveNum:
            bestMoveNum = findDistanceP(mazeArray, gameDict, xE, yE + 1, direction)
            bestMove = 4 # down

    if bestMove != 0:
        return bestMove
    else:
        if left == True:
            return 1
        elif right == True:
            return 2
        elif up == True:
            return 3
        elif down == True:
            return 4
        else:
            return random.randint(1,4)

def findDistanceP(mazeArray, gameDict, x, y, direction):
    """
    Determines the distance from Pac-Man to the specified (x, y) coordinate

    This function is used in the enemyFrontMove() function.

    @type  mazeArray: array
    @param mazeArray: array of the maze read from the text file
    @type  gameDict : dictionary
    @param gameDict : dictionary of all variables that are related with movement (coordinates of player/enemy, arrays of coordinates of pac-dots, power-pellets)
    @type  x        : integer
    @param x        : x-coordinate
    @type  y        : integer
    @param y        : y-coordinate
    @type  direction: integer
    @param direction: current direction of Pac-Man

    @rtype : integer
    @rparam: distance from the position in front of Pac-Man's mouth to specified (x, y) coordinate
    """
    xP, yP = gameDict["player"]
    a = b = 0
    if direction == "right":
        a = xP + 1
        b = yP
    elif direction == "left":
        a = xP - 1
        b = yP
    elif direction == "up":
        a = xP
        b = yP - 1
    elif direction == "down":
        a = xP
        b = yP + 1
    
    if x >= a:
        if y >= b:
            return (x - a + y - b)
        else:
            return (x - a + b - y)
    else:
        if y >= yP:
            return (a - x + y - b)
        else:
            return (a - x + b - y)

# Call the main() function
if __name__ == "__main__":
    main()
