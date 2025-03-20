import pygame
import sys
import datetime
from game_model import (
    GameModel,
    generate_trivia_question_grok,
    check_game_winner,
    check_draw,
    board_to_2d,
    minimax
)
from game_view import GameView
from database import create_connection, execute_query  # Ensure database.py is in your project

class GameController:
    def __init__(self, screen):
        self.screen = screen
        self.model = GameModel()
        self.view = GameView(screen, self.model)
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.handle_event(event)
            # In single-player mode (AI enabled), if it's AI's turn, let it move automatically.
            if self.model.ai_enabled and self.model.state == "game" and self.model.current_turn == "O":
                self.perform_ai_move()
            self.view.draw()
        pygame.quit()
        sys.exit()

    def log_game_result(self):
        """Log the game result to the MySQL database."""
        # Update with your credentials and database name.
        connection = create_connection("localhost", "root", "IdodoBird!1", "tic_tac_toe_db")
        if connection:
            player1 = self.model.player1_name
            player2 = self.model.player2_name
            # Determine winner from the result message.
            if "wins" in self.model.result_message:
                # Expected format: "Name wins!"
                winner = self.model.result_message.split(" wins!")[0]
            else:
                winner = "Draw"
            mode = self.model.game_mode
            now = datetime.datetime.now()
            game_date = now.date()  # YYYY-MM-DD
            game_time = now.strftime("%H:%M:%S")  # 24h format HH:MM:SS
            query = f"""
            INSERT INTO project_results (player1, player2, winner, mode, game_date, game_time)
            VALUES ('{player1}', '{player2}', '{winner}', '{mode}', '{game_date}', '{game_time}')
            """
            execute_query(connection, query)
            connection.close()
            self.model.result_logged = True

    def handle_event(self, event):
        state = self.model.state

        if state == "game_type":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.single_player_button.is_clicked(event.pos):
                    self.model.ai_enabled = True
                    self.model.state = "name_input"
                elif self.view.two_player_button.is_clicked(event.pos):
                    self.model.ai_enabled = False
                    self.model.state = "name_input"

        elif state == "name_input":
            self.view.player1_box.handle_event(event)
            if not self.model.ai_enabled:
                self.view.player2_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.start_button.is_clicked(event.pos):
                    self.model.player1_name = self.view.player1_box.text.strip() or "Player 1"
                    self.model.player2_name = (
                        "Computer" if self.model.ai_enabled
                        else self.view.player2_box.text.strip() or "Player 2"
                    )
                    self.model.state = "mode_select"

        elif state == "mode_select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.model.ai_enabled:
                    # In single-player mode, force game mode to 3x3.
                    self.model.game_mode = "3x3"
                else:
                    if self.view.mode3_button.is_clicked(event.pos):
                        self.model.game_mode = "3x3"
                    elif self.view.mode4_button.is_clicked(event.pos):
                        self.model.game_mode = "4x4"
                    elif self.view.mode5_button.is_clicked(event.pos):
                        self.model.game_mode = "5x5"
                if self.model.game_mode:
                    self.model.create_board()
                    self.model.state = "game"

        elif state == "game":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for cell in self.model.cells:
                    if cell.rect.collidepoint(event.pos) and cell.value is None:
                        # For two-player 3x3 mode, trigger a trivia question.
                        if self.model.game_mode == "3x3" and not self.model.ai_enabled:
                            tq = generate_trivia_question_grok("geography")
                            if tq is None:
                                # Fallback trivia question.
                                tq = {
                                    "question": "What is the capital of France?",
                                    "options": ["Paris", "London", "Berlin", "Rome"],
                                    "answer": 0
                                }
                            self.model.pending_move = (cell.row, cell.col)
                            self.model.current_trivia_question = tq
                            self.model.state = "trivia"
                        else:
                            # For single-player mode (or for non-3x3 boards), place the move immediately.
                            cell.mark(
                                self.model.current_turn,
                                self.model.player1_color if self.model.current_turn == "X" else self.model.player2_color
                            )
                            self.model.moves.append({
                                "player": self.model.current_turn,
                                "row": cell.row,
                                "col": cell.col
                            })
                            winner = check_game_winner(self.model.cells, self.model.board_size, self.model.game_mode)
                            if winner:
                                self.model.result_message = (
                                    f"{self.model.player1_name if winner == 'X' else self.model.player2_name} wins!"
                                )
                                self.model.state = "result"
                                if not self.model.result_logged:
                                    self.log_game_result()
                            elif check_draw(self.model.cells):
                                self.model.result_message = "It's a draw!"
                                self.model.state = "result"
                                if not self.model.result_logged:
                                    self.log_game_result()
                            else:
                                self.model.current_turn = "O" if self.model.current_turn == "X" else "X"
                        break

        elif state == "trivia":
            if event.type == pygame.MOUSEBUTTONDOWN:
                for btn, idx in self.view.trivia_buttons:
                    if btn.is_clicked(event.pos):
                        correct = self.model.current_trivia_question.get("answer")
                        # If the player answers correctly, place his piece.
                        if idx == correct:
                            pending = self.model.pending_move
                            if pending:
                                for cell in self.model.cells:
                                    if cell.row == pending[0] and cell.col == pending[1]:
                                        cell.mark(
                                            self.model.current_turn,
                                            self.model.player1_color if self.model.current_turn == "X" else self.model.player2_color
                                        )
                                        self.model.moves.append({
                                            "player": self.model.current_turn,
                                            "row": cell.row,
                                            "col": cell.col
                                        })
                                        break
                        # If the answer is wrong, no piece is placed.
                        # In either case, switch turn.
                        self.model.current_turn = "O" if self.model.current_turn == "X" else "X"
                        self.model.pending_move = None
                        self.model.current_trivia_question = None
                        winner = check_game_winner(self.model.cells, self.model.board_size, self.model.game_mode)
                        if winner:
                            self.model.result_message = (
                                f"{self.model.player1_name if winner == 'X' else self.model.player2_name} wins!"
                            )
                            self.model.state = "result"
                            if not self.model.result_logged:
                                self.log_game_result()
                        elif check_draw(self.model.cells):
                            self.model.result_message = "It's a draw!"
                            self.model.state = "result"
                            if not self.model.result_logged:
                                self.log_game_result()
                        else:
                            self.model.state = "game"
                        break

        elif state == "result":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.play_again_button.is_clicked(event.pos):
                    self.model.state = "mode_select"
                    self.model.game_mode = None
                    # Reset result_logged for a new game.
                    self.model.result_logged = False

    def perform_ai_move(self):
        board = board_to_2d(self.model.cells, self.model.board_size)
        _, move = minimax(board, 0, True, -float("inf"), float("inf"))
        if move is not None:
            i, j = move
            for cell in self.model.cells:
                if cell.row == i and cell.col == j:
                    cell.mark(
                        self.model.current_turn,
                        self.model.player2_color
                    )
                    self.model.moves.append({
                        "player": self.model.current_turn,
                        "row": cell.row,
                        "col": cell.col
                    })
                    break
            winner = check_game_winner(self.model.cells, self.model.board_size, self.model.game_mode)
            if winner:
                self.model.result_message = (
                    f"{self.model.player1_name if winner == 'X' else self.model.player2_name} wins!"
                )
                self.model.state = "result"
                if not self.model.result_logged:
                    self.log_game_result()
            elif check_draw(self.model.cells):
                self.model.result_message = "It's a draw!"
                self.model.state = "result"
                if not self.model.result_logged:
                    self.log_game_result()
            else:
                self.model.current_turn = "X"
