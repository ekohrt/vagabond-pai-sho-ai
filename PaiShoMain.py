# -*- coding: utf-8 -*-
"""
Finished on Sep 20 2021
@author: https://github.com/ekohrt

Pygame UI for playing a game of Vagabond Pai Sho.

Note: Using the AI puts the entire program on hold, so it will not respond
until the calculating time is up and a move is performed. This is because I
am a noob and don't know how to run things in parallel, so... apologies.

"""

import pygame as p
import math
import numpy as np
from constants2 import LOTUS, BISON, WHEEL, BADGER, CHRYS, FIRELILY, DRAGON, EMPTY, BOUNDARY, WHITE_POOL_ROW
from PaiShoEngine import startState, index, coord, getVal, Move
import monteCarlo_vanila_AI
import monteCarlo_with_eval_AI
from button import Button


p.init()
p.display.set_caption('AIroh: Vagabond Pai Sho') #change window name
                      
icon = p.image.load('images_paisho/r_badgermole.png')
p.display.set_icon(icon) #change window icon 

BOARD_WIDTH = BOARD_HEIGHT = 504 #pixels: 504 is nice because it's divisible by 18 and 24. DO NOT CHANGE.
SQ_SIZE = BOARD_WIDTH // 18 #board is 18 squares wide
HALF_SQ = SQ_SIZE//2
SQ_DIAG = SQ_SIZE * math.sqrt(2)
HIGHLIGHT_WIDTH = 2
HIGHLIGHT_RADIUS = SQ_SIZE//2 + HIGHLIGHT_WIDTH

SCREEN_WIDTH = BOARD_WIDTH + (4*SQ_SIZE)
SCREEN_HEIGHT = 504 #DO NOT CHANGE.

MAX_FPS = 60 #doesn't have to be very high for pygame; 15 will work
IMAGES = {}
TYPE_STRINGS = {LOTUS: 'lotus', BISON: 'bison', WHEEL: 'wheel', BADGER: 'badgermole', CHRYS: 'chrysanthemum', FIRELILY: 'firelily', DRAGON: 'dragon', EMPTY: '', BOUNDARY: ''}

POOL_START = BOARD_WIDTH + HALF_SQ #starting x coord on screen for the piece pool

