# -*- coding: utf-8 -*-
"""
Finished on Sep 20 2021
@author https://github.com/ekohrt

Just some constants for Vagabond Pai Sho.
DO NOT EDIT THESE CONSTANTS
"""

import numpy as np

#Each piece is represented by an int on the board
#DO NOT CHANGE THESE NUMBERS DEAR GOD IT WILL DESTROY EVERYTHING
W_LOTUS     = 110
W_BISON_1   = 120
W_BISON_2   = 121
W_WHEEL_1   = 130
W_WHEEL_2   = 131
W_BADGER_1  = 140
W_BADGER_2  = 141
W_CHRYS_1   = 150
W_CHRYS_2   = 151
W_FIRELILY  = 160
W_DRAGON    = 170

R_LOTUS     = 210
R_BISON_1   = 220
R_BISON_2   = 221
R_WHEEL_1   = 230
R_WHEEL_2   = 231
R_BADGER_1  = 240
R_BADGER_2  = 241
R_CHRYS_1   = 250
R_CHRYS_2   = 251
R_FIRELILY  = 260
R_DRAGON    = 270

EMPTY = 0
BOUNDARY = -1

#Each piece type is represented by an int (this is the 10s place from pNums)
#DO NOT CHANGE THESE NUMBERS IT WILL BREAK THINGS
LOTUS = 1
BISON = 2
WHEEL = 3
BADGER = 4
CHRYS = 5
FIRELILY = 6
DRAGON = 7

#Two players: White (1) and Red (2)
WHITE_TEAM = 1
RED_TEAM = 2
TEAMS = (WHITE_TEAM, RED_TEAM)

#Just some common sets of pieces for convenience
FLOWERS = {LOTUS, CHRYS, FIRELILY}
W_FLOWERS = {W_LOTUS, W_CHRYS_1, W_CHRYS_2, W_FIRELILY}
R_FLOWERS = {R_LOTUS, R_CHRYS_1, R_CHRYS_2, R_FIRELILY}
ALL_FLOWERS = {WHITE_TEAM: W_FLOWERS, RED_TEAM: R_FLOWERS}
ALL_TYPES = {CHRYS, BADGER, BISON, FIRELILY, LOTUS, WHEEL, DRAGON}
W_BISONS = (W_BISON_1, W_BISON_2)
R_BISONS = (R_BISON_1, R_BISON_2)
ALL_BISONS = (W_BISON_1, W_BISON_2, R_BISON_1, R_BISON_2)
ALL_CHRYSANTHEMUMS = {WHITE_TEAM: (W_CHRYS_1, W_CHRYS_2), RED_TEAM: (R_CHRYS_1, R_CHRYS_2)}
ALL_BADGERMOLES = {WHITE_TEAM: (W_BADGER_1, W_BADGER_2), RED_TEAM: (R_BADGER_1, R_BADGER_2)}

#giving each piece a relative value, so you can roughly analyze a board (like in chess)
PIECE_VALUES = {
    W_LOTUS     : 50,
    W_BISON_1   : 5,
    W_BISON_2   : 5,
    W_WHEEL_1   : 5,
    W_WHEEL_2   : 5,
    W_BADGER_1  : 5,
    W_BADGER_2  : 5,
    W_CHRYS_1   : 5,
    W_CHRYS_2   : 5,
    W_FIRELILY  : 5,
    W_DRAGON    : 5,
    
    R_LOTUS     : -50,
    R_BISON_1   : -5,
    R_BISON_2   : -5,
    R_WHEEL_1   : -5,
    R_WHEEL_2   : -5,
    R_BADGER_1  : -5,
    R_BADGER_2  : -5,
    R_CHRYS_1   : -5,
    R_CHRYS_2   : -5,
    R_FIRELILY  : -5,
    R_DRAGON    : -5
}

#strings for each piece number
pNames = {
        W_LOTUS: 'W_Lotus', 
        W_BISON_1: 'W_Bison_1',   W_BISON_2: 'W_Bison_2',
        W_WHEEL_1: 'W_Wheel_1',   W_WHEEL_2: 'W_Wheel_2',
        W_BADGER_1: 'W_Badger_1', W_BADGER_2: 'W_Badger_2',
        W_CHRYS_1: 'W_Chrys_1',   W_CHRYS_2: 'W_Chrys_2',
        W_FIRELILY: 'W_Firelily',
        W_DRAGON: 'W_Dragon',
        
        R_LOTUS: 'R_Lotus', 
        R_BISON_1: 'R_Bison_1',    R_BISON_2: 'R_Bison_2',
        R_WHEEL_1: 'R_Wheel_1',    R_WHEEL_2: 'R_Wheel_2',
        R_BADGER_1: 'R_Badger_1',  R_BADGER_2: 'R_Badger_2',
        R_CHRYS_1: 'R_Chrys_1',    R_CHRYS_2: 'R_Chrys_2',
        R_FIRELILY: 'R_Firelily',
        R_DRAGON: 'R_Dragon'
        }

