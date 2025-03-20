import pygame
import sys
import pandas as pd

pygame.init()

# ----- Window Settings and Colors -----
WIDTH, HEIGHT = 600, 600
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

FONT = pygame.font.SysFont("Arial", 30)
SMALL_FONT = pygame.font.SysFont("Arial", 24)


# ----- UI Classes -----
class TextInputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = WHITE
        self.text = text
        self.txt_surface = FONT.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the user clicked inside the box
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = FONT.render(self.text, True, BLACK)

    def draw(self, screen):
        # Draw the text and the box
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = FONT.render(text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


# ----- Game Board Sprite -----
class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col, size, x_offset, y_offset):
        super().__init__()
        self.row = row
        self.col = col
        self.size = size
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        self.rect = self.image.get_rect(topleft=(x_offset + col * size, y_offset + row * size))
        self.value = None  # Will be "X" or "O"

    def mark(self, player):
        if self.value is None:
            self.value = player
            text_surface = FONT.render(player, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.size // 2, self.size // 2))
            self.image.blit(text_surface, text_rect)


# ----- Helper Functions for Win Checking -----
def count_sequences(board, player, seq_length):
    """
    Counts the number of contiguous sequences of exactly seq_length for the given player.
    It checks in four directions: right, down, down-right, and up-right.
    """
    count = 0
    rows = len(board)
    cols = len(board[0])
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == player:
                for di, dj in directions:
                    # Only count sequence if this cell is the start (i.e. previous cell is not the same)
                    prev_i, prev_j = i - di, j - dj
                    if 0 <= prev_i < rows and 0 <= prev_j < cols and board[prev_i][prev_j] == player:
                        continue  # Not a starting cell
                    # Count contiguous same-player cells in this direction
                    seq_len = 0
                    x, y = i, j
                    while 0 <= x < rows and 0 <= y < cols and board[x][y] == player:
                        seq_len += 1
                        x += di
                        y += dj
                    if seq_len == seq_length:
                        # Ensure that the sequence is not part of a longer one
                        if 0 <= x < rows and 0 <= y < cols and board[x][y] == player:
                            continue
                        count += 1
    return count


def check_game_winner(cells, board_size, mode):
    """
    Returns "X" or "O" if a winning condition is met based on the game mode,
    otherwise returns None.

    For "3x3": win if there is at least one sequence of 3.
    For "4x4": win if there is at least one 4-in-a-row OR at least two 3-in-a-rows.
    For "5x5": win if there is at least one 5-in-a-row OR two 4-in-a-rows OR three 3-in-a-rows.
    """
    # Build the board as a 2D list.
    board = [[None for _ in range(board_size)] for _ in range(board_size)]
    for cell in cells:
        board[cell.row][cell.col] = cell.value

    for player in ["X", "O"]:
        if mode == "3x3":
            if count_sequences(board, player, 3) >= 1:
                return player
        elif mode == "4x4":
            if count_sequences(board, player, 4) >= 1 or count_sequences(board, player, 3) >= 2:
                return player
        elif mode == "5x5":
            if (count_sequences(board, player, 5) >= 1 or
                    count_sequences(board, player, 4) >= 2 or
                    count_sequences(board, player, 3) >= 3):
                return player
    return None


def check_draw(cells):
    """Returns True if all cells are marked."""
    for cell in cells:
        if cell.value is None:
            return False
    return True


def create_cells(board_origin_x, board_origin_y, cell_size, board_size):
    """Creates and returns a new group of Cell sprites for a board of the given size."""
    cells = pygame.sprite.Group()
    for row in range(board_size):
        for col in range(board_size):
            cell = Cell(row, col, cell_size, board_origin_x, board_origin_y)
            cells.add(cell)
    return cells


# ----- Main Game Function -----
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tic Tac Toe")
    clock = pygame.time.Clock()

    # Define game modes and their board settings.
    modes_settings = {
        "3x3": {"board_size": 3, "cell_size": 100, "origin": (150, 100)},
        "4x4": {"board_size": 4, "cell_size": 80, "origin": (100, 80)},
        "5x5": {"board_size": 5, "cell_size": 70, "origin": (80, 70)}
    }

    # Game States: "name_input", "mode_select", "game", "result"
    state = "name_input"

    # Text input boxes for player names
    player1_box = TextInputBox(200, 150, 200, 40)
    player2_box = TextInputBox(200, 250, 200, 40)
    start_button = Button(250, 350, 100, 50, "Start")

    # Buttons for mode selection (will be shown in "mode_select" state)
    mode3_button = Button(100, 250, 120, 50, "3x3")
    mode4_button = Button(240, 250, 120, 50, "4x4")
    mode5_button = Button(380, 250, 120, 50, "5x5")

    # Button for playing again (on result screen)
    play_again_button = Button(225, 500, 150, 50, "Play Again")

    # Variables to store player names and game settings
    player1_name = ""
    player2_name = ""
    current_turn = "X"  # Player 1 always starts
    game_mode = None  # "3x3", "4x4", or "5x5"
    board_size = None
    cell_size = None
    board_origin = None
    cells = None  # Will hold the board cells (sprites)
    result_message = ""

    # List to record moves (each move is a dictionary: player, row, col)
    moves = []

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ----- Name Input State -----
            if state == "name_input":
                player1_box.handle_event(event)
                player2_box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.is_clicked(event.pos):
                        if player1_box.text.strip() != "" and player2_box.text.strip() != "":
                            player1_name = player1_box.text.strip()
                            player2_name = player2_box.text.strip()
                            state = "mode_select"  # Proceed to choose board mode
                        else:
                            print("Please fill in both names.")

            # ----- Mode Selection State -----
            elif state == "mode_select":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mode3_button.is_clicked(event.pos):
                        game_mode = "3x3"
                    elif mode4_button.is_clicked(event.pos):
                        game_mode = "4x4"
                    elif mode5_button.is_clicked(event.pos):
                        game_mode = "5x5"

                    if game_mode:
                        # Set board settings based on chosen mode.
                        board_size = modes_settings[game_mode]["board_size"]
                        cell_size = modes_settings[game_mode]["cell_size"]
                        board_origin = modes_settings[game_mode]["origin"]
                        # Create the game board.
                        cells = create_cells(board_origin[0], board_origin[1], cell_size, board_size)
                        current_turn = "X"
                        moves = []
                        state = "game"

            # ----- Game State -----
            elif state == "game":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for cell in cells:
                        if cell.rect.collidepoint(pos) and cell.value is None:
                            cell.mark(current_turn)
                            moves.append({"player": current_turn, "row": cell.row, "col": cell.col})
                            # Check for a winner using mode-specific rules.
                            winner = check_game_winner(cells, board_size, game_mode)
                            if winner is not None:
                                if winner == "X":
                                    result_message = f"{player1_name} (X) wins!"
                                else:
                                    result_message = f"{player2_name} (O) wins!"
                                state = "result"
                            elif check_draw(cells):
                                result_message = "It's a draw!"
                                state = "result"
                            else:
                                current_turn = "O" if current_turn == "X" else "X"
                            break

            # ----- Result State -----
            elif state == "result":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button.is_clicked(event.pos):
                        # Go back to mode selection (players can choose a new board mode)
                        state = "mode_select"
                        game_mode = None

        # ----- Drawing the Screens -----
        screen.fill(WHITE)
        if state == "name_input":
            title_surface = FONT.render("Enter Player Names", True, BLACK)
            screen.blit(title_surface, (180, 50))
            label1 = SMALL_FONT.render("Player 1:", True, BLACK)
            screen.blit(label1, (100, 160))
            label2 = SMALL_FONT.render("Player 2:", True, BLACK)
            screen.blit(label2, (100, 260))
            player1_box.draw(screen)
            player2_box.draw(screen)
            start_button.draw(screen)

        elif state == "mode_select":
            title = FONT.render("Select Game Mode", True, BLACK)
            screen.blit(title, (180, 150))
            mode3_button.draw(screen)
            mode4_button.draw(screen)
            mode5_button.draw(screen)

        elif state == "game":
            info_text = f"{player1_name} (X) vs {player2_name} (O) - Turn: {current_turn} - Mode: {game_mode}"
            info_surface = SMALL_FONT.render(info_text, True, BLACK)
            screen.blit(info_surface, (20, 20))
            if cells:
                cells.draw(screen)

        elif state == "result":
            result_surface = FONT.render(result_message, True, BLACK)
            screen.blit(result_surface, (100, 30))
            if cells:
                cells.draw(screen)
            play_again_button.draw(screen)

        pygame.display.flip()

    # At exit, print out the moves using pandas.
    df = pd.DataFrame(moves)
    print("Game Moves:")
    print(df)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