#Map screen points to game board coordinates, and also invert it to map in reverse
#yes I found the screen points by hand. pygame is not the best game engine and I am not the best programmer, lol sorry
screenPointsToBoardCoords = {(13, 174): (12, 0), (13, 213): (13, 1), (13, 252): (14, 2), (13, 292): (15, 3), (13, 331): (16, 4), (34, 154): (11, 0), (34, 193): (12, 1), (34, 232): (13, 2), (34, 272): (14, 3), (34, 312): (15, 4), (34, 351): (16, 5), (53, 134): (10, 0), (53, 174): (11, 1), (53, 213): (12, 2), (53, 252): (13, 3), (53, 292): (14, 4), (53, 331): (15, 5), (53, 371): (16, 6), (73, 114): (9, 0), (73, 154): (10, 1), (73, 193): (11, 2), (73, 232): (12, 3), (73, 272): (13, 4), (73, 312): (14, 5), (73, 351): (15, 6), (73, 391): (16, 7), (92, 95): (8, 0), (92, 134): (9, 1), (92, 174): (10, 2), (92, 213): (11, 3), (92, 252): (12, 4), (92, 292): (13, 5), (92, 331): (14, 6), (92, 371): (15, 7), (92, 411): (16, 8), (112, 75): (7, 0), (112, 114): (8, 1), (112, 154): (9, 2), (112, 193): (10, 3), (112, 232): (11, 4), (112, 272): (12, 5), (112, 312): (13, 6), (112, 351): (14, 7), (112, 391): (15, 8), (112, 431): (16, 9), (132, 55): (6, 0), (132, 95): (7, 1), (132, 134): (8, 2), (132, 174): (9, 3), (132, 213): (10, 4), (132, 252): (11, 5), (132, 292): (12, 6), (132, 331): (13, 7), (132, 371): (14, 8), (132, 411): (15, 9), (132, 451): (16, 10), (152, 35): (5, 0), (152, 75): (6, 1), (152, 114): (7, 2), (152, 154): (8, 3), (152, 193): (9, 4), (152, 232): (10, 5), (152, 272): (11, 6), (152, 312): (12, 7), (152, 351): (13, 8), (152, 391): (14, 9), (152, 431): (15, 10), (152, 470): (16, 11), (172, 16): (4, 0), (172, 55): (5, 1), (172, 95): (6, 2), (172, 134): (7, 3), (172, 174): (8, 4), (172, 213): (9, 5), (172, 252): (10, 6), (172, 292): (11, 7), (172, 331): (12, 8), (172, 371): (13, 9), (172, 411): (14, 10), (172, 451): (15, 11), (172, 490): (16, 12), (192, 35): (4, 1), (192, 75): (5, 2), (192, 114): (6, 3), (192, 154): (7, 4), (192, 193): (8, 5), (192, 232): (9, 6), (192, 272): (10, 7), (192, 312): (11, 8), (192, 351): (12, 9), (192, 391): (13, 10), (192, 431): (14, 11), (192, 470): (15, 12), (212, 16): (3, 1), (212, 55): (4, 2), (212, 95): (5, 3), (212, 134): (6, 4), (212, 174): (7, 5), (212, 213): (8, 6), (212, 252): (9, 7), (212, 292): (10, 8), (212, 331): (11, 9), (212, 371): (12, 10), (212, 411): (13, 11), (212, 451): (14, 12), (212, 490): (15, 13), (231, 35): (3, 2), (231, 75): (4, 3), (231, 114): (5, 4), (231, 154): (6, 5), (231, 193): (7, 6), (231, 232): (8, 7), (231, 272): (9, 8), (231, 312): (10, 9), (231, 351): (11, 10), (231, 391): (12, 11), (231, 431): (13, 12), (231, 470): (14, 13), (252, 16): (2, 2), (251, 55): (3, 3), (251, 95): (4, 4), (251, 134): (5, 5), (251, 174): (6, 6), (251, 213): (7, 7), (251, 252): (8, 8), (251, 292): (9, 9), (251, 331): (10, 10), (251, 371): (11, 11), (251, 411): (12, 12), (251, 451): (13, 13), (251, 490): (14, 14), (271, 35): (2, 3), (271, 75): (3, 4), (271, 114): (4, 5), (271, 154): (5, 6), (271, 193): (6, 7), (271, 232): (7, 8), (271, 272): (8, 9), (271, 312): (9, 10), (271, 351): (10, 11), (271, 391): (11, 12), (271, 431): (12, 13), (271, 470): (13, 14), (291, 16): (1, 3), (291, 55): (2, 4), (291, 95): (3, 5), (291, 134): (4, 6), (291, 174): (5, 7), (291, 213): (6, 8), (291, 252): (7, 9), (291, 292): (8, 10), (291, 331): (9, 11), (291, 371): (10, 12), (291, 411): (11, 13), (291, 451): (12, 14), (291, 490): (13, 15), (310, 35): (1, 4), (310, 75): (2, 5), (310, 114): (3, 6), (310, 154): (4, 7), (310, 193): (5, 8), (310, 232): (6, 9), (310, 272): (7, 10), (310, 312): (8, 11), (310, 351): (9, 12), (310, 391): (10, 13), (310, 431): (11, 14), (310, 470): (12, 15), (330, 16): (0, 4), (330, 55): (1, 5), (330, 95): (2, 6), (330, 134): (3, 7), (330, 174): (4, 8), (330, 213): (5, 9), (330, 252): (6, 10), (330, 292): (7, 11), (330, 331): (8, 12), (330, 371): (9, 13), (330, 411): (10, 14), (330, 451): (11, 15), (330, 490): (12, 16), (350, 35): (0, 5), (350, 75): (1, 6), (350, 114): (2, 7), (350, 154): (3, 8), (350, 193): (4, 9), (350, 232): (5, 10), (350, 272): (6, 11), (350, 312): (7, 12), (350, 351): (8, 13), (350, 391): (9, 14), (350, 431): (10, 15), (350, 470): (11, 16), (370, 55): (0, 6), (370, 95): (1, 7), (370, 134): (2, 8), (370, 174): (3, 9), (370, 213): (4, 10), (370, 252): (5, 11), (370, 292): (6, 12), (370, 331): (7, 13), (370, 371): (8, 14), (370, 411): (9, 15), (371, 450): (10, 16), (390, 75): (0, 7), (390, 114): (1, 8), (390, 154): (2, 9), (390, 193): (3, 10), (390, 232): (4, 11), (390, 272): (5, 12), (390, 312): (6, 13), (390, 351): (7, 14), (390, 390): (8, 15), (390, 431): (9, 16), (410, 95): (0, 8), (410, 134): (1, 9), (410, 174): (2, 10), (410, 213): (3, 11), (410, 252): (4, 12), (410, 292): (5, 13), (410, 331): (6, 14), (410, 371): (7, 15), (410, 411): (8, 16), (429, 114): (0, 9), (429, 154): (1, 10), (429, 193): (2, 11), (429, 232): (3, 12), (429, 272): (4, 13), (429, 312): (5, 14), (429, 351): (6, 15), (429, 391): (7, 16), (449, 134): (0, 10), (449, 174): (1, 11), (449, 213): (2, 12), (449, 252): (3, 13), (449, 292): (4, 14), (449, 331): (5, 15), (449, 371): (6, 16), (469, 154): (0, 11), (469, 193): (1, 12), (469, 232): (2, 13), (469, 272): (3, 14), (469, 312): (4, 15), (469, 351): (5, 16), (489, 174): (0, 12), (489, 213): (1, 13), (489, 252): (2, 14), (489, 292): (3, 15), (489, 331): (4, 16),
                                #white pool (row 17)
                                (POOL_START, HALF_SQ): (17,0), (POOL_START+SQ_SIZE, HALF_SQ): (17,1), (POOL_START+2*SQ_SIZE, HALF_SQ): (17,2), (POOL_START+3*SQ_SIZE, HALF_SQ): (17,3),
                                (POOL_START, 1*SQ_SIZE+HALF_SQ): (17,4), (POOL_START+SQ_SIZE, 1*SQ_SIZE+HALF_SQ): (17,5), (POOL_START+2*SQ_SIZE, 1*SQ_SIZE+HALF_SQ): (17,6), (POOL_START+3*SQ_SIZE, 1*SQ_SIZE+HALF_SQ): (17,7),
                                (POOL_START, 2*SQ_SIZE+HALF_SQ): (17,8), (POOL_START+SQ_SIZE, 2*SQ_SIZE+HALF_SQ): (17,9), (POOL_START+2*SQ_SIZE, 2*SQ_SIZE+HALF_SQ): (17,10), (POOL_START+3*SQ_SIZE, 2*SQ_SIZE+HALF_SQ): (17,11),
                                #red pool (row 18)
                                (POOL_START, 4*SQ_SIZE+HALF_SQ): (18,0), (POOL_START+SQ_SIZE, 4*SQ_SIZE+HALF_SQ): (18,1), (POOL_START+2*SQ_SIZE, 4*SQ_SIZE+HALF_SQ): (18,2), (POOL_START+3*SQ_SIZE, 4*SQ_SIZE+HALF_SQ): (18,3),
                                (POOL_START, 5*SQ_SIZE+HALF_SQ): (18,4), (POOL_START+SQ_SIZE, 5*SQ_SIZE+HALF_SQ): (18,5), (POOL_START+2*SQ_SIZE, 5*SQ_SIZE+HALF_SQ): (18,6), (POOL_START+3*SQ_SIZE, 5*SQ_SIZE+HALF_SQ): (18,7),
                                (POOL_START, 6*SQ_SIZE+HALF_SQ): (18,8), (POOL_START+SQ_SIZE, 6*SQ_SIZE+HALF_SQ): (18,9), (POOL_START+2*SQ_SIZE, 6*SQ_SIZE+HALF_SQ): (18,10), (POOL_START+3*SQ_SIZE, 6*SQ_SIZE+HALF_SQ): (18,11)
                                
                                }    
