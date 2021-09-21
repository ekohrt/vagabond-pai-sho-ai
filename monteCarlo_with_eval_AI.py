# -*- coding: utf-8 -*-
"""
Finished on Sep 20 2021
@author: https://github.com/ekohrt

Monte Carlo Tree Search (MCTS) AI is a game-playing algorithm
that randomly simulates many playthroughs of a game and returns the
move that performs best.

*This is a hybrid approach using both MCTS and an evaluation function.

The other common game-playing algorithm is called "Minimax", which actually
analyzes every combination of possible moves up to a certain depth. 

Minimax doesn't really work for this game because the raw branching factor 
is too high: something like 1500.So analyzing 3 moves ahead is 
1500^3 = 3,375,000,000 (3 billion) positions to analyze. You also need to 
invent a utility function, some way of analyzing a board state to decide 
how good or bad it is.

So MCTS is is.

The idea for combining MCTS with an Evaluation Function came from here: 
    https://www.sciencedirect.com/science/article/pii/S0304397516302717



References:
-Implementation reference: https://medium.com/@quasimik/implementing-monte-carlo-tree-search-in-node-js-5f07595104df
^had to convert this from javascript and modify it heavily

-Why you discard the tree each time: https://stackoverflow.com/questions/47389700/why-does-monte-carlo-tree-search-reset-tree

-Possible memory issues: http://orangehelicopter.com/academic/papers/powley_aiide17.pdf

-MCTS with Evaluation Function: https://www.sciencedirect.com/science/article/pii/S0304397516302717

"""




import math
import time
import random
from constants2 import RED_TEAM

# =============================================================================
# TREE
# =============================================================================

