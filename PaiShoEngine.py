# -*- coding: utf-8 -*-
"""
Finished on Sep 20 2021
@author: https://github.com/ekohrt

An engine for playing a game of Vagabond Pai Sho.

The board is stored as a numpy array of ints representing spaces and pieces.
More information about the board state is stored in a BoardState object.

Rules found here: https://skudpaisho.com/site/games/vagabond-pai-sho/

Note: Python is not the best choice for game-playing AIs, as its loops are
notoriously slow - which is bad because an AI must do a lot of looping 
to analyze large numbers of moves.

But it's easy to read and write and I'm a programming noob so yeah.
I tried my best.

"""

from constants2 import LOTUS, BISON, WHEEL, BADGER, CHRYS, FIRELILY, DRAGON, EMPTY, BOUNDARY, FLOWERS, ALL_CHRYSANTHEMUMS, ALL_TYPES, pNames
from constants2 import BOARD_WIDTH, TEMPLE_INDICES, EMPTY_BOARD, WHITE_TEAM, RED_TEAM, WHITE_POOL
from constants2 import W_LOTUS, W_FIRELILY, R_LOTUS, R_FIRELILY
from constants2 import ORDINAL_DIRECTIONS, DIAGONAL_DIRECTIONS, UP, DOWN, LEFT, RIGHT, UP_L, UP_R, DOWN_L, DOWN_R, WHEEL_DIRECTIONS
from constants2 import BOARD_COORDS, BOARD_INDICES, PREDEFINED_FIRELILY_SPACES, PREDEFINED_LOTUS_SPACES, PREDEFINED_BADGERMOLE_SPACES
from constants2 import PIECE_VALUES
import numpy as np



#*******************************************************************************
# 
# BOARDSTATE CLASS
#
#*******************************************************************************

