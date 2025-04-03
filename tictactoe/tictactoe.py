"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # First check is the board is in a terminal state and if so return None or smth
    # Loop through each spot on the board
        # Keep track of how many X's there are and how many O's there are
        # If # of X's is == to # of O's, then it is X's turn
        # If # of O's is less then the number of X's, then it is O's turn
    if terminal(board):
        return None
    x = 0
    o = 0
    for row in board:
        for column in row:
            if column == "X":
                x += 1
            elif column == "O":
                o += 1
    if x == o:
        return "X"
    elif o < x:
        return "O"
    else:
        raise Exception("Board is not properly implemented")


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # If there is an empty spot on the board, return it in a set
    options = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                options.add((i,j))
    return options


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # First, raise error if the action is for a previously filled spot
    if action not in actions(board):
        raise Exception("Spot taken")
    # Deep copies as sets cannot be manipulated
    resulting_board = copy.deepcopy(board)
    row = action[0]
    column = action[1]

    # sets chosen spot equal to the current player's symbol
    resulting_board[row][column] = player(board)
    return resulting_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Potential winning boards include
        # All rows are the same (3)
        # All columns are the same  (3)
        # The 2 diagonals    
    # Checking the rows
    for i in range(3):
        if board[i][0] == board[i][1] and board[i][0] == board[i][2]:
            return valid_winner(board[i][0])

    # Checking the columns
    for i in range(3):
        if board[0][i] == board[1][i] and board[0][i] == board[2][i]:
            return valid_winner(board[0][i])

    # Checking the diagonals
    if board[0][0] == board[1][1] and board [0][0]== board[2][2]:
        return valid_winner(board[0][0])
    elif board[0][2] == board[1][1] and board[0][2] == board[2][0]:
        return valid_winner(board[0][2])
    
    return None

def valid_winner(input):
    if input == "X" or input == "O":
        return input
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) == "X":
        return True
    elif winner(board) == "O":
        return True

    # If there is an empty spot, then the game is not over
    for row in board:
        for column in row:
            if column == None:
                return False
    
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    
    if (player(board) == "X"):
        return max_value(board)[1]
    elif (player(board) == "O"):
        return min_value(board)[1]

def max_value(board):
    if terminal(board):
        return [utility(board), None]
    
    moves = actions(board)
    best_outcome = -2

    for move in moves:
        opp_outcome = min_value(result(board, move))[0]
        if opp_outcome > best_outcome:
            best_outcome = opp_outcome
            best_move = move
    return [best_outcome, best_move]
    
    

def min_value(board):
    if terminal(board):
        return [utility(board), None]
    
    moves = actions(board)
    best_outcome = 2
    
    for move in moves:
        opp_outcome = max_value(result(board, move))[0]
        if opp_outcome < best_outcome:
            best_outcome = opp_outcome
            best_move = move
    return [best_outcome, best_move]         

    