"""
Class representing the Monte Carlo search tree.
"""
class MonteCarlo:
    
    """
    Constructor
    @param game -  the current Game object
    @param UCB1ExploreParam
    """
    def __init__(self, UCB1ExploreParam=2):
        self.UCB1ExploreParam = UCB1ExploreParam
        self.nodes = {} #this is the tree
        
    
    """
    prints the first level of the tree (all moves available from given boardState)
    """
    def printTree(self, boardState):
        boardHash = boardState.hashThis()
        if boardHash in self.nodes:
            rootNode = self.nodes[boardHash]
            for moveHash in rootNode.children:
                data = rootNode.children[moveHash]
                move = data['move']
                n_moves = data['node'].n_moves
                n_wins = data['node'].n_wins
                print(move.toString(), "|", "n_moves:", n_moves, "|", "n_wins:", n_wins)
    
    
    """
    If given state does not exist, create dangling node of that state.
    """
    def makeNode(self, boardState):
        boardHash = boardState.hashThis()
        if boardHash not in self.nodes.keys():
            unexpandedMoves = boardState.getAllMoves_Limited() #shallow-copy all moves from this state
            node = MonteCarloNode(None, None, boardState, unexpandedMoves)
            self.nodes[boardHash] = node
            
 
    
    """
    From given state, repeatedly run MCTS for the allotted time
    build the statistics tree, then return the 'best' move.
    
    4-Phase Algorithm:
    In phase (1), existing information is used to repeatedly choose 
        successive child nodes down to the end of the search tree.
    Next, in phase (2), the search tree is expanded by adding a node.
    Then, in phase (3), a simulation is run to the end to determine the winner.
    Finally, in phase (4), all the nodes in the selected path are updated with 
        new information gained from the simulated game.
        
    @param state - a BoardState to analyze
    @param timeout - float seconds; this is how long to run the calculation for.
    @return - returns a Move object
    """
    def runSearch(self, boardState, timeout):
        reverse_eval = (boardState.turnPlayer == RED_TEAM) #if it's red player, reverse the eval fctn (times -1)
            
        #if you can win the game, do it immediately.
        winMove = boardState.winningMove()
        if winMove != None: 
            return winMove
        
        self.makeNode(boardState)    #makes root of the tree
        end = time.time() + timeout  #time.time() returns float representing elapsed seconds since epoch
        
        iterations = 0
        
        #repeat this for the allowed timeout time
        while (time.time() < end):  
            iterations += 1
            
            #1. Selection: find the next node to look at (unexpanded or leaf, chosen by UCB1 heuristic)
            node = self.select(boardState)
            
            winner = node.boardState.winner()
            if node.isLeaf() == False and winner == -1:   #-1 means no winner yet 
                #2. Expansion: Expand a random unexpanded child node of given node
                node = self.expand(node)
                
                #3. Simulation: Play game to terminal state (randomly), return winner
                #winner = self.simulate(node)
                # winner = self.simulate_better(node)
                utility = self.simulate_better(node, reverse_eval) #TODO
                
            #4. Backpropagation: Update ancestor statistics
            self.backpropagate(node, utility)
            
            #output for debugging
            if iterations % 200 ==0: 
                print(iterations, "simulations")
        
        print("TOTAL SIMULATIONS:", iterations)
        return self.bestMove(boardState)           
            


        
    """
    Get the best move from available statistics.
    --> the "best" move is the one with the most visits. https://ai.stackexchange.com/a/17713
    
    Note that there are different ways to choose the “best” play. 
        The one here is called "robust child" in the literature, 
        choosing the highest n_moves. Another is "max child", which 
        chooses the highest winrate n_wins/n_moves.
    """
    def bestMove(self, boardState):
        # If not all children are expanded, not enough information.
        # aka, you haven't checked all of the available moves at least once
        # this might just mean you have to run the search for longer
        # --> or, if it just takes too long, then maybe change this to pick from best options
        rootNode = self.nodes[boardState.hashThis()]
        if not rootNode.isFullyExpanded():
            raise Exception("Not enough information!! Root not fully expanded! Might need longer runtime.") 
            #instead of raising an exception, maybe pick the best move from the available options?
            #allMoves = node.expandedMoves()

        allMoves = rootNode.allMoves()
        bestMove = None
        maxN = -math.inf
        print("THERE ARE THIS MANY MOVES:", len(allMoves))
        #loop over all moves and return the one with the highest n_moves
        for move in allMoves:
            childNode = rootNode.childNode(move)
            if childNode.n_moves > maxN: 
                bestMove = move
                maxN = childNode.n_moves
        return bestMove
        
    
    
    """
    Get the best n moves from the stats tree
    """
    def bestNMoves(self, boardState):
        #TODO - too lazy, not necessary
        pass
    


    """
    Phase 1, Selection: Select until you find a node not fully expanded OR leaf
    """
    def select(self, boardState):
        node = self.nodes[boardState.hashThis()]
        
        while node.isFullyExpanded() and not node.isLeaf():
            moves = node.allMoves()
            bestMove = None
            bestUCB1 = -math.inf
            for move in moves:
                childUCB1 = node.childNode(move).getUCB1(self.UCB1ExploreParam)
                if childUCB1 > bestUCB1:
                    bestMove = move
                    bestUCB1 = childUCB1
            node = node.childNode(bestMove)
        #return an unexpanded node
        return node

        
    
    """
    Phase 2, Expansion: Expand a random unexpanded child node of given node
    """
    def expand(self, node):
        #pick random move
        move = random.choice( node.unexpandedMoves() )
        
        #expand (i.e. perform the move and get the available moves from the new state)
        childState = node.boardState.nextState(move)
        childUnexpandedMoves = childState.getAllMoves_Limited()
        childNode = node.expand(move, childState, childUnexpandedMoves)
        self.nodes[childState.hashThis()] = childNode
        return childNode


        
    
    
    """
    Phase 3, Simulation: Play game to terminal state (randomly)
    """
    def simulate_random(self, node):
        boardState = node.boardState
        winner = boardState.winner()
        moveCount = 0
        while winner == -1:
            moves = boardState.getAllMoves_Limited()
            if len(moves)==0: break  #a comment in the reference article said to put this here
            move = random.choice(moves)
            boardState = boardState.nextState(move)
            winner = boardState.winner()
            moveCount+=1
            #stop simulation if it goes on too long... like, why look 50 moves deep when humans only think like 5 deep?
            if moveCount > 20: return 0
        print(moveCount)
        return winner

        
    """
    Phase 3, Simulation: Play game to terminal state 
    Takes when possible, but random otherwise. 
    (this is strictly better than pure random, since purely random 
       playthroughs basically never end. And we don't have much time.)
    
    @return winner is 1 if white wins, 2 if red, or 0 if no winner.
    """
    def simulate_better(self, node, reverse_eval):
        boardState = node.boardState
        winner = boardState.winner()
        count = 0
        while winner == -1:
            allMoves = boardState.getAllMoves_Limited()
            if not allMoves: break #if no available moves, break. Idk if this is necessary
            
            #if there's a capture available, take it (for simulation purposes)
            captureMoves = [m for m in allMoves if m.isCapture]
            if captureMoves:
                move = random.choice(captureMoves)
            #otherwise, just pick a random move
            else:
                move = random.choice(allMoves)
            
            #perform the move and check for game over
            boardState = boardState.nextState(move)
            winner = boardState.winner()
            
            #don't simulate past 10 moves... most games don't go past 30 moves total
            count+=1
            if count > 6: 
                # return 0
                break
        #return the evaluation score - but reverse the sign if red player is calculating
        if reverse_eval:
            return -1 * boardState.evaluation()
        else:
            return boardState.evaluation()
    
    """
    Phase 4, Backpropagation: Update ancestor statistics with win/loss data.
    @param node is a new leaf node that you just simulated
    @return nothing; just updates the tree.
    """
    def backpropagate(self, node, utility):
        while node != None:
            node.n_moves += 1
            #Parent's choice
            if node.parent == None: return
            
            #instead of win count, backpropagate the resulting board evaluation
            node.n_wins += utility
                
            #move upward in the tree for next iteration
            node = node.parent

    
    