"""
Class representing a game state.
Contains board array and current player.
Also calculates and stores locations of pieces on creation for faster searching.

Note: stores a copy of the given board parameter, which is expensive, 
so don't be redundant and pass a copy of that board.
"""
class BoardState:
    __slots__ = ["board", "turnPlayer", "pieceLocations", "emptyIndices", 
                 "playerCanCapFlowers", "canCapNonFlowers", "bisonTerritories", 
                 "protectedPieces", "fireLilyRadii", "trappedIndices"]
    
    def __init__(self, board, turnPlayer, oldState=None):
        self.board = np.copy(board)
        self.turnPlayer = turnPlayer
        self.updateAll(oldState)
    
    
    """
    recalculates all the info about the board state (do this when a BoardState is created)
    """
    def updateAll(self, oldState):
        self.update_pieceLocations(oldState)
        self.update_emptyIndices()
        self.update_playerCanCapFlowers()
        self.update_canCapNonFlowers()
        self.update_protectedPieces()
        self.update_fireLilyRadii()
        self.update_trappedIndices()
        self.update_bisonTerritories()
    
    """dicts of pieces on board and in pool - so finding them is easier (and only loop over board once)"""
    def update_pieceLocations(self, oldState):
        #this is suuuuper expensive. so, just copy the previous state's pieceLocations dict
        if oldState:
            self.pieceLocations = oldState.pieceLocations.copy()
        else:
            self.pieceLocations = {val:idx for idx, val in enumerate(self.board) if val > 0}
    
    """set of empty indices <not temples> (so you only loop over the board once to calculate this)"""
    def update_emptyIndices(self):
        #use set difference so you don't hve to loop over entire board
        self.emptyIndices = BOARD_INDICES - TEMPLE_INDICES - set(self.pieceLocations.values())
        #self.emptyIndices = {idx for idx, val in enumerate(self.board[:WHITE_POOL]) if val == EMPTY and idx not in TEMPLE_INDICES} 
        
    """dict of players (colors, teams) who can/can't capture flowers (players can cap. flowers if their lotus is on board)"""
    def update_playerCanCapFlowers(self):
        self.playerCanCapFlowers = {WHITE_TEAM: not self.pieceLocations.get(W_LOTUS, -1) >= WHITE_POOL, 
                                      RED_TEAM: not self.pieceLocations.get(R_LOTUS, -1) >= WHITE_POOL}
    
    """boolean showing whether both players can capture pieces (true when both lotuses are on board)"""
    def update_canCapNonFlowers(self):
        self.canCapNonFlowers = self.playerCanCapFlowers[WHITE_TEAM] and self.playerCanCapFlowers[RED_TEAM]
    
    """set of all pieces on board that are protected (don't want to calculate this hundreds/thousands of times)"""
    def update_protectedPieces(self):
        self.protectedPieces = {pieceNum for pieceNum,idx in self.pieceLocations.items() if idx < WHITE_POOL and isProtected(pieceNum, idx, self.board)}
    
    """dict that stores the sets of spaces within 5 of each fire lily"""
    def update_fireLilyRadii(self):
        self.fireLilyRadii = {WHITE_TEAM: getIndicesWithinN(self.pieceLocations.get(W_FIRELILY, -1), n=5),
                              RED_TEAM: getIndicesWithinN(self.pieceLocations.get(R_FIRELILY, -1), n=5)}
    
    """dict of each player's set of all spaces adjacent to an enemy chrysanthemum"""
    def update_trappedIndices(self):
        self.trappedIndices = {WHITE_TEAM: getTrappedIndices(self, WHITE_TEAM), RED_TEAM: getTrappedIndices(self, RED_TEAM)}
    
    """dict of bison territories for each player"""
    def update_bisonTerritories(self):
        self.bisonTerritories = {WHITE_TEAM: self.getBisonTerritories(WHITE_TEAM), RED_TEAM: self.getBisonTerritories(RED_TEAM)}
    
    
    
    """
    Edits this BoardState in place according to the given move (no new object created)
    Also advances to next player.
    -->use for monteCarlo simulation; faster than making a new BoardState object every move
    
    Check attributes of the move; update certain things depending on the move, 
    and keep others the same -> you don't want to recalc everything each move.
    """
    def performMove(self, move):
        p_typ = move.int_piece // 10 % 10   #type of piece moved
        dest_typ = move.dest_val // 10 % 10 #type of piece at destination
        
        #0) update board
        #start space becomes EMPTY, dest space becomes the piece you moved
        self.board[move.start_idx] = EMPTY
        self.board[move.dest_idx] = move.int_piece
        
        #1) update pieceLocations
        #if dest space is a piece (capture), remove that piece from pieceLocations
        self.pieceLocations.pop(move.dest_val, None)
        #update pieceLocations with new location
        self.pieceLocations[move.int_piece] = move.dest_idx
        
        #2) update emptyIndices
        #remove destination from emptyIndices; also, if not a placement move, add start_idx to empty.
        self.emptyIndices.discard(move.dest_idx)
        if not move.isPlacement and not move.start_idx in TEMPLE_INDICES: 
            self.emptyIndices.add(move.start_idx)
        
        #3,4) update playerCanCapFlowers and canCapNonFlowers
        #only recalculate these if the move is a lotus placement
        if (move.int_piece == W_LOTUS or move.int_piece == R_LOTUS) and move.isPlacement:
            self.update_playerCanCapFlowers()
            self.update_canCapNonFlowers()
            
        #5) update protectedPieces
        #Recalculate every move -->well... only flowers can be protected, and they stay still...
        #recalculate if: any flower placed, moved, or captured; OR any badgermole placed, moved, or captured
        if (p_typ == LOTUS or p_typ == CHRYS or p_typ == FIRELILY or dest_typ == LOTUS or dest_typ == CHRYS or dest_typ == FIRELILY or p_typ == BADGER or dest_typ == BADGER):
            self.update_protectedPieces()
        
        #6) self.fireLilyRadii
        #only recalculate this when a fire lily is placed or captured.
        if (p_typ == FIRELILY) or (dest_typ == FIRELILY):
            self.update_fireLilyRadii()
        
        #7) self.trappedIndices
        #only recalculate this if move places a chrysanthemum or captures one. (shortcut: all chrys moves are placement moves)
        if (p_typ == CHRYS) or (dest_typ == CHRYS):
            self.update_trappedIndices()
        
        #8) self.bisonTerritories
        #only recalculate this when a bison is moved or captured, or a chrys is placed or captured
        if (p_typ == BISON) or (dest_typ == BISON) or (p_typ == CHRYS) or (dest_typ == CHRYS):
            self.update_bisonTerritories()
        
        #switch players
        self.turnPlayer = 1 + self.turnPlayer%2
        
    
    
    """
    Performs the given move on a new BoardState object and returns the new state
    """
    def nextState(self, move):
        newBoardState = BoardState(self.board, self.turnPlayer, oldState=self)  #make new game state object
        newBoardState.performMove(move) #perform the move on it and switch players
        return newBoardState
    
    
    """
    returns just the essential information as a tuple, in case you need to store it
    (dict representing all piece locations (4x smaller than whole board), int representing the turn player)
    """
    def minimize(self):
        return (self.pieceLocations, self.turnPlayer)

    """
    encoodes the board state as a unique string
    """
    def hashThis(self):
        return "".join([str(i) for i in self.board])
        #TODO: maybe look into "Zobrist Hashing": https://en.wikipedia.org/wiki/Zobrist_hashing


    """
    encodes the board state as a string similar to chess's FEN notation
    ->each row of the board is described between '/'s
    ->e12 etc indicates 12 empty spaces in a row
    ->p221 etc indicates that piece
    ->@r or @w indicates the turn player
    ->the last two rows are the white piece pool and then the red pool.
    ->for example: e2p221e1p120e4/e11/e13/e15/e17/e17/e17/e17/e5p121e11/...@r
    """
    def encodeBoardFEN(self):
        #TODO do I even need this?
        pass


    """
    prints the current board in console (for debugging)
    """
    def printBoard(self):
        print(getBoardString(self.board))
    
    
    
    """
    Evaluation function: returns a score for this board position; -1 to 1.
    @param player is the perspective
    """
    def evaluation(self):
        return sum( (PIECE_VALUES[p] for p in self.pieceLocations) ) /100 #normalize to b/w -1 and 1, since all the piece values happen to add to 100
            



    """
    returns a set of spaces controlled by a given team's sky bison
    @param teamnum is 1 for white and 2 for red.
    @return set of tuples (row_int,col_int)
    """
    def getBisonTerritories(self, teamNum):
        territory = set()
        for idx in pieceIndicesOnBoard(self, {teamNum}, {BISON}):
            #if bison on board and not in a temple and not trapped, calc its territory
            if idx not in TEMPLE_INDICES and idx not in self.trappedIndices[teamNum]:
                territory |= getIndicesWithinN(idx, n=6) #add all spaces within 6 steps
                territory.add(idx) #(remember to include bison's own space too)
        return territory
    
    
    
    """
    returns a move that wins the game (captures lotus), if there is one.
    Note: this is expensive, so don't run this repeatedly in a loop.
    """
    def winningMove(self):
        allMoves = self.getAllMoves_Limited()
        return next( (m for m in allMoves if m.dest_val == W_LOTUS or m.dest_val == R_LOTUS), None )
        
    
    
    """
    Returns the winner of the game, if there is one.
    If one player has lost their lotus, the other player wins.
    Could return 1 (player 1), 2 (player 2), 0 (a tie), or -1 (nobody has won yet)
    """
    def winner(self):
        #search the board for lotuses: 
        white_lotus = W_LOTUS in self.pieceLocations
        red_lotus = R_LOTUS in self.pieceLocations
        
        #if both lotuses are present, no winner
        if white_lotus and red_lotus: return -1
        #If one player has lost their lotus, the other player wins. (white = 1, red = 2)
        elif not red_lotus: return 1
        elif not white_lotus: return 2
        #TODO check for stalemate and return 0? seems hard...
        else: return 0



    """
    Returns a list of ALL valid moves for the turn player
    (includes duplicate moves, like when two of the same piece are in the pool)
    """
    def getAllMoves(self):
        allMoves = []
        #loop over pieces on board: calc moves for each, add them all to a list
        for pieceNum in self.pieceLocations:
            #check that space has a piece belonging to turn player
            if pieceNum//100 == self.turnPlayer:
                idx = self.pieceLocations[pieceNum]
                typ = pType(pieceNum)
                #calculate moves based on piece type
                allMoves.extend( MOVE_FUNCTIONS[typ](self, pieceNum, idx) )
        return allMoves
    
     
    
    """
    Returns a limited list of some valid moves for the turn player
    - does not include duplicate moves
    - limits the placement options to just the most common spaces
    *this reduces the branching factor from like 2000 to ~300
    """
    def getAllMoves_Limited(self):
        if self.winner() != -1: return [] #no moves if game is over
        #flags - only look at one of each piece in pool (no duplicate placement moves)
        pool_badgermole = False
        pool_chrys = False
        pool_wheel = False
        pool_bison = False
        
        allMoves = []
        #loop over pieces on board: calc moves for each, add them all to a list
        for pieceNum, idx in self.pieceLocations.items():
            #if piece belongs to turn player
            if pieceNum//100 == self.turnPlayer:
                typ = pieceNum // 10 % 10
                
                #only calculate placement moves for one of each piece type in the pool (avoids duplicate moves)
                if idx >= WHITE_POOL:
                    if typ == CHRYS:
                        if pool_chrys: continue
                        else: pool_chrys = True
                    elif typ == BADGER:
                        if pool_badgermole: continue
                        else: pool_badgermole = True
                    elif typ == WHEEL:
                        if pool_wheel: continue
                        else: pool_wheel = True
                    elif typ == BISON:
                        if pool_bison: continue
                        else: pool_bison = True
    
                #calculate moves based on piece type
                allMoves.extend( MOVE_FUNCTIONS[typ](self, pieceNum, idx, placementMovesFctn=placementMoves_Limited) )
        
        #if you can capture the lotus tile, make it the only option.
        # for m in allMoves:
        #     if (m.dest_val == W_LOTUS) or (m.dest_val == R_LOTUS): 
        #         return [m]
        captureLotus = next( (m for m in allMoves if m.dest_val == W_LOTUS or m.dest_val == R_LOTUS), None )
        if captureLotus: 
            return [captureLotus]
        
        return allMoves



