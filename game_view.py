import pygame
from ui_helpers import (
    TextInputBox,
    Button,
    BACKGROUND_GRADIENT_START,
    BACKGROUND_GRADIENT_END,
    BLACK,
    FONT,
    SMALL_FONT
)


class GameView:
    def __init__(self, screen, model):
        self.screen = screen
        self.model = model
        self.single_player_button = Button(150, 250, 150, 50, "Single Player")
        self.two_player_button = Button(320, 250, 150, 50, "Two Players")
        self.player1_box = TextInputBox(200, 150, 200, 40)
        self.player2_box = TextInputBox(200, 250, 200, 40)
        self.start_button = Button(250, 350, 100, 50, "Start")
        # Board mode selection buttons.
        self.mode3_button = Button((600 - 120) // 2, 250, 120, 50, "3x3")
        self.mode4_button = Button(240, 250, 120, 50, "4x4")
        self.mode5_button = Button(380, 250, 120, 50, "5x5")
        self.trivia_buttons = []
        self.play_again_button = Button(225, 500, 150, 50, "Play Again")

    def draw_gradient(self, start_color, end_color):
        """Draw a vertical gradient background."""
        height = self.screen.get_height()
        for y in range(height):
            ratio = y / height
            r = start_color[0] + (end_color[0] - start_color[0]) * ratio
            g = start_color[1] + (end_color[1] - start_color[1]) * ratio
            b = start_color[2] + (end_color[2] - start_color[2]) * ratio
            pygame.draw.line(self.screen, (int(r), int(g), int(b)), (0, y), (self.screen.get_width(), y))

    def draw(self):
        # Draw the gradient background.
        self.draw_gradient(BACKGROUND_GRADIENT_START, BACKGROUND_GRADIENT_END)

        state = self.model.state
        if state == "game_type":
            title = FONT.render("Select Game Type", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            self.single_player_button.draw(self.screen)
            self.two_player_button.draw(self.screen)
        elif state == "name_input":
            title = FONT.render("Enter Player Name(s)", True, BLACK)
            title_rect = title.get_rect(center=(300, 50))
            self.screen.blit(title, title_rect)
            label1 = SMALL_FONT.render("Player 1:", True, BLACK)
            self.screen.blit(label1, (100, 160))
            self.player1_box.draw(self.screen)
            if not self.model.ai_enabled:
                label2 = SMALL_FONT.render("Player 2:", True, BLACK)
                self.screen.blit(label2, (100, 260))
                self.player2_box.draw(self.screen)
            else:
                comp_label = SMALL_FONT.render("Player 2: Computer", True, BLACK)
                comp_label_rect = comp_label.get_rect(center=(300, 260))
                self.screen.blit(comp_label, comp_label_rect)
            self.start_button.draw(self.screen)
        elif state == "mode_select":
            title = FONT.render("Select Board Mode", True, BLACK)
            title_rect = title.get_rect(center=(300, 150))
            self.screen.blit(title, title_rect)
            if self.model.ai_enabled:
                self.mode3_button.rect.x = (600 - 120) // 2
                self.mode3_button.draw(self.screen)
            else:
                self.mode3_button.rect.x = 100
                self.mode3_button.draw(self.screen)
                self.mode4_button.draw(self.screen)
                self.mode5_button.draw(self.screen)
        elif state == "game":
            self.model.cells.draw(self.screen)
            info_text = f"{self.model.player1_name} (X) vs {self.model.player2_name} (O)  Turn: {self.model.current_turn}"
            info = SMALL_FONT.render(info_text, True, BLACK)
            self.screen.blit(info, (20, 20))
        elif state == "trivia":
            self.trivia_buttons = []
            if self.model.current_trivia_question:
                q = self.model.current_trivia_question
                q_text = FONT.render(q["question"], True, BLACK)
                q_rect = q_text.get_rect(center=(300, 100))
                self.screen.blit(q_text, q_rect)
                options = q["options"]
                x = 100
                y = 250
                for idx, option in enumerate(options):
                    btn = Button(x, y + idx * 60, 400, 50, option)
                    btn.draw(self.screen)
                    self.trivia_buttons.append((btn, idx))
        elif state == "result":
            big_font = pygame.font.SysFont("Arial", 60)
            res = big_font.render(self.model.result_message, True, BLACK)
            text_rect = res.get_rect(center=(600 // 2, 300))
            self.screen.blit(res, text_rect)
            self.play_again_button.draw(self.screen)
        pygame.display.flip()