# =============================================================================
# NODE
# =============================================================================
    
"""
Class representing a node in the search tree.
Source: https://github.com/quasimik/medium-mcts/blob/master/monte-carlo-node.js
"""
class MonteCarloNode:
    
    __slots__ = ["move", "boardState", "n_moves", "n_wins", "parent", "children"]
    
    
    """
    @param parent - the parent MonteCarloNode
    @param move - the Move made from the parent to get to this node
    @param boardState - the BoardState associated with this node
    @param unexpandedMvoes - a list of legal Moves that can be made from this node
    """
    def __init__(self, parent, move, boardState, unexpandedMoves):
        self.move = move
        self.boardState = boardState
        # Stats to keep track of after simulations
        self.n_moves = 0
        self.n_wins = 0
        # Tree stuff
        self.parent = parent
        
        #MonteCarloNode.children is a map from Move hashes to a dict
        #containing (1) the Move object and (2) the associated child node. 
        #It includes the Move object here for convenient recovery of Move objects 
        #from their hashes.
        self.children = {m.hashThis(): { "move": m, "node": None } for m in unexpandedMoves}
        
        
    """
    Get the MonteCarloNode corresponding to the given move.
    
    @param move - The Move leading to the child node.
    @return {MonteCarloNode} The child node corresponding to the Move given.
    """
    def childNode(self, move):
        moveKey = move.hashThis()
        if moveKey not in self.children:
            raise Exception("No such move!") 
        child = self.children[moveKey]
        if (child["node"] == None):
            raise Exception("Child is not expanded!")
        return child["node"]

    
    """
    Expand the specified child move and return the new child node.
    Specifically, it replaces null (unexpanded) nodes in MonteCarloNode.children with real nodes.
    
    Expand the specified child's move and return the new child node.
    Add the node to the array of children nodes.
    Remove the play from the array of unexpanded plays.
    """
    def expand(self, move, childState, unexpandedMoves):
        moveKey = move.hashThis()
        if not moveKey in self.children.keys():
            raise Exception("No such move!")
        childNode = MonteCarloNode(self, move, childState, unexpandedMoves)
        self.children[moveKey] = { "move": move, "node": childNode }
        return childNode
    

    """
    Get all legal Moves from this node.
    @return an array of Moves
    """
    def allMoves(self): 
        return [child["move"] for child in self.children.values()]


    """
    Get all unexpanded legal Moves from this node (search children for "None" nodes).
    @return list of Moves
    """
    def unexpandedMoves(self):
        return [child["move"] for child in self.children.values() if child["node"] == None]


    """
    Get all expanded legal Moves from this node (search children for "non-None" nodes).
    @return ist of Moves
    """
    def expandedMoves(self):
        return [child["move"] for child in self.children.values() if child["node"] != None]


    """
    True if this node is fully expanded. 
    AKA have you visited each child?
    (search children for "None" nodes -> true if none found).
    """
    def isFullyExpanded(self):
        for child in self.children.values():
            if child["node"] == None: return False
        return True

        
    """
    True if this node is terminal in the game tree, 
    - NOT INCLUSIVE of termination due to winning.
    """
    def isLeaf(self):
        return len(self.children) == 0

      
    """
    Get the UCB1 value for this node. (UCB1 is an "upper confidence bound" optimization alg)
    
    The literature just agrees that this is a good equation to balance
    exploration of new nodes/moves with exploitation of promising ones.
    
    @param {double} biasParam - The square of the bias parameter in the UCB1 algorithm, defaults to 2.
    @return {double} The UCB1 value of this node.
    """    
    def getUCB1(self, biasParam):
        return (self.n_wins / self.n_moves) + math.sqrt(biasParam) * math.log(self.parent.n_moves / self.n_moves)