#------------------------------------------------------------------------------
#
# MISC UTILITY FUNCTIONS
#
#------------------------------------------------------------------------------

"""
Returns starting state of the game, with an empty board and player 1's turn.
"""
def startState():
    return BoardState(EMPTY_BOARD, 1)


"""
converts row and col to int index in board's list
"""
def index(row, col):
    return (row*BOARD_WIDTH) + col


"""
converts int index to (row, col) tuple
"""
def coord(idx):
    return (idx//BOARD_WIDTH, idx%BOARD_WIDTH) #(row, col)

def idx_row(idx):
    return idx//BOARD_WIDTH

def idx_col(idx):
    return idx%BOARD_WIDTH
    

"""
Returns true if the given index is a valid space on the board (not in corners or piece pools)
"""
def isOnBoard(idx):
    # idx is in the array (above 0 and not in pool) and not a boundary space
    return (0 <= idx < WHITE_POOL) and EMPTY_BOARD[idx] != BOUNDARY 


"""
Returns true if the given (row, col) coord is a valid space (not in corners or piece pools)
"""
def coordIsOnBoard(row, col):
    return (row,col) in BOARD_COORDS



"""
returns the int value on the board at given coords
@param board is the current board (int[])
"""
def getVal(board, row, col):
    return board[(row*BOARD_WIDTH) + col]




"""
returns a board as a string in nice columns
"""
def getBoardString(board):
    s = ""
    for r in range(BOARD_WIDTH+2):  #number of rows plus the two piece pools at the end
        for c in range(BOARD_WIDTH):
            s += "{:^4}".format(str(board[index(r, c)]))
        s += "\n"
    return s


    
"""
returns a set of all valid adjacent spaces as indexes
"""
def getAdjacentIndices_orig(idx):
    row, col = idx//BOARD_WIDTH, idx%BOARD_WIDTH
    adjs = set()
    #if not in first row, add the space above it (row -1)
    if row > 0 and isOnBoard( idx+UP ): 
        adjs.add( idx+UP )
    #if not in last row, add the space below it (row +1)
    if row < BOARD_WIDTH-1 and isOnBoard( idx+DOWN ): 
        adjs.add( idx+DOWN )
    #if not in first column, add the space left of it (col -1)
    if col > 0 and isOnBoard( idx+LEFT ): 
        adjs.add( idx+LEFT )
    #if not in last column, add the space right of it (col +1)
    if col < BOARD_WIDTH-1 and isOnBoard( idx+RIGHT ): 
        adjs.add( idx+RIGHT )
    return adjs

#cache adjacent indices for every board space
ADJACENT_INDICES = {idx : getAdjacentIndices_orig(idx) for idx in BOARD_INDICES}
def getAdjacentIndices(idx):
    return ADJACENT_INDICES.get(idx, set()) #ADJACENT_INDICES is a dict of sets



"""
returns a set of all valid spaces diagonal from idx as indexes
UP_L, UP_R, DOWN_L, DOWN_R
"""
def getDiagonalIndices_orig(idx):
    row, col = idx//BOARD_WIDTH, idx%BOARD_WIDTH
    diags = set()
    #if not in first row or last column, add the space above right (row -1, col +1)
    if row > 0 and col < BOARD_WIDTH-1 and isOnBoard( idx+UP_R ): 
        diags.add( idx+UP_R )
    #if not in first row or first column, add the space above left (row -1, col -1)
    if row > 0 and col > 0 and isOnBoard( idx+UP_L ): 
        diags.add( idx+UP_L )
    #if not in last row or last column, add the space below right (row +1, col +1)
    if row < BOARD_WIDTH-1 and col < BOARD_WIDTH-1 and isOnBoard( idx+DOWN_R ): 
        diags.add( idx+DOWN_R )
    #if not in last row or first column, add the space below left (row +1, col -1)
    if row < BOARD_WIDTH-1 and col > 0 and isOnBoard( idx+DOWN_L ): 
        diags.add( idx+DOWN_L )
    return diags

#cache diagonal indices for every space on board
DIAGONAL_INDICES = {idx : getDiagonalIndices_orig(idx) for idx in BOARD_INDICES}
def getDiagonalIndices(idx):
    return DIAGONAL_INDICES.get(idx, set()) #DIAGONAL_INDICES is a dict of sets


"""
returns true if the given indices are adjacent (or same)
#WARNING: this does not check if coordinates are valid board spaces.
"""
def areAdjIndices(idx1, idx2):
    row1, col1 = coord(idx1)
    row2, col2 = coord(idx2)
    return (abs(row1-row2)<=1 and col1==col2) or (abs(col1-col2)<=1 and row1==row2)

"""
returns true if the given coords are adjacent on board (or same)
"""
def areAdjCoords(row1, col1, row2, col2):
    return (abs(row1-row2)<=1 and col1==col2) or (abs(col1-col2)<=1 and row1==row2)

"""
Piece Type - returns the int type of the given piece (compare to constants)
@param pieceNum is the int representation of the piece
"""
def pType(pieceNum):
    if pieceNum == BOUNDARY: return BOUNDARY
    return pieceNum // 10 % 10



"""
returns the opposite team of a given piece (1 means white, 2 means red)
"""
def getEnemyTeam(int_piece):
    return (1 + (int_piece//100)%2)




"""
returns set of all spaces within distance n of a given coord (used for firelily and dragon)
Also used for SkyBison territories, but instead of default 5, pass n=6.
@param idx is the location of a firelily or bison on board

Ex. n=3: 
    returns index of each #:
         #
       # # #
     # # # # #
   # # # @ # # #
     # # # # #
       # # #
         #
           (excluding the @). 
"""
def getIndicesWithinN_orig(st_idx, n=5):
    w = BOARD_WIDTH
    return { i for i in BOARD_INDICES if abs(i//w - st_idx//w) + abs(i%w - st_idx%w) <= n }                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

#cache the indices within 5 and 6 of all board spaces (so you don't recalculate it over and over)
INDICES_WITHIN_5 = {idx: getIndicesWithinN_orig(idx, 5) for idx in BOARD_INDICES}
INDICES_WITHIN_6 = {idx: getIndicesWithinN_orig(idx, 6) for idx in BOARD_INDICES}

def getIndicesWithinN(idx, n=5):
    if n == 5:
        return INDICES_WITHIN_5.get(idx, set())
    elif n == 6:
        return INDICES_WITHIN_6.get(idx, set())
    else:
        return getIndicesWithinN_orig(idx, n)



"""
returns the set of all indices in a diagonal line from the given idx
(like how a wheel piece moves)
"""
def getIndicesInLine(idx):
    start_row, start_col = idx//BOARD_WIDTH, idx%BOARD_WIDTH #convert idx to row&col
    indices = set()
    for d in DIAGONAL_DIRECTIONS:
        #keep checking only while the space diagonal from current position is valid.
        row = start_row + d[0]
        col = start_col + d[1]
        while (row, col) in BOARD_COORDS:
            end_idx = (row*BOARD_WIDTH) + col #convert (row,col) to int index
            indices.add(end_idx)
            row += d[0]
            col += d[1]
    return indices


"""
returns true if there is an enemy chrysanthemum adjacent to the given sky bison
- checks all adjacent spaces for an opponent's chrysanthemum.

@param pieceNum
@param idx is a location on board
@param boardState is the current boardState object
"""


def isTrapped(pieceNum, idx, boardState):
    return idx in boardState.trappedIndices[pieceNum//100]


"""
return a set of all 'trapped' indices for a given player
i.e. all spaces where the player's bison would be trapped
"""
def getTrappedIndices(boardState, player):
    #return all indices adjacent to enemy chrysanthemums
    enemyPlayer = 1 + player % 2
    chrys = ALL_CHRYSANTHEMUMS[enemyPlayer] #tuple with 2 items
    chrysIdx1 = boardState.pieceLocations.get(chrys[0], -1)
    chrysIdx2 = boardState.pieceLocations.get(chrys[1], -1)
    return getAdjacentIndices(chrysIdx1) | getAdjacentIndices(chrysIdx2)

"""
returns true if the given piece is protected by an adjacent badgermole

**Needs to be optimized, called like 80 times in each bisonWalk()
**In 30 seconds, this is called more than a million times. So it needs to be OPTIMIZED.
"""
def isProtected(pieceNum, idx, board):
    # if it's not a flower, don't bother checking.
    if pieceNum//10%10 not in FLOWERS or idx >= WHITE_POOL:
        return False
    
    # check adjacent spaces for badgermole of same team
    for i in ADJACENT_INDICES[idx]:
        boardVal = board[i]
        #the constant BADGER is 4: use '4' here so you don't have to look it up
        if (boardVal // 10 % 10 == 4) and (pieceNum//100 == boardVal//100): 
            return True
    return False 
    #this one-liner is slower than the explicit for loop... somehow
    # return any( board[i]//10 == 4 and board[i]//100 == player for i in ADJACENT_INDICES[idx] )    


"""
returns true if piece1 can capture piece2 - assuming that piece1 can reach piece2.

@param piece1 is the turn-player's piece seeking to capture piece2 (int)
@param piece2 is the piece to be captured by piece1 (int).
@param idx2 is the position of piece2 (ints).
@param boardState is the current BoardState instance.
"""
def canCapture(piece1, piece2, idx2, boardState):
    #return false if same team:
    if piece1//100 == piece2//100:
        return False
    
    #if p2 is a flower, check if flowers can be captured, and whether it's protected
    if piece2//10%10 in FLOWERS and boardState.playerCanCapFlowers[piece1//100]:
        return piece2 not in boardState.protectedPieces
        #return not isProtected(piece2, idx2, boardState.board)
        
    #if p2 is a non-flower, you can capture if players can capture non-flowers
    else:
        return boardState.canCapNonFlowers
    


"""
Returns 1 if given 2; returns 2 if given 1
"""
def nextPlayer(player_int):
    return (1 + player_int%2)



"""
Returns set of indices of a player's pieces of a given type(s) that are on the board (not in pool)
@param players_set is a set of players (like {1,2}  or {WHITE_TEAM, RED_TEAM})
@param types_set is a set of piece types (like {BISON, WHEEL} )
"""
def pieceIndicesOnBoard(boardState, players_set, types_set):
    return {boardState.pieceLocations[p] for p in boardState.pieceLocations
            if boardState.pieceLocations[p] < WHITE_POOL
            and p//10%10 in types_set and p//100 in players_set}



#-------------------------------------------------------------------------------
# 
# Calculating moves for each piece type
#
#-------------------------------------------------------------------------------
"""
returns a list of Moves for a piece that has yet to be placed on board 
(aka valid spaces to put that piece)

@param pieceNum is the int representation of the piece
@param idx is the location of the piece (should be in piece pool)
@param board is the current board (int[][])
"""
def placementMoves(boardState, pieceNum, start_idx):
    typ = pieceNum // 10 % 10
    
    #if piece is a bison, return empty temples (bc skybisons must be placed on temples)
    if typ == BISON: 
        return [Move(pieceNum, start_idx, t, EMPTY, isPlacement=True) for t in TEMPLE_INDICES if boardState.board[t] == EMPTY]
        
    #if piece is a Dragon, return empty spaces <5 spaces from firelily
    elif typ == DRAGON:
        #find team's firelily, return all emptyspaces with 5 spaces of it 
        lilyNum = (pieceNum//100)*100+(FIRELILY*10)
        # return [] if firelily not on board
        if lilyNum not in boardState.pieceLocations:
            return []
        # otherwise get all empty spaces within 5 of the lily
        lily_idx = boardState.pieceLocations[lilyNum]
        end_indices = getIndicesWithinN(lily_idx, n=5)
        return [Move(pieceNum, start_idx, end_idx, EMPTY, isPlacement=True) 
                for end_idx in end_indices if boardState.board[end_idx] == EMPTY and end_idx not in TEMPLE_INDICES]
        
    #for non-bison pieces, just return all empty board spaces (non-temples)
    else: 
        return [Move(pieceNum, start_idx, end_idx, EMPTY, isPlacement=True) for end_idx in boardState.emptyIndices]
    
    
    
    

"""
An attempt to limit the number of placement move options, for faster analysis.
Heuristics:
- Badgermoles: adjacent to your flowers, plus some spots in the center = max 21 placement moves. 
- Chrysanthemums: adjacent to enemy bison or diagonal to your lotus/lily = max 16 placement moves.
- FireLily: within 5 spaces of either lotus; or adjacent to your badgermoles; or 9 predefined spaces; = max 137 placement moves. 
- Lotus: adjacent to your badgermoles (8) or diag from your flowers (12) or in one of the 49 pre-defined board spaces = max 69 placement moves 
- Sky Bison: normal placement in temples = 4 placement moves
- Dragon: normal placement within 5 of your fire lily = 60 placement moves
- Wheels: only in line with another piece = ? maybe 150 spaces max?

@param bs is the current BoardState object
@param pieceNum is the piece in question (you're finding this piece's placement moves)
@param start_idx is the starting index of the piece (in pool)
"""
def placementMoves_Limited(boardState, pieceNum, start_idx):  
    #store some variables locally so you don't have to look them up every time
    EMPTY_0 = EMPTY
    TEMPLES = TEMPLE_INDICES
    
    board = boardState.board
    typ = pieceNum // 10 % 10
    player = pieceNum // 100
    enemyPlayer = 1 + player%2
    
    #Skybisons must be placed on empty temples
    if typ == BISON: 
        return [Move(pieceNum, start_idx, t, EMPTY_0, isPlacement=True) for t in TEMPLES if board[t] == EMPTY_0]
    
    #if piece is a Dragon, return empty spaces <5 spaces from firelily
    elif typ == DRAGON:
        # get all empty spaces within 5 of the lily
        end_indices = boardState.fireLilyRadii[player]
        return [Move(pieceNum, start_idx, end_idx, EMPTY_0, isPlacement=True) 
                for end_idx in end_indices if board[end_idx] == EMPTY_0 and end_idx not in TEMPLES]
    
    #the other piece types:
    spaces = set()
    
    #Badgermoles can be placed adjacent to your flowers
    if typ == BADGER:
        #get all spaces adj to your flowers
        for idx in pieceIndicesOnBoard(boardState, {player}, {CHRYS, LOTUS, FIRELILY}):
            spaces |= getAdjacentIndices(idx) #union
        #also add some pre-defined spaces
        spaces |= PREDEFINED_BADGERMOLE_SPACES
        
    #Crysanthemums can be placed 1) adjacent to enemy bison and 2) diagonal to your flowers
    elif typ == CHRYS:
        #get all spaces adjacent to enemy bisons
        for idx in pieceIndicesOnBoard(boardState, {enemyPlayer}, {BISON}):
            spaces |= getAdjacentIndices(idx) #union
        #get all spaces diagonal to your lotus and firelily
        for idx in pieceIndicesOnBoard(boardState, {player}, {LOTUS, FIRELILY}):
            spaces |= getDiagonalIndices(idx)
        
    #Firelilies can be placed 1) at a few pre-defined spaces in the middle, 
    #2) within striking distance of either lotus (5 spaces), or 3) adjacent to badgermoles
    elif typ == FIRELILY:
        #get all spaces within 5 of a lotus
        for idx in pieceIndicesOnBoard(boardState, {WHITE_TEAM, RED_TEAM}, {LOTUS}):
            spaces |= getIndicesWithinN(idx, n=5)
        #get all spaces adjacent to badgermoles
        for idx in pieceIndicesOnBoard(boardState, {player}, {BADGER}):
            spaces |= getAdjacentIndices(idx)
        #add all the pre-defined spaces
        spaces |= PREDEFINED_FIRELILY_SPACES
        
    
        
    #if piece is a Lotus, only place it: 
    #a) next to your badgermoles, or
    #b) diagonal to another of your flowers (so one badgermole can protect both), or
    #c) in one of the pre-defined edge spaces where it's common to place a lotus.
    elif typ == LOTUS:
        #get all spaces adjacent to your badgermoles
        for idx in pieceIndicesOnBoard(boardState, {player}, {BADGER}):
            spaces |= getAdjacentIndices(idx)
        #get all spaces diagonal to your other flowers
        for idx in pieceIndicesOnBoard(boardState, {player}, {FIRELILY, CHRYS}):
            spaces |= getDiagonalIndices(idx)
        #add pre-defined spaces
        spaces |= PREDEFINED_LOTUS_SPACES
        
    
    #if piece is a wheel, only place in line with another piece.
    #(why place it anywhere else? cuts down 245 options a lot, especially early game)
    #so: get all spaces diagonally in line with a piece (either player)
    elif typ == WHEEL:
        for idx in pieceIndicesOnBoard(boardState, {player, enemyPlayer}, ALL_TYPES):
            spaces |= getIndicesInLine(idx)
        
    #shouldn't reach here
    else: 
        raise Exception("HEY, A PROBLEM!! Invalid piece type?")
    
    #return placement moves to all calculated spaces that are empty and not temples
    # return [Move(pieceNum, start_idx, s, EMPTY_0, isPlacement=True) for s in spaces if board[s]==EMPTY_0 and s not in TEMPLES]
    return [Move(pieceNum, start_idx, s, EMPTY_0, isPlacement=True) for s in spaces if s in boardState.emptyIndices]





"""
Helper for calcLotusMoves and calcBadgermoleMoves
- returns a list of non-capture moves to empty adjacent spaces.
"""    
def adjMoves(boardState, pieceNum, start_idx):
    return [Move(pieceNum, start_idx, end_idx, EMPTY) for end_idx in getAdjacentIndices(start_idx) 
            if (end_idx not in TEMPLE_INDICES) and (boardState.board[end_idx] == EMPTY)]
           

"""
returns a list of Moves for a given Lotus piece
@param pieceNum is the int representation of the piece
@param row, col is the location of the piece on board (could also be in piece pool)
@param board is the current board (int[][])
"""
def calcLotusMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    #if lotus hasn't been played yet, return all empty spaces on board
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    #otherwise, it can move 1 space adjacent
    return adjMoves(boardState, pieceNum, start_idx)
    
    
"""
Returns a list of Moves for a given Badgermole piece.
Badgermoles can move to an adjacent space, or if there is a clear line to any flower
    piece (of either team) it can jump to that flower.
Like:
    0000000 F 00000
    0000000 * 00000
    0000000 0 00000
    F*00000 B 000*F
    0000000 0 00000
    0000000 F 00000         
    (where B is the badgermole, 0 is empty space, F is a flower, 
    and * is a space you can jump to)
"""
def calcBadgermoleMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    #if badgermole hasn't been played yet, return all empty spaces on board
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    
    #badgermoles can move to adjacent spaces
    moves = adjMoves(boardState, pieceNum, start_idx)
    
    #badgermoles can also jump to flowers if there is a straight-line path
    board = boardState.board
    start_row, start_col = coord(start_idx)
    for d in ORDINAL_DIRECTIONS:
        #keep checking only while the next space is valid.
        row = start_row + d[0]
        col = start_col + d[1]
        
        while (row, col) in BOARD_COORDS: #while isOnBoard(row,col)
            end_idx = (row*BOARD_WIDTH) + col #convert (row,col) to int index
            boardVal = board[end_idx]
            # If it hits a flower, add prev. space to list. Then stop looking in this direction.
            if boardVal//10%10 in FLOWERS: 
                row -= d[0] #get prev space
                col -= d[1]
                if not areAdjCoords(row, col, start_row, start_col): #only add as move if not adjacent (must be a jump over 2 or more spaces - to avoid duplicate moves)
                    prev_end_idx = index(row, col)
                    moves.append(Move(pieceNum, start_idx, prev_end_idx, board[prev_end_idx], isCapture=False))
                break
            # If it's empty space, add move to list and continue looking in this direction.
            elif end_idx not in TEMPLE_INDICES and boardVal == EMPTY:
                row += d[0]
                col += d[1]
            #if it's anything else then break
            else:
                break
    return moves
    

"""
Returns a list of Moves for a given Wheel piece
Cycles diagonally until you hit something (while loop), checks if you can take the thing, 
    then repeats for other directions.
"""
def calcWheelMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    #if wheel hasn't been played yet, return all empty spaces on board
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    
    #look diagonally in each direction
    moves = []
    for d, edges in WHEEL_DIRECTIONS:
        idx = start_idx
        while idx not in edges:
            #check space up-left of index
            idx += d
            boardVal = boardState.board[idx]
            
            #is it empty? add to moves and keep looping
            if idx in boardState.emptyIndices:
                moves.append(Move(pieceNum, start_idx, idx, boardVal))
                
            #if it's a piece that can be captured, add move and break
            elif canCapture(pieceNum, boardVal, idx, boardState):
                moves.append(Move(pieceNum, start_idx, idx, boardVal, isCapture=True))
                break
            
            #if it can't be captured, stop looping
            else:
                break
    return moves
          

    
    
"""
Returns a list of Moves for a given FireLily piece
"""
def calcFirelilyMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    #if lily hasn't been played yet, return all empty spaces on board
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    #if fire lily is already on board, it cannot move.
    return []
    
    
"""
Returns a list of Moves for a given Chrysanthemum piece
"""
def calcChrysMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    #if chrys hasn't been played yet, return all empty spaces on board
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    #if chrysanthemum is already on board, it cannot move.
    return []
    
    
"""
Returns a list of Moves for a given Dragon piece.
- Dragon cannot move or be placed if firelily is not on board.
- If firelily is on board, dragon can be placed inside a 5-space radius of it.
- When dragon and firelily are on board, dragon can move anywhere within the 5-space radius.
"""
def calcDragonMoves(boardState, pieceNum, start_idx, placementMovesFctn=placementMoves):
    # if dragon is in pool, get placement moves
    if start_idx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, start_idx)
    
    player = pieceNum//100
    
    # if Dragon on board, dragon can move anywhere within 5 spaces of lily
    moves = []
    for end_idx in boardState.fireLilyRadii[player]:
        boardVal = boardState.board[end_idx]
        #move to empty space
        if end_idx in boardState.emptyIndices:
            moves.append( Move(pieceNum, start_idx, end_idx, boardVal) )
        #capture a piece
        elif canCapture(pieceNum, boardVal, end_idx, boardState): 
            moves.append( Move(pieceNum, start_idx, end_idx, boardVal, isCapture=True) )
    
    return moves
    
    
"""
Calculates all moves a SkyBison can make.
This is a breadth-first traversal, adding adjacent spaces to a queue until you run out of steps.
@param startIdx is the starting board index of the bison (int)
@param maxSteps should always be 6 because bison can move a max of 6 spaces
"""
def calcSkyBisonMoves(boardState, pieceNum, startIdx, maxSteps=6, placementMovesFctn=placementMoves):
    #if bison hasn't been played yet, return empty temples
    if startIdx >= WHITE_POOL:
        return placementMovesFctn(boardState, pieceNum, startIdx)
    
    elif isTrapped(pieceNum, startIdx, boardState):
        return []
    
    player = pieceNum//100
    enemyPlayer = 1 + player % 2
    trappedIndices = boardState.trappedIndices[player]
    ADJACENT_INDICES_loc = ADJACENT_INDICES #store global as local
    
    enemy_terr = boardState.bisonTerritories[enemyPlayer]
    offLimits = {startIdx} #a set of indices where the bison cannot end on: enemy territories and its starting space
    queue = [(startIdx, 0)] # spaces to visit next (tuples of (board_idx, num_steps_to_get_there) )
    moves = [] #list of final moves to return
    steps = 0  #up to 6 steps
    visited = set() #indices you have analyzed adjacent tiles for already
    
    #the rest of the spaces:
    while queue:
        cur_idx, steps = queue.pop(0) #pop first item
        visited.add(cur_idx) #mark current idx as visited
        
        #add current space to final list, if it's not off-limits (aka. enemy bison territory)
        if (cur_idx not in offLimits) and (cur_idx not in enemy_terr):
            moves.append( Move(pieceNum, startIdx, cur_idx, EMPTY) )
            offLimits.add(cur_idx) #prevent duplicate moves
            
        #look at adjacent spaces if not trapped, and distance is less than max
        if steps < maxSteps and not (cur_idx in trappedIndices):
            for a in ADJACENT_INDICES_loc[cur_idx]:
                if a not in visited:
                    boardVal = boardState.board[a]
                    #if it's empty, add to queue (so as to look at its adj spaces)
                    # if (boardVal == 0) and (a not in TEMPLE_INDICES):
                    if a in boardState.emptyIndices:
                        queue.append( (a,steps+1) )
                    #If it's a takeable piece, add to finalSpaces as a capture move. (can capture on temples)
                    elif canCapture(pieceNum, boardVal, a, boardState) and (a not in offLimits) and (a not in enemy_terr):
                        moves.append( Move(pieceNum, startIdx, a, boardVal, isCapture=True) )
                        offLimits.add(cur_idx) #prevent duplicate moves
                    #otherwise, it's your own piece, so you can't walk into it. Do nothing.         
    return moves



MOVE_FUNCTIONS = {LOTUS: calcLotusMoves, BISON: calcSkyBisonMoves, 
                      WHEEL: calcWheelMoves, BADGER: calcBadgermoleMoves, 
                      CHRYS: calcChrysMoves, FIRELILY: calcFirelilyMoves, 
                      DRAGON: calcDragonMoves}




#*******************************************************************************
# 
# MOVE CLASS
#
#*******************************************************************************


"""
Class representing a state transition.(aka a "move")
"""
class Move:
    __slots__ = ["int_piece", "start_idx", "dest_idx", "dest_val", "isCapture", "isPlacement"] # saves memory & faster https://stackoverflow.com/questions/472000/usage-of-slots
    def __init__(self, int_piece, start_idx, dest_idx, dest_val, isCapture=False, isPlacement=False):
        self.int_piece = int_piece   #int id of the moving piece
        self.start_idx = start_idx
        self.dest_idx = dest_idx
        self.dest_val = dest_val     #value of the board at destination (empty or a piece num)
        self.isCapture = isCapture
        self.isPlacement = isPlacement
        
    """
    Overriding the built-in equals method (for comparisons using the == operator and such)
    """
    def __eq__(self, other):
        return (isinstance(other, Move) and #must both be Move objects
                    ( (self.int_piece == other.int_piece and self.start_idx == other.start_idx
                    and self.dest_idx == other.dest_idx and self.dest_val == other.dest_val) ) )
    
    """
    Give a descriptor for the move - NOT FOR USE AS HASH.
    """
    def toString(self):
        s = pNames[self.int_piece]
        if self.isPlacement:
            s += " p " + str(self.dest_idx)
        else: #movement
            if self.isCapture:
                s += " x " + pNames[self.dest_val]
            else:
                s += " m " + str(self.dest_idx)
        return s

    """
    Returns a unique string identifier for this move -> used as dict keys, etc.
    -->just concatenates together the piece to move, the start space, and end space.
    -->use the toString if you want a readable description
    """
    def hashThis(self):
        return "".join([str(self.int_piece), str(self.start_idx), str(self.dest_idx)]) 



