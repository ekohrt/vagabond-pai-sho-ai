# Game-Playing AI for Vagabond Pai Sho
A python game where you can play Vagabond Pai Sho against an AI.  
The AI uses monte-carlo tree search (MCTS) with a basic evaluation function.
  
![Preview of the ](preview_image.png?raw=true "Title")
  
The maximum branching factor of Vagabond Pai Sho is enormous: in some positions, almost 1500 moves are possible. So algorithms like Minimax are not feasible, because the game tree is too large to analyze completely; searching just 4 plies deep means 1500^4 = 5,062,500,000,000 (5 trillion) positions. This is the primary motivation for using MCTS.
  
The first step was to reduce the branching factor as much as possible, since most of the possible moves are pointless. Some heuristics were used to cut down the number of possible placement moves, since most pieces can be placed anywhere on the board (245 options). It is possible to reduce the maximum branching factor to around 300, with just 67 opening moves:
- **Wheels**: only place in line with another piece
- **Badgermoles**: only place adjacent to one of your flowers. Also includes some pre-defined spaces in the center that are always available.
- **Chrysanthemums: only place adjacent to enemy Sky Bison, or diagonal to one of your flowers (to block the path to the flower, or allow a badgermole to protect both).
- **Fire Lily**: only place within 5 spaces of either lotus (this is within striking distance), or diagonal to your flowers. Includes some pre-defined spaces around the board.
- **Lotus**: only place adjacent to your badgermole or diagonal to one of your flowers. Includes ~40 pre-defined spaces around the edges of the board.
- **Bison**: normal
- **Dragon**: normal
  
The next step was implementing the monte carlo search tree in python. Note: python is not the best choice for this kind of algorithm because its loops are incredibly slow. But it's the language I knew best, so, yeah. This guide on MCTS implementation in javascript was helpful: https://medium.com/@quasimik/implementing-monte-carlo-tree-search-in-node-js-5f07595104df, though I had to translate it to python.
  
After the vanilla MCTS was made, several optimizations were needed to increase the number of simulated games per second:
- Calculate and store things before the game starts (ex. keep a dict of all adjacent spaces for every space on the board, etc.)
- Replace for-loops with list comprehensions whenever possible
- Use \_\_slots\_\_ to reduce the size of your objects
- The biggest bottleneck is calculating Sky Bison moves
  
Some more optimizations were used to increase the quality of each simulation, so that they carried more meaningful information:
- Instead of randomly choosing moves to simulate a game, always take a piece when possible
- stop the simulation early (6 moves deep is enough), instead of playing out to the end
- Instead of backpropagating just a win or loss, backpropagate a simple board evaluation (like in chess). All pieces were given equal value except the Lotus. This idea was inspired by this paper: https://www.sciencedirect.com/science/article/pii/S0304397516302717.
  
All in all, the AI can pump out ~8000 simulations in 30 seconds (on my machine). It plays sensibly, but far from perfectly.
  
The UI for the game is run on the engine 'pygame'. It's not great but it works.
  
Dependencies: pygame, numpy
  
Images provided by The Garden Gate - SkudPaiSho.com.