#number of rows and columns 
BOARD_WIDTH = 17

#temple coordinates (col,row) and indices
TEMPLE_COORDS = {(8,0), (8,16), (0,8), (16,8)}
TEMPLE_INDICES = {8, 136, 152, 280}

#the empty game board. -1 is not a valid space, 0 is an empty space.
#rotate 45deg --> this way (clockwise)
EMPTY_BOARD = np.array([
        #0,  1,  2,  3,    4, 5, 6, 7, 8, 9, 10,11,12,   13, 14, 15, 16 
        -1, -1, -1, -1,    0, 0, 0, 0, 0, 0, 0, 0, 0,    -1, -1, -1, -1,  #0
        -1, -1, -1,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,  -1, -1, -1,  #1
        -1, -1,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0, -1, -1,  #2
        -1,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0, -1,  #3
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #4
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #5
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #6
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #7
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #8
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #9
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #10
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #11
         0,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0,  0,  #12
        -1,  0,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0,  0, -1,  #13
        -1, -1,  0,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,   0, -1, -1,  #14
        -1, -1, -1,  0,    0, 0, 0, 0, 0, 0, 0, 0, 0,    0,  -1, -1, -1,  #15
        -1, -1, -1, -1,    0, 0, 0, 0, 0, 0, 0, 0, 0,    -1, -1, -1, -1,  #16
        #This row is the off-board piece pool for white.
        W_CHRYS_1, W_BISON_1, W_BADGER_1, W_WHEEL_1,    #17
        W_CHRYS_2, W_BISON_2, W_BADGER_2, W_WHEEL_2,
        W_FIRELILY, W_DRAGON, -1,         W_LOTUS,   -1,-1,-1,-1,-1,
        #This row is the off-board piece pool for red.
        R_CHRYS_1, R_BISON_1, R_BADGER_1, R_WHEEL_1,      #18
        R_CHRYS_2, R_BISON_2, R_BADGER_2, R_WHEEL_2, 
        R_FIRELILY, R_DRAGON, -1,         R_LOTUS,   -1,-1,-1,-1,-1])



#Index for the start of white and red unplayed-piece pools
WHITE_POOL = 289
RED_POOL = 306

#row numbers of white and red unplayed-piece pools (for coord system: NOT INDICES)
WHITE_POOL_ROW = 17
RED_POOL_ROW = 18

#indices of spaces not on the board (i.e. boundaries, and the piece pools)
BOUND_INDICES = {0, 1, 2, 3, 13, 14, 15, 16, 17, 18, 19, 31, 32, 33, 34, 35, 49, 50, 51, 67, 221, 237, 238, 239, 253, 254, 255, 256, 257, 269, 270, 271, 272, 273, 274, 275, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322}
BOUND_COORDS = {(0, 0), (0, 1), (0, 2), (0, 3), (0, 13), (0, 14), (0, 15), (0, 16), (1, 0), (1, 1), (1, 2), (1, 14), (1, 15), (1, 16), (2, 0), (2, 1), (2, 15), (2, 16), (3, 0), (3, 16), (13, 0), (13, 16), (14, 0), (14, 1), (14, 15), (14, 16), (15, 0), (15, 1), (15, 2), (15, 14), (15, 15), (15, 16), (16, 0), (16, 1), (16, 2), (16, 3), (16, 13), (16, 14), (16, 15), (16, 16), (17, 0), (17, 1), (17, 2), (17, 3), (17, 4), (17, 5), (17, 6), (17, 7), (17, 8), (17, 9), (17, 10), (17, 11), (17, 12), (17, 13), (17, 14), (17, 15), (17, 16), (18, 0), (18, 1), (18, 2), (18, 3), (18, 4), (18, 5), (18, 6), (18, 7), (18, 8), (18, 9), (18, 10), (18, 11), (18, 12), (18, 13), (18, 14), (18, 15), (18, 16)}

