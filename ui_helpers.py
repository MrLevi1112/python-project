import pygame

pygame.font.init()

BACKGROUND_GRADIENT_START = (135, 206, 235)  # Sky Blue
BACKGROUND_GRADIENT_END = (255, 255, 255)      # White

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (180, 180, 180)
DARK_GRAY = (100, 100, 100)

FONT = pygame.font.SysFont("Verdana", 30)
SMALL_FONT = pygame.font.SysFont("Verdana", 24)

class TextInputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.txt_surface = FONT.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, BLACK)

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=5)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=5)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Button:
    def __init__(self, x, y, w, h, text, font=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font if font is not None else SMALL_FONT
        self.txt_surface = self.font.render(text, True, BLACK)

    def draw(self, screen):
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, self.rect, border_radius=8)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Cell(pygame.sprite.Sprite):
    def __init__(self, row, col, size, x_offset, y_offset):
        super().__init__()
        self.row = row
        self.col = col
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, self.image.get_rect(), 2)
        self.rect = self.image.get_rect(topleft=(x_offset + col * size, y_offset + row * size))
        self.value = None

    def mark(self, player, color):
        if self.value is None:
            self.value = player
            text_surface = FONT.render(player, True, color)
            text_rect = text_surface.get_rect(center=(self.size // 2, self.size // 2))
            self.image.blit(text_surface, text_rect)

def create_cells(x_offset, y_offset, cell_size, board_size):
    cells = pygame.sprite.Group()
    for row in range(board_size):
        for col in range(board_size):
            cell = Cell(row, col, cell_size, x_offset, y_offset)
            cells.add(cell)
    return cells
