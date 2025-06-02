import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

BG_COLOR = (240, 240, 240)
FONT = pygame.font.SysFont("arial", 24)

# Placeholder message
rock_response = "Hey there, I'm Rocky! Tell me how you're feeling."

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOR)

    # Message box
    text_surface = FONT.render(rock_response, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