#indices of all spaces on the board (including temples; not including pools.)
BOARD_INDICES = {4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 276, 277, 278, 279, 280, 281, 282, 283, 284}
BOARD_COORDS = {(0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9), (2, 10), (2, 11), (2, 12), (2, 13), (2, 14), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10), (3, 11), (3, 12), (3, 13), (3, 14), (3, 15), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10), (4, 11), (4, 12), (4, 13), (4, 14), (4, 15), (4, 16), (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (5, 12), (5, 13), (5, 14), (5, 15), (5, 16), (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7), (6, 8), (6, 9), (6, 10), (6, 11), (6, 12), (6, 13), (6, 14), (6, 15), (6, 16), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9), (7, 10), (7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8), (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14), (8, 15), (8, 16), (9, 0), (9, 1), (9, 2), (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8), (9, 9), (9, 10), (9, 11), (9, 12), (9, 13), (9, 14), (9, 15), (9, 16), (10, 0), (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9), (10, 10), (10, 11), (10, 12), (10, 13), (10, 14), (10, 15), (10, 16), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4), (11, 5), (11, 6), (11, 7), (11, 8), (11, 9), (11, 10), (11, 11), (11, 12), (11, 13), (11, 14), (11, 15), (11, 16), (12, 0), (12, 1), (12, 2), (12, 3), (12, 4), (12, 5), (12, 6), (12, 7), (12, 8), (12, 9), (12, 10), (12, 11), (12, 12), (12, 13), (12, 14), (12, 15), (12, 16), (13, 1), (13, 2), (13, 3), (13, 4), (13, 5), (13, 6), (13, 7), (13, 8), (13, 9), (13, 10), (13, 11), (13, 12), (13, 13), (13, 14), (13, 15), (14, 2), (14, 3), (14, 4), (14, 5), (14, 6), (14, 7), (14, 8), (14, 9), (14, 10), (14, 11), (14, 12), (14, 13), (14, 14), (15, 3), (15, 4), (15, 5), (15, 6), (15, 7), (15, 8), (15, 9), (15, 10), (15, 11), (15, 12), (15, 13), (16, 4), (16, 5), (16, 6), (16, 7), (16, 8), (16, 9), (16, 10), (16, 11), (16, 12)}

#directions to loop over
ORDINAL_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1)) #represent vertical and horizontal (row,col) changes
DIAGONAL_DIRECTIONS = ((1, 1), (1, -1), (-1, -1), (-1, 1)) #represent diagonal (row,col) changes

#add these constants to an index to get the index above, below, left, or right (careful because )
UP, DOWN, LEFT, RIGHT = -BOARD_WIDTH, BOARD_WIDTH, -1, 1
#same thing but diagonals
UP_L, UP_R, DOWN_L, DOWN_R = UP+LEFT, UP+RIGHT, DOWN+LEFT, DOWN+RIGHT
DIAGS = (UP_L, UP_R, DOWN_L, DOWN_R)

#some predefined common spaces where the AI can place these pieces; helps reduce the branching factor by a lot.
PREDEFINED_FIRELILY_SPACES = {229, 139, 144, 149, 59, 72, 80, 216, 208}
PREDEFINED_LOTUS_SPACES = {258, 4, 6, 7, 135, 9, 10, 137, 12, 138, 139, 263, 144, 268, 20, 149, 150, 151, 276, 25, 153, 278, 279, 281, 30, 282, 284, 36, 169, 42, 170, 48, 52, 186, 59, 66, 68, 204, 84, 220, 222, 229, 102, 236, 240, 118, 119, 246, 252}
PREDEFINED_BADGERMOLE_SPACES = {161, 143, 144, 145, 127}

#indices at the edge of the board: useful for calculating wheel moves
UP_L_EDGES = {4, 5, 6, 7, 8, 9, 10, 11, 12, 136, 20, 153, 36, 170, 52, 187, 68, 204, 85, 102, 119}
UP_R_EDGES = {4, 5, 6, 7, 8, 9, 10, 11, 12, 135, 152, 30, 169, 48, 186, 66, 203, 84, 220, 101, 118}
DOWN_L_EDGES = {258, 136, 276, 277, 278, 279, 280, 281, 153, 282, 283, 284, 170, 187, 68, 204, 85, 222, 102, 240, 119}
DOWN_R_EDGES = {135, 268, 276, 277, 278, 279, 280, 281, 282, 152, 283, 284, 169, 186, 203, 84, 220, 101, 236, 118, 252}
WHEEL_DIRECTIONS = [(UP_L, UP_L_EDGES), (UP_R, UP_R_EDGES), (DOWN_L, DOWN_L_EDGES), (DOWN_R, DOWN_R_EDGES)]



