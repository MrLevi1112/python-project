import pygame
import sys
import datetime
import random
from game_model import GameModel, check_game_winner, check_draw, board_to_2d, minimax
from game_view import GameView
from database import create_connection, execute_query
from question_db import load_geography_questions, get_random_question


class GameController:
    def __init__(self, screen):
        self.screen = screen
        self.model = GameModel()
        self.view = GameView(screen, self.model)
        self.clock = pygame.time.Clock()
        self.questions = load_geography_questions()
        self.model.state = "welcome"

    def run(self):
        running = True
        while running:
            self.clock.tick(30)
            # In single-player mode, if it's AI's turn, perform AI move.
            if self.model.ai_enabled and self.model.state == "game" and self.model.current_turn == "O":
                self.perform_ai_move()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.handle_event(event)
            self.view.draw()
        pygame.quit()
        sys.exit()

    def log_game_result(self):
        # Use correct connection parameters.
        connection = create_connection("localhost", "root", "IdodoBird!1", "tic_tac_toe_db")
        if connection:
            player1 = self.model.player1_name
            player2 = self.model.player2_name
            if "wins" in self.model.result_message:
                winner = self.model.result_message.split(" wins!")[0]
            else:
                winner = "Draw"
            mode = self.model.game_mode
            now = datetime.datetime.now()
            game_date = now.date()
            game_time = now.strftime("%H:%M:%S")
            query = f"""
            INSERT INTO project_results (player1, player2, winner, mode, game_date, game_time)
            VALUES ('{player1}', '{player2}', '{winner}', '{mode}', '{game_date}', '{game_time}')
            """
            execute_query(connection, query)
            connection.close()
            self.model.result_logged = True

    def perform_ai_move(self):
        board = board_to_2d(self.model.cells, self.model.board_size)
        difficulty = self.model.ai_difficulty  # "easy", "medium", or "hard"
        move = None
        available_moves = [(cell.row, cell.col) for cell in self.model.cells if cell.value is None]

        # If board is not 3x3 or difficulty is "easy", choose a random move.
        if self.model.board_size != 3 or difficulty == "easy":
            if available_moves:
                move = random.choice(available_moves)
        elif difficulty == "medium":
            if random.random() < 0.5:
                if available_moves:
                    move = random.choice(available_moves)
            else:
                score, move = minimax(board, 0, True, -float("inf"), float("inf"))
        elif difficulty == "hard":
            score, move = minimax(board, 0, True, -float("inf"), float("inf"))

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

    def handle_event(self, event):
        state = self.model.state

        # Back button handling (applies to all screens except welcome).
        if state != "welcome" and event.type == pygame.MOUSEBUTTONDOWN:
            if self.view.back_button.is_clicked(event.pos):
                if state == "game_type":
                    self.model.state = "welcome"
                elif state == "difficulty_select":
                    self.model.state = "game_type"
                elif state == "name_input":
                    if self.model.ai_enabled:
                        self.model.state = "difficulty_select"
                    else:
                        self.model.state = "game_type"
                elif state == "mode_select":
                    self.model.state = "name_input"
                elif state == "game":
                    self.model.state = "mode_select"
                elif state == "trivia":
                    self.model.state = "game"
                elif state == "result":
                    self.model.state = "mode_select"
                return

        if state == "welcome":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.start_welcome_button.is_clicked(event.pos):
                    self.model.state = "game_type"

        elif state == "game_type":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.single_player_button.is_clicked(event.pos):
                    self.model.ai_enabled = True
                    self.model.state = "difficulty_select"
                elif self.view.two_player_button.is_clicked(event.pos):
                    self.model.ai_enabled = False
                    self.model.state = "name_input"

        elif state == "difficulty_select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.easy_button.is_clicked(event.pos):
                    self.model.ai_difficulty = "easy"
                    self.model.state = "name_input"
                elif self.view.medium_button.is_clicked(event.pos):
                    self.model.ai_difficulty = "medium"
                    self.model.state = "name_input"
                elif self.view.hard_button.is_clicked(event.pos):
                    self.model.ai_difficulty = "hard"
                    self.model.state = "name_input"

        elif state == "name_input":
            self.view.player1_box.handle_event(event)
            if not self.model.ai_enabled:
                self.view.player2_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.view.name_start_button.is_clicked(event.pos):
                    self.model.player1_name = self.view.player1_box.text.strip() or "Player 1"
                    if self.model.ai_enabled:
                        self.model.player2_name = "ChupChik"
                        # In single-player, set board mode to 3x3 and start game immediately.
                        self.model.game_mode = "3x3"
                        self.model.create_board()
                        self.model.state = "game"
                    else:
                        self.model.player2_name = self.view.player2_box.text.strip() or "Player 2"
                        self.model.state = "mode_select"

        elif state == "mode_select":
            if event.type == pygame.MOUSEBUTTONDOWN:
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
                        # In two-player mode on 3x3, trigger trivia; otherwise, mark move immediately.
                        if (not self.model.ai_enabled) and (self.model.game_mode == "3x3"):
                            question = get_random_question(self.questions)
                            self.model.pending_move = (cell.row, cell.col)
                            self.model.current_trivia_question = question
                            self.model.state = "trivia"
                        else:
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
                    self.model.result_logged = False
