import pygame
import sys
import requests
import json


def get_rocky_response(mood_input):
    prompt = f"You are a pet rock named Rocky. The user says they feel '{mood_input}'. Respond with a comforting quote or fun fact in a kind, friendly tone."

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt},
        stream=True
    )

    full_reply = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            try:
                json_data = json.loads(data)
                full_reply += json_data.get("response", "")
            except:
                continue
    return full_reply


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

BG_COLOR = (240, 240, 240)
FONT = pygame.font.SysFont("arial", 24)

# Placeholder message
try:
    rock_response = get_rocky_response("lonely")
except Exception as e:
    rock_response = f"Oops! Rocky is quiet right now. Error: {e}"


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
