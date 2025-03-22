from ui_helpers import create_cells

class GameModel:
    def __init__(self):
        self.state = "welcome"  # Starting state
        self.player1_name = ""
        self.player2_name = ""
        self.player1_color = (255, 0, 0)
        self.player2_color = (0, 0, 255)
        self.ai_enabled = False
        self.ai_difficulty = "easy"  # "easy", "medium", or "hard"
        self.game_mode = None       # "3x3", "4x4", or "5x5"
        self.board_size = None
        self.cell_size = None
        self.board_origin = None
        self.current_turn = "X"
        self.moves = []
        self.cells = None
        self.result_message = ""
        self.current_trivia_question = None
        self.pending_move = None
        self.result_logged = False

    def create_board(self):
        if self.game_mode == "3x3":
            self.board_size = 3
            self.cell_size = 100
            self.board_origin = (150, 100)
        elif self.game_mode == "4x4":
            self.board_size = 4
            self.cell_size = 80
            self.board_origin = (100, 80)
        elif self.game_mode == "5x5":
            self.board_size = 5
            self.cell_size = 70
            self.board_origin = (80, 70)
        self.cells = create_cells(self.board_origin[0], self.board_origin[1], self.cell_size, self.board_size)
        self.current_turn = "X"
        self.moves = []
        self.result_logged = False

def check_draw(cells):
    for cell in cells:
        if cell.value is None:
            return False
    return True

def count_exact_sequences(board, player, L):
    count = 0
    rows = len(board)
    cols = len(board[0])
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for i in range(rows):
        for j in range(cols):
            if board[i][j] != player:
                continue
            for di, dj in directions:
                prev_i, prev_j = i - di, j - dj
                if 0 <= prev_i < rows and 0 <= prev_j < cols and board[prev_i][prev_j] == player:
                    continue
                length = 0
                x, y = i, j
                while 0 <= x < rows and 0 <= y < cols and board[x][y] == player:
                    length += 1
                    x += di
                    y += dj
                if length == L:
                    count += 1
    return count

def check_game_winner(cells, board_size, mode):
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    for cell in cells:
        board[cell.row][cell.col] = cell.value
    for player in ["X", "O"]:
        if mode == "3x3":
            if count_exact_sequences(board, player, 3) >= 1:
                return player
        elif mode == "4x4":
            if count_exact_sequences(board, player, 4) >= 1 or count_exact_sequences(board, player, 3) >= 2:
                return player
        elif mode == "5x5":
            if (count_exact_sequences(board, player, 5) >= 1 or
                count_exact_sequences(board, player, 4) >= 2 or
                count_exact_sequences(board, player, 3) >= 3):
                return player
    return None

def board_to_2d(cells, board_size):
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    for cell in cells:
        board[cell.row][cell.col] = cell.value
    return board

def evaluate_board(board):
    # Simple evaluation for a 3x3 board.
    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    for j in range(3):
        if board[0][j] is not None and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None

def is_draw_board(board):
    for row in board:
        for cell in row:
            if cell is None:
                return False
    return True

def minimax(board, depth, is_maximizing, alpha, beta):
    winner = evaluate_board(board)
    if winner == "O":
        return 10 - depth, None
    elif winner == "X":
        return depth - 10, None
    elif is_draw_board(board):
        return 0, None

    if is_maximizing:
        best_score = -float("inf")
        best_move = None
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] is None:
                    board[i][j] = "O"
                    score, _ = minimax(board, depth + 1, False, alpha, beta)
                    board[i][j] = None
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = float("inf")
        best_move = None
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] is None:
                    board[i][j] = "X"
                    score, _ = minimax(board, depth + 1, True, alpha, beta)
                    board[i][j] = None
                    if score < best_score:
                        best_score = score
                        best_move = (i, j)
                    beta = min(beta, score)
                    if beta <= alpha:
                        break
            if beta <= alpha:
                break
        return best_score, best_move
