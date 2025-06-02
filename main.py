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


def render_wrapped_text(text, font, color, surface, x, y, max_width):
    words = text.split()
    line = ""
    lines = []

    for word in words:
        test_line = f"{line} {word}".strip()
        if font.size(test_line)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = test_line
    lines.append(line)

    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y + i * font.get_height()))


pygame.init()

user_input = ''
input_active = False

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

input_box_rect = pygame.Rect(40, HEIGHT - 50, WIDTH - 80, 32)

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

        if input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    rock_response = get_rocky_response(user_input)
                except Exception as e:
                    rock_response = f"Oops! Rocky is quiet right now. Error: {e}"
                user_input = ''
            elif event.key == pygame.K_BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box_rect.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False

    screen.fill(BG_COLOR)

    box_color = (255, 255, 255) if input_active else (230, 230, 230)
    pygame.draw.rect(screen, box_color, input_box_rect)
    pygame.draw.rect(screen, (0, 0, 0), input_box_rect, 2)

    # Render input text inside box
    input_surface = FONT.render(user_input, True, (0, 0, 0))
    screen.blit(input_surface, (input_box_rect.x + 10, input_box_rect.y + 5))

    render_wrapped_text(rock_response, FONT, (0, 0, 0), screen, 40, 40, WIDTH - 80)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
