import pygame
from game_controller import GameController

def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Tic Tac Toe with Geography Trivia")
    controller = GameController(screen)
    controller.run()

if __name__ == "__main__":
    main()
