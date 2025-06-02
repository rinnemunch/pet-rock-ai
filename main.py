import pygame
import sys
import requests
import json
import os


def load_rock_name():
    if os.path.exists("rock_data.json"):
        with open("rock_data.json", "r") as file:
            data = json.load(file)
            return data.get("name", "Rocky")
    return None


def save_rock_name(name):
    with open("rock_data.json", "w") as file:
        json.dump({"name": name}, file)


def get_rocky_response(mood_input, rock_name="Rocky"):
    prompt = f"You are a pet rock named {rock_name}. The user says they feel '{mood_input}'. Respond with a comforting quote or fun fact in a kind, friendly tone."

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

rock_name = load_rock_name()
naming_phase = rock_name is None

user_input = ''
input_active = naming_phase

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

input_box_rect = pygame.Rect(40, HEIGHT - 50, WIDTH - 80, 32)

BG_COLOR = (240, 240, 240)
FONT = pygame.font.SysFont("arial", 24)

if naming_phase:
    rock_response = ""
else:
    try:
        rock_response = get_rocky_response("lonely", rock_name)
    except Exception as e:
        rock_response = f"Oops! {rock_name or 'Rocky'} is quiet right now. Error: {e}"

clock = pygame.time.Clock()
cursor_visible = True
cursor_timer = 0
running = True

rock_img = pygame.image.load("rock.png").convert_alpha()
rock_img = pygame.transform.scale(rock_img, (200, 200))  # size adjust
rock_rect = rock_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                if naming_phase:
                    rock_name = user_input.strip() or "Rocky"
                    save_rock_name(rock_name)
                    naming_phase = False
                    try:
                        rock_response = get_rocky_response("lonely", rock_name)
                    except Exception as e:
                        rock_response = f"Oops! {rock_name} is quiet right now. Error: {e}"
                else:
                    try:
                        rock_response = get_rocky_response(user_input, rock_name)
                    except Exception as e:
                        rock_response = f"Oops! {rock_name} is quiet right now. Error: {e}"
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
    screen.blit(rock_img, rock_rect)

    box_color = (255, 255, 255) if input_active else (230, 230, 230)
    pygame.draw.rect(screen, box_color, input_box_rect)
    pygame.draw.rect(screen, (0, 0, 0), input_box_rect, 2)

    # Render input text inside box
    input_surface = FONT.render(user_input, True, (0, 0, 0))
    screen.blit(input_surface, (input_box_rect.x + 10, input_box_rect.y + 5))
    if input_active and cursor_visible:
        cursor_x = input_box_rect.x + 10 + input_surface.get_width() + 2
        cursor_y = input_box_rect.y + (input_box_rect.height - input_surface.get_height()) // 2
        cursor_height = input_surface.get_height()
        pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    response_box_rect = pygame.Rect(40, 40, WIDTH - 80, 180)
    pygame.draw.rect(screen, (255, 255, 255), response_box_rect)
    pygame.draw.rect(screen, (0, 0, 0), response_box_rect, 2)

    padding = 10
    if naming_phase:
        render_wrapped_text("What would you like to name your pet rock?", FONT, (0, 0, 0), screen,
                            response_box_rect.x + padding,
                            response_box_rect.y + padding,
                            response_box_rect.width - 2 * padding)
    else:
        render_wrapped_text(rock_response, FONT, (0, 0, 0), screen,
                            response_box_rect.x + padding,
                            response_box_rect.y + padding,
                            response_box_rect.width - 2 * padding)

    # cursor blink
    cursor_timer += 1
    if cursor_timer % 60 < 30:
        cursor_visible = True
    else:
        cursor_visible = False
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
