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
    global CLOCK, SCREEN, FONT, LARGEFONT, SCORE, LIVES, HIGH_SCORE_MIN, LINES

    pygame.init()
    CLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    VLARGEFONT = pygame.font.Font("freesansbold.ttf", 50)
    LARGEFONT = pygame.font.Font("freesansbold.ttf", 30)
    FONT = pygame.font.Font("freesansbold.ttf", 18)
    
    pygame.display.set_caption("Professor Pac-Man")
    pygame.display.set_icon(pygame.image.load("assets/pacmanR.png"))
    
    SCORE = 0
    LIVES = 3
    LEVEL = 1

    # MUSIC FILES
    correct = pygame.mixer.Sound("sounds/eatGhost.ogg")
    loseLife = pygame.mixer.Sound("sounds/death.ogg")
    finishedGame = pygame.mixer.Sound("sounds/finishedGame.ogg")
        
    # Variables used later to determine high score
    LINES = 0
    HIGH_SCORE_MIN = sys.maxsize

    # calculates HIGH_SCORE_MIN (the lowest score on the high score board, used later to calculate whether the player made high score)
    countNum = 0
    with open("data/save_file_PP.txt", "r") as f:
        for line in f:
            LINES += 1
            for s in line.split("     "):
                countNum += 1
                if (countNum-2)%3 == 0 and countNum >= 2:
                    if int(s) < HIGH_SCORE_MIN:
                        HIGH_SCORE_MIN = int(s)

    start()  # Start Screen interface
                    
    index = 0
    Questions = []
        
    questions_file = open("data/questions.txt", "r")
    lines = questions_file.readlines()
    questions_file.close()

    for i in range(len(lines)):
        line = lines[i].rstrip("\r\n")
        Questions.append(line)

    num = len(Questions)

    PACMAN = pygame.image.load("assets/pacmanR.png")
    PACMAN_C = pygame.image.load("assets/pacmanR_C.png")
    PacX = 150
    PacY = 155
    PacSpeed = 5
    P_IMAGE = PACMAN

    top = 210

    quickChange = False  # boolean value used for Pac-Man animation
    timeUp = False
    gameOver = False

    # Boolean values used when game is completed
    timeDraw = False
    askName  = False

    # Mouse coordinate values
    mousex = 0
    mousey = 0
    
    questionFinished = False  # boolean value that indicates whether level is finished or not
        
    while True:
        questionIndex = index
        keyPressed = False
        mousePressed = False

        PacX += PacSpeed
        if PacX == SCREEN_WIDTH-150:
            timeUp = True
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_1:
                    if Questions[questionIndex + 5] != "1":
                        if LIVES > 1:
                            timeUp = True
                        elif LIVES == 1:
                            LIVES -= 1
                            keyPressed = False
                    else:
                        questionFinished = True
                    if LIVES != 0:
                        keyPressed = False
                elif event.key == K_2:
                    if Questions[questionIndex + 5] != "2":
                        if LIVES > 1:
                            timeUp = True
                        elif LIVES == 1:
                            LIVES -= 1
                            keyPressed = False
                    else:
                        questionFinished = True
                    if LIVES != 0:
                        keyPressed = False
                elif event.key == K_3:
                    if Questions[questionIndex + 5] != "3":
                        if LIVES > 1:
                            timeUp = True
                        elif LIVES == 1:
                            LIVES -= 1
                            keyPressed = False
                    else:
                        questionFinished = True
                    if LIVES != 0:
                        keyPressed = False
                elif event.key == K_4:
                    if Questions[questionIndex + 5] != "4":
                        if LIVES > 1:
                            timeUp = True
                        elif LIVES == 1:
                            LIVES -= 1
                            keyPressed = False
                    else:
                        questionFinished = True
                    if LIVES != 0:
                        keyPressed = False
                        

            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mousePressed = True

        if quickChange == False:
            P_IMAGE = PACMAN
            quickChange = True
        else:
            P_IMAGE = PACMAN_C
            quickChange = False

        SCREEN.fill(SCREEN_COLOR)

        pygame.draw.line(SCREEN, FONT_COLOR, (25,200), (SCREEN_WIDTH-25, 200), 4)
        pygame.draw.line(SCREEN, FONT_COLOR, (25,SCREEN_HEIGHT-35), (SCREEN_WIDTH-25, SCREEN_HEIGHT-35), 4)
        pygame.draw.line(SCREEN, FONT_COLOR, (25,200), (25, SCREEN_HEIGHT-35), 4)
        pygame.draw.line(SCREEN, FONT_COLOR, (SCREEN_WIDTH-25,200), (SCREEN_WIDTH-25, SCREEN_HEIGHT-35), 4)

        # Score Line
        lineRect = pygame.image.load("assets/scoreLine.png").get_rect()
        lineRect.bottomleft = (150, 180)
        SCREEN.blit(pygame.image.load("assets/scoreLine.png"), lineRect)

        # Text that shows lives
        livesScreen = VLARGEFONT.render("%s" % LIVES, 1, START_FONT_COLOR)
        livesRect = livesScreen.get_rect()
        livesRect.bottomleft = (SCREEN_WIDTH-175, 80)
        SCREEN.blit(livesScreen, livesRect)

        strawRect = pygame.image.load("assets/strawberry.jpg").get_rect()
        strawRect.bottomleft = (SCREEN_WIDTH-170, 110)
        SCREEN.blit(pygame.image.load("assets/strawberry.jpg"), strawRect)

        # Image that shows score
        scoreRect = pygame.image.load("assets/scoreBoard.jpg").get_rect()
        scoreRect.bottomleft = (SCREEN_WIDTH/2, 150)
        SCREEN.blit(pygame.image.load("assets/scoreBoard.jpg"), scoreRect)

        scoreScreen = VLARGEFONT.render("%s" % (SCORE), 1, FONT_COLOR)
        score1Rect = scoreScreen.get_rect()
        score1Rect.centerx = SCREEN_WIDTH/2+175
        score1Rect.top = 65
        SCREEN.blit(scoreScreen, score1Rect)
    
        # Text that shows the level number
        numberRect = pygame.image.load("assets/profPacMan.jpg").get_rect()
        numberRect.bottomleft = (300, 150)
        SCREEN.blit(pygame.image.load("assets/profPacMan.jpg"), numberRect)

        numberScreen = LARGEFONT.render("%s" % (LEVEL), 1, FONT_COLOR)
        number1Rect = numberScreen.get_rect()
        number1Rect.centerx = 365
        number1Rect.top = 118
        SCREEN.blit(numberScreen, number1Rect)

        # HOME button
        text = FONT.render("HOME", 1, FONT_COLOR)
        textrect = text.get_rect()
        textrect.top = 675
        textrect.centerx = 1160 
        pygame.draw.rect(SCREEN, (255,0,0), (1120,670,80,30), 0)
        SCREEN.blit(text, textrect)

        question = LARGEFONT.render(Questions[questionIndex], 1, FONT_COLOR)
        questionRect = question.get_rect()
        questionRect.top = top
        questionRect.centerx = SCREEN_WIDTH/2
        SCREEN.blit(question, questionRect)
        
        question1 = LARGEFONT.render(Questions[questionIndex + 1], 1, FONT_COLOR)
        question1Rect = question1.get_rect()
        question1Rect.top = top + 100
        question1Rect.x = 100
        SCREEN.blit(question1, question1Rect)

        question2 = LARGEFONT.render(Questions[questionIndex + 2], 1, FONT_COLOR)
        question2Rect = question2.get_rect()
        question2Rect.top = top + 200
        question2Rect.x = 100
        SCREEN.blit(question2, question2Rect)

        question3 = LARGEFONT.render(Questions[questionIndex + 3], 1, FONT_COLOR)
        question3Rect = question3.get_rect()
        question3Rect.top = top + 300
        question3Rect.x = 100
        SCREEN.blit(question3, question3Rect)

        question4 = LARGEFONT.render(Questions[questionIndex + 4], 1, FONT_COLOR)
        question4Rect = question4.get_rect()
        question4Rect.top = top + 400
        question4Rect.x = 100
        SCREEN.blit(question4, question4Rect)
                
        SCREEN.blit(P_IMAGE, (PacX, PacY))

        if timeUp == True:
            loseLife.play(0)
            if Questions[questionIndex + 5] == "1":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+120), 30, 5)
                pygame.display.update()
            elif Questions[questionIndex + 5] == "2":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+220), 30, 5)
                pygame.display.update()
            elif Questions[questionIndex + 5] == "3":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+320), 30, 5)
                pygame.display.update()
            else:
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+420), 30, 5)
                pygame.display.update()
            LIVES -= 1
            if index == num-6:
                questionFinished = True
                PacX = SCREEN_WIDTH
            if LIVES != 0 and index != num-6:
                index += 7
                LEVEL += 1
            PacX = 100
            timeUp = False
            pygame.time.delay(1000)
        
        # HOME button
        if mousex >= 1120 and mousex <= 1200 and mousey >= 670 and mousey <= 700:
            if mousePressed:
                main()  # go back to the start screen

        # If level is finished (Note: the number of lives remaining must be greater than 0)
        if questionFinished and LIVES > 0:
            if index == num-6:  # if last level
                if timeDraw == False:
                    if Questions[questionIndex + 5] == "1":
                        pygame.draw.circle(SCREEN, (255,0,0), (110,top+120), 30, 5)
                        pygame.display.update()
                    elif Questions[questionIndex + 5] == "2":
                        pygame.draw.circle(SCREEN, (255,0,0), (110,top+220), 30, 5)
                        pygame.display.update()
                    elif Questions[questionIndex + 5] == "3":
                        pygame.draw.circle(SCREEN, (255,0,0), (110,top+320), 30, 5)
                        pygame.display.update()
                    else:
                        pygame.draw.circle(SCREEN, (255,0,0), (110,top+420), 30, 5)
                        pygame.display.update()
                    if PacX < 213:
                        SCORE += 800
                    elif PacX < 325:
                        SCORE += 700
                    elif PacX < 438:
                        SCORE += 600
                    elif PacX < 550:
                        SCORE += 500
                    elif PacX < 663:
                        SCORE += 400
                    elif PacX < 775:
                        SCORE += 300
                    elif PacX < 888:
                        SCORE += 200
                    elif PacX < 1000:
                        SCORE += 100
                    finishedGame.play(0)
                
                # Draw completed image onto screen
                SCREEN.fill(SCREEN_COLOR)
                completedRect = pygame.image.load("assets/completed_PP.png").get_rect()
                completedRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                SCREEN.blit(pygame.image.load("assets/completed_PP.png"), completedRect)

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
                        save_file = open("data/save_file_PP.txt", "r")
                        lines = save_file.readlines()
                        save_file.close()

                        save_file = open("data/save_file_PP.txt", "w")

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
                    pygame.quit()
                    sys.exit()

            else:  # if not last level
                correct.play(0)
                index += 7
                if PacX < 213:
                    SCORE += 800
                elif PacX < 325:
                    SCORE += 700
                elif PacX < 438:
                    SCORE += 600
                elif PacX < 550:
                    SCORE += 500
                elif PacX < 663:
                    SCORE += 400
                elif PacX < 775:
                    SCORE += 300
                elif PacX < 888:
                    SCORE += 200
                else:
                    SCORE += 100

                if Questions[questionIndex + 5] == "1":
                    pygame.draw.circle(SCREEN, (255,0,0), (110,top+120), 30, 5)
                    pygame.display.update()
                elif Questions[questionIndex + 5] == "2":
                    pygame.draw.circle(SCREEN, (255,0,0), (110,top+220), 30, 5)
                    pygame.display.update()
                elif Questions[questionIndex + 5] == "3":
                    pygame.draw.circle(SCREEN, (255,0,0), (110,top+320), 30, 5)
                    pygame.display.update()
                else:
                    pygame.draw.circle(SCREEN, (255,0,0), (110,top+420), 30, 5)
                    pygame.display.update()
                LEVEL += 1
                PacX = 100
                questionFinished = False
                pygame.time.delay(1000)

        if LIVES == 0 and gameOver == False:
            gameOverRect = pygame.image.load("assets/gameover_PP.png").get_rect()
            gameOverRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            SCREEN.blit(pygame.image.load("assets/gameover_PP.png"), gameOverRect)
            PacSpeed = 0

            if Questions[questionIndex + 5] == "1":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+120), 30, 5)
                pygame.display.update()
            elif Questions[questionIndex + 5] == "2":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+220), 30, 5)
                pygame.display.update()
            elif Questions[questionIndex + 5] == "3":
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+320), 30, 5)
                pygame.display.update()
            else:
                pygame.draw.circle(SCREEN, (255,0,0), (110,top+420), 30, 5)
                pygame.display.update()

            if keyPressed:
                gameOver = True
                keyPressed = False

        if gameOver == True:
            # Draw completed image onto screen
            SCREEN.fill(SCREEN_COLOR)
            completedRect = pygame.image.load("assets/completed_PP.png").get_rect()
            completedRect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            SCREEN.blit(pygame.image.load("assets/completed_PP.png"), completedRect)

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
                    save_file = open("data/save_file_PP.txt", "r")
                    lines = save_file.readlines()
                    save_file.close()

                    save_file = open("data/save_file_PP.txt", "w")

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
                pygame.quit()
                sys.exit()

        pygame.display.update()
        CLOCK.tick(25)

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
    title = pygame.image.load("assets/title_PP.png").get_rect()
    title.top = 50
    title.centerx = SCREEN_WIDTH/2
    SCREEN.blit(pygame.image.load("assets/title_PP.png"), title)

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
            Text = ["Professor Pac-Man is a quiz arcade game.",
                    "Answer multiple-choice questions before the time runs out.",
                    "To answer, press the keyboard keys 1, 2, 3, or 4.",
                    "The timer is the original Pac-Man, eating a row of pellets.",
                    "The more pellets left when the player answers, the higher the score given.",
                    "The player starts with 3 fruits.",
                    "The player loses a fruit when the player gets a question wrong.",
                    "If the player runs out of fruits, it is game over.",
                    "There are 10 total questions."]

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
            with open("data/save_file_PP.txt", "r") as f:
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
            save_file = open("data/save_file_PP.txt", "r")
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


# Call the main() function
if __name__ == "__main__":
    main()