boardCoordsToScreenPoints = {val:key for key,val in screenPointsToBoardCoords.items()} #invert dict
rawScreenPoints = list(screenPointsToBoardCoords.keys()) #order is important for some things
numpy_screenPoints = np.asarray(rawScreenPoints)

#i guess constructing fonts takes a long time, so do it once here
myFont_10 = p.font.SysFont('Constantia', 10)
myFont_18 = p.font.SysFont('Constantia', 18)



"""
Initialize a global dictionary of images. This will be called exactly once in the main.
"""
def loadImages():
    pieces = ['w_badgermole', 'w_bison', 'w_chrysanthemum', 'w_dragon', 'w_firelily', 'w_lotus', 'w_wheel', 
                  'r_badgermole', 'r_bison', 'r_chrysanthemum', 'r_dragon', 'r_firelily', 'r_lotus', 'r_wheel']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale( p.image.load("images_paisho/" + piece + ".png"), (SQ_SIZE, SQ_SIZE) )
    #Note: we can now access an image by saying "IMAGES['wp']"





"""
Main driver for our code. This will handle user input and updating the graphics.
"""
def main():
    p.init() #initialize pygame
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white")) #start with blank white background
    loadImages() #only do this once, before the while loop
    
    #Buttons
    resetBtn = Button(BOARD_WIDTH, ((BOARD_HEIGHT*3)//4)-35, screen, "Reset", width=110, height=30, text_size=14)
    calculateBtn = Button(BOARD_WIDTH, (BOARD_HEIGHT*3)//4, screen, "Calculate Move", width=110, height=30, text_size=14)
    decTimeBtn = Button(BOARD_WIDTH, ((BOARD_HEIGHT*3)//4)+35, screen, "-", width=30, height=30, text_size=14)
    incTimeBtn = Button(BOARD_WIDTH+80, ((BOARD_HEIGHT*3)//4)+35, screen, "+", width=30, height=30, text_size=14)
    
    boardState = startState() #initialize game state: empty board, player 1
    validMoves = boardState.getAllMoves() #calculate all moves for the current player
    moveMade = False #flag variable for when a move is made - we don't want to calculate this every frame...
    
    #stuff for selecting pieces and showing their moves
    isPieceSelected = False #phase
    selectedPoint = ()
    startCoord = () 
    endCoord = ()
    selectedPiece = -1
    selectedPieceMoves = [] #moves that selected piece can make
    
    timeOptions = [5, 15, 30, 45, 60, 90, 120, 180, 240, 300, 600, 1200] #seconds
    timeChoiceIdx = 2 #default timeOption choice (start at 30sec)
    outputMessage = "Welcome!"
    calculateMove = False
    
    #game loop
    running = True
    while running:
        
        #"The Event Queue"
        for e in p.event.get():
            
            #hitting 'x' button stops game
            if e.type == p.QUIT: 
                running = False
            
            #pressing space does nothing for now, keeping this around for later though
            elif e.type == p.KEYDOWN and e.key == p.K_SPACE:
                print("Space Key Pressed - Nothing happened, carry on.")
            
            #mouse click handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                
                #select space nearest to mouse click
                location = p.mouse.get_pos() #xy location of the mouse
                selectedPoint = closest_point(location)
                selectedCoord = screenPointsToBoardCoords.get(selectedPoint, ())
                
                #Didn't click on the board: reset everything
                if selectedCoord == ():
                    selectedPoint = ()
                    startCoord = ()
                    endCoord = ()
                    isPieceSelected = False
                    selectedPiece = -1
                    selectedPieceMoves = []
                    
                #first click: selecting a piece
                elif not isPieceSelected:
                    startCoord = selectedCoord
                    boardVal = getVal(boardState.board, startCoord[0], startCoord[1])
                    #clicked on player's piece - select it, highlight moves
                    if boardVal // 100 == boardState.turnPlayer:
                        isPieceSelected = True
                        selectedPiece = boardVal
                        selectedPieceMoves = getMovesForPiece(selectedPiece, validMoves)
                    #clicked on an empty/invalid space - reset everything
                    else:
                        selectedPoint = ()
                        startCoord = ()
                        endCoord = ()
                        isPieceSelected = False
                        selectedPiece = -1
                        selectedPieceMoves = []
                        
                #second click: selecting a move
                else:
                    endCoord = selectedCoord
                    boardVal = getVal(boardState.board, endCoord[0], endCoord[1])
                    #clicked on player's own piece - change starting selection to this piece
                    if boardVal // 100 == boardState.turnPlayer:
                        startCoord = selectedCoord
                        boardVal = getVal(boardState.board, startCoord[0], startCoord[1])
                        isPieceSelected = True
                        selectedPiece = boardVal
                        selectedPieceMoves = getMovesForPiece(selectedPiece, validMoves) #for highlighting
                    #clicked something else - valid move? invalid space?
                    else:
                        #if the selected coord is a valid move, perform it
                        m = constructMove(selectedPiece, startCoord, endCoord, boardState)
                        if m in validMoves:
                            print("move performed", m.toString())
                            boardState.performMove(m)
                            # print("TERR", boardState.bisonTerritories)
                            # print("TRAPPED", boardState.trappedIndices)
                            # print("PROT",boardState.protectedPieces)
                            # print("BISON",pieceIndicesOnBoard(boardState, {boardState.turnPlayer}, {BISON}) )
                            moveMade = True
                            outputMessage = m.toString()
                        #reset everything after this second click
                        selectedPoint = ()
                        startCoord = ()
                        endCoord = ()
                        isPieceSelected = False
                        selectedPiece = -1
                        selectedPieceMoves = []
        #End of event queue
        
        #recalculate valid moves when necessary
        if moveMade:
            validMoves = boardState.getAllMoves()
            moveMade = False
            
        #draw the board
        drawGameState(screen, boardState.board)
        #highlight selected piece and its available moves
        highlightPoint(screen, selectedPoint)
        highlightMoves(screen, selectedPieceMoves)
        
        #RESET BUTTON HANDLER: returns game to its starting state
        if resetBtn.draw_button():
            boardState = startState()
            validMoves = boardState.getAllMoves()
            #reset flags
            isPieceSelected = False
            selectedPoint, startCoord, endCoord = (), (), ()
            selectedPiece = -1
            selectedPieceMoves = []
            outputMessage = "Reset Game."
        
        #CALCULATE BUTTON HANDLER: have the cpu make a move
        if calculateBtn.draw_button():
            calculateMove = True #at the end of this game-loop iteration, calc a move
            thinkTime = timeOptions[timeChoiceIdx]
            outputMessage = "Thinking... (" + str(thinkTime) + " sec)"
        
        #INCREASE TIME BUTTON HANDLER:
        if decTimeBtn.draw_button():
            timeChoiceIdx = max(timeChoiceIdx-1, 0) #don't go below 0
            
        #DECREASE TIME BUTTON HANDLER:
        if incTimeBtn.draw_button(): 
            timeChoiceIdx = min(timeChoiceIdx+1, len(timeOptions)-1) #don't go above length of options list
        
        #text field for displaying the thinking time in seconds (between +/- buttons)
        drawTextBox(screen, decTimeBtn.x+decTimeBtn.width, decTimeBtn.y, 50, decTimeBtn.height, str(timeOptions[timeChoiceIdx]), myFont_18)
        
        #text field for displaying other messages
        field_width = calculateBtn.width
        drawTextBox(screen, decTimeBtn.x, decTimeBtn.y+decTimeBtn.height+5, field_width, 
                    decTimeBtn.height, outputMessage, myFont_10)
        
        
        #pygame upkeep
        clock.tick(MAX_FPS)
        p.display.flip() #updates the screen (you first make changes to a buffer, then it "flips" between the old display and the new one now showing. https://stackoverflow.com/a/48770582)
        
        #after everything: if you clicked the button, calculate a move (this puts the whole program on hold)
        if calculateMove:
            print("Calculating Move...", thinkTime, "seconds")
            print("Analyzing", len(boardState.getAllMoves_Limited()), "moves.")
            print("Note: The game window will not respond until finished calculating.")
            # mcts = monteCarlo_AI.MonteCarlo()
            mcts = monteCarlo_with_eval_AI.MonteCarlo()
            m = mcts.runSearch(boardState, thinkTime)
            print("move performed", m.toString())
#            mcts.printTree(boardState) #debugging
            outputMessage = m.toString()
            boardState = boardState.nextState(m) #perform move
            moveMade = True
            calculateMove = False
    
    #quit the game if you ever exit the loop    
    p.quit() 
    #End of Main



"""
Draws a message on the screen at the given x,y location
"""
def drawText(screen, x, y, message, font_object, text_color=(0,0,0)):
    text_img = font_object.render(message, True, text_color)
    screen.blit(text_img, (x, y))
    return text_img

"""
Draws a rectangle on the screen
"""
def drawRectangle(screen, x, y, width, height, rect_color=(255,255,255)):
    myRect = p.Rect(x, y, width, height)
    p.draw.rect(screen, rect_color, myRect)

"""
Draws a text message inside a rectangle
"""
def drawTextBox(screen, x, y, width, height, message, font_object, text_color=(0,0,0), rect_color=(255,255,255)):
    drawRectangle(screen, x, y, width, height, rect_color)
    
    #add text over rect
    text_img = font_object.render(message, True, text_color)
    
    #try to center the text in the button
    text_x = x + width//2 - text_img.get_width()//2
    text_y = y + height//2 - text_img.get_height()//2 +2
    drawText(screen, text_x, text_y, message, font_object, text_color)


"""
Responsible for all graphics within a current game state
Order is important
"""
def drawGameState(screen, board):
    drawBoard(screen) #draw squares on the board
    drawPieces(screen, board) #draw piecs on top of the squares


"""
Draw the pai sho board's shapes & lines, without pieces.
Fun fact: on a chess board, (row+col)%2 gives the color of the square
"""
def drawBoard(screen):
    darkgrey = p.Color(64,64,64)
    #red corners
    red = p.Color(130, 0, 0)
    p.draw.rect(screen, red, p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)) #params are starting loc and size
    #Side panel for piece pool
    p.draw.rect(screen, darkgrey, p.Rect(BOARD_WIDTH, 0, SCREEN_WIDTH-BOARD_WIDTH, BOARD_HEIGHT))
    
    #brown rectangles across middle
    brown = p.Color(181, 143, 88)
    h = 7 * math.sqrt(2) * (SQ_SIZE)
    corner_offset = ((18-(7*math.sqrt(2))) / 2) * SQ_SIZE
    p.draw.rect(screen, brown, p.Rect(0, corner_offset, BOARD_WIDTH, h))
    p.draw.rect(screen, brown, p.Rect(corner_offset, 0, h, BOARD_WIDTH))
    
    #red square in middle
    p.draw.rect(screen, red, p.Rect(corner_offset, corner_offset, h, h))
    
    #grey triangles
    grey = p.Color(180,180,180)
    midPt = (BOARD_WIDTH/2,BOARD_HEIGHT/2)
    p.draw.polygon(screen, grey, [(corner_offset,corner_offset),(corner_offset+h-1, corner_offset), midPt])
    p.draw.polygon(screen, grey, [(corner_offset,corner_offset+h),(corner_offset+h-1, corner_offset+h), midPt])

    #draw lines for square
    black = p.Color("black")
    p.draw.line(screen, black, (0, corner_offset), (BOARD_WIDTH, corner_offset))
    p.draw.line(screen, black, (0, BOARD_HEIGHT-corner_offset), (BOARD_WIDTH, BOARD_HEIGHT-corner_offset))
    p.draw.line(screen, black, (corner_offset, 0), (corner_offset, BOARD_HEIGHT))
    p.draw.line(screen, black, (BOARD_HEIGHT-corner_offset-1, 0), (BOARD_WIDTH-corner_offset-1, BOARD_HEIGHT))
    
    #draw board lines: bottom left to top right
    yOffset = 187 #for adjusting: shifts lines down
    startX = 0
    endX = BOARD_WIDTH
    numLines = 17
    for i in range(numLines):
        startY = i * SQ_DIAG + yOffset
        endY = (i * SQ_DIAG) - BOARD_WIDTH + yOffset
        p.draw.line(screen, black, (startX, startY), (endX, endY))
        
    #draw board lines: top left to bottom right
    yOffset = -315
    for i in range(numLines):
        startY = i * SQ_DIAG + yOffset
        endY = (i * SQ_DIAG) + BOARD_WIDTH + yOffset
        p.draw.line(screen, black, (startX, startY), (endX, endY))
    
    #cover everything outside the circle
    radius = BOARD_WIDTH/2
    cover_surf = p.Surface((BOARD_WIDTH,BOARD_HEIGHT))
    cover_surf.set_colorkey((255, 255, 255))
    p.draw.rect(cover_surf, darkgrey, p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT))
    p.draw.circle(cover_surf, (255, 255, 255), (radius, radius), radius)
    clip_rect = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT)
    screen.blit(cover_surf, clip_rect)
    
    
    
"""
Find the closest grid point to the mouse coordinate, via euclidean distance
Source: https://codereview.stackexchange.com/a/28210

@param mouse_point is a tuple screen coordinate ex. (251, 213)
@return the point in rawScreenPoints that is closest to given point
"""
def closest_point(mouse_point):
    dist_sq = np.sum((numpy_screenPoints - mouse_point)**2, axis=1)
    if np.min(dist_sq) > HALF_SQ**2:
        return ()
    return rawScreenPoints[np.argmin(dist_sq)]



"""
Get the image for a given piece
@param pieceNum is an int representing a piece (see constants file)
"""
def getImage(pieceNum):
    if pieceNum == EMPTY or pieceNum == BOUNDARY: #empty is 0 and board boundaries are -1
        return None
    color = 'w' if pieceNum//100==1 else 'r'
    typ = TYPE_STRINGS[pieceNum // 10 % 10]
    return IMAGES[color + "_" + typ]



"""
Draw pieces on the board using current game state
"""
def drawPieces(screen, board):
    #loop over board, if it's a piece then get corresponding screen points and
    #  draw that piece there.
    for i, val in enumerate(board):
        if val != EMPTY and val != BOUNDARY: #not empty square
            img = getImage(val)
            screenLoc = boardCoordsToScreenPoints[coord(i)]
            pieceLoc = (screenLoc[0]-HALF_SQ, screenLoc[1]-HALF_SQ)
            screen.blit(img, p.Rect(pieceLoc[0], pieceLoc[1], SQ_SIZE, SQ_SIZE))

"""
Highlight some point with a circle
"""
def highlightPoint(screen, point):
    if point != (): 
        #color options? (58,90,64) (255,255,130) (75,104,88) (41,47,54) (224,224,224)
        p.draw.circle(screen, (224,224,224), point, HIGHLIGHT_RADIUS, width=HIGHLIGHT_WIDTH)

"""
Highlight board spaces that represent moves a piece could make
"""
def highlightMoves(screen, moves):
    for m in moves:
        pt = boardCoordsToScreenPoints[coord(m.dest_idx)]
        highlightPoint(screen, pt)

"""
When user selects a board point, return what moves can be made by that piece
"""
def getMovesForPiece(pieceNum, validMoves):
    return [m for m in validMoves if m.int_piece == pieceNum]

"""
Choose a move by first selecting a piece and then selecting a board space to move to.
Returns the move with the same piece and destingation point
"""
def constructMove(selectedPiece, startCoord, endCoord, boardState):
#    board = boardState.board
    start_idx = index(startCoord[0], startCoord[1])
    end_idx = index(endCoord[0], endCoord[1])
    destVal = getVal(boardState.board, endCoord[0], endCoord[1]) #board value move lands at
    isPlacement = startCoord[0] >= WHITE_POOL_ROW #placement move if starts in pool
    isCapture = destVal > 0 #capture move if lands on a piece
    return Move(selectedPiece, start_idx, end_idx, destVal, isCapture, isPlacement)

"""
Get the board value at the selected space
"""
def boardValAtSelectedPoint(sel_point, board):
    if sel_point in screenPointsToBoardCoords:
        c = screenPointsToBoardCoords[sel_point]
        return getVal(board, c[0], c[1])
    return BOUNDARY


    
         
if __name__ == "__main__":
    # Profiling stuff
    import cProfile as profile
    profile.run('main()', sort='time')
    # main()
    
    
    