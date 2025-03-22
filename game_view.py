import pygame
import textwrap
from ui_helpers import TextInputBox, Button, BACKGROUND_GRADIENT_START, BACKGROUND_GRADIENT_END, BLACK, FONT, SMALL_FONT


class GameView:
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model

        # Default Back button (for most screens, drawn at top-left).
        self.back_button = Button(10, 10, 80, 40, "Back")

        # Welcome screen: a single Start button.
        self.start_welcome_button = Button(250, 300, 100, 50, "Start")

        # Game mode screen: two buttons.
        self.single_player_button = Button(150, 250, 150, 50, "Single Player")
        self.two_player_button = Button(320, 250, 150, 50, "Two Players")

        # Difficulty selection screen (for Single Player).
        self.easy_button = Button(150, 250, 100, 50, "Easy")
        self.medium_button = Button(250, 250, 100, 50, "Medium")
        self.hard_button = Button(350, 250, 100, 50, "Hard")

        # Name input screen.
        self.player1_box = TextInputBox(200, 150, 200, 40)
        self.player2_box = TextInputBox(200, 210, 200, 40)
        self.name_start_button = Button(250, 280, 100, 50, "Continue")

        # Board mode selection buttons (only for two-player mode).
        self.mode3_button = Button(100, 250, 120, 50, "3x3")
        self.mode4_button = Button(240, 250, 120, 50, "4x4")
        self.mode5_button = Button(380, 250, 120, 50, "5x5")

        self.trivia_buttons = []
        self.play_again_button = Button(225, 500, 150, 50, "Play Again")

    def draw_gradient(self, start_color, end_color):
        height = self.screen.get_height()
        for y in range(height):
            ratio = y / height
            r = start_color[0] + (end_color[0] - start_color[0]) * ratio
            g = start_color[1] + (end_color[1] - start_color[1]) * ratio
            b = start_color[2] + (end_color[2] - start_color[2]) * ratio
            pygame.draw.line(self.screen, (int(r), int(g), int(b)), (0, y), (self.screen.get_width(), y))

    def draw_wrapped_text(self, text, font, color, x, y, max_width):
        """Draw text with wrapping if it exceeds max_width."""
        lines = textwrap.wrap(text, width=40)
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (x, y + i * text_surface.get_height()))

    def draw(self):
        self.draw_gradient(BACKGROUND_GRADIENT_START, BACKGROUND_GRADIENT_END)
        state = self.model.state

        if state == "welcome":
            title = FONT.render("Welcome to Tic Tac Toe", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            self.start_welcome_button.draw(self.screen)

        elif state == "game_type":
            title = FONT.render("Select Game Mode", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            self.single_player_button.draw(self.screen)
            self.two_player_button.draw(self.screen)

        elif state == "difficulty_select":
            title = FONT.render("Select AI Difficulty", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            self.easy_button.draw(self.screen)
            self.medium_button.draw(self.screen)
            self.hard_button.draw(self.screen)

        elif state == "name_input":
            title = FONT.render("Enter Player Names", True, BLACK)
            title_rect = title.get_rect(center=(300, 50))
            self.screen.blit(title, title_rect)
            label1 = SMALL_FONT.render("Player 1:", True, BLACK)
            self.screen.blit(label1, (100, 160))
            self.player1_box.draw(self.screen)
            if not self.model.ai_enabled:
                label2 = SMALL_FONT.render("Player 2:", True, BLACK)
                self.screen.blit(label2, (100, 220))
                self.player2_box.draw(self.screen)
            self.name_start_button.draw(self.screen)

        elif state == "mode_select":
            title = FONT.render("Select Board Mode", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            self.mode3_button.draw(self.screen)
            self.mode4_button.draw(self.screen)
            self.mode5_button.draw(self.screen)

        elif state == "game":
            self.model.cells.draw(self.screen)
            info_text = f"{self.model.player1_name} (X) vs {self.model.player2_name} (O)  Turn: {self.model.current_turn}"
            info = SMALL_FONT.render(info_text, True, BLACK)
            self.screen.blit(info, (20, 20))
            # When inside a game, reposition the back button to the bottom left.
            self.back_button.rect.topleft = (10, 550)
            self.back_button.draw(self.screen)

        elif state == "trivia":
            self.trivia_buttons = []
            if self.model.current_trivia_question:
                q = self.model.current_trivia_question
                self.draw_wrapped_text(q["question"], SMALL_FONT, BLACK, 50, 50, self.screen.get_width() - 100)
                options = q["options"]
                x = 100
                y = 250
                for idx, option in enumerate(options):
                    btn = Button(x, y + idx * 60, 400, 50, option)
                    btn.draw(self.screen)
                    self.trivia_buttons.append((btn, idx))
            # Use default back button position for trivia.
            self.back_button.rect.topleft = (10, 10)
            self.back_button.draw(self.screen)

        elif state == "result":
            big_font = pygame.font.SysFont("Arial", 60)
            res = big_font.render(self.model.result_message, True, BLACK)
            text_rect = res.get_rect(center=(300, 300))
            self.screen.blit(res, text_rect)
            self.play_again_button.draw(self.screen)
            self.back_button.rect.topleft = (10, 10)
            self.back_button.draw(self.screen)

        # For all other screens (that are not "game"), draw back button at default position.
        if state not in ["welcome", "game", "trivia", "result"]:
            self.back_button.rect.topleft = (10, 10)
            self.back_button.draw(self.screen)

        pygame.display.flip()
