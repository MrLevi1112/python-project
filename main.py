import pygame
from game_controller import GameController

def main():
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Tic Tac Toe with Mode Selection and AI")
    controller = GameController(screen)
    controller.run()

if __name__ == "__main__":
    main()
