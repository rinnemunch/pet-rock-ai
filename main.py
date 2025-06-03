import pygame
import sys
import requests
import json
import os
import re


def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


def load_rock_data():
    if os.path.exists("rock_data.json"):
        with open("rock_data.json", "r") as file:
            data = json.load(file)
            return (
                data.get("name", "Rocky"),
                data.get("background", "forest"),
                data.get("personality", "Wise"),
                data.get("music_on", True)
            )
    return "Rocky", "forest", "Wise", True


def save_rock_data(name, background, personality, music_on=True):
    with open("rock_data.json", "w") as file:
        json.dump({
            "name": name,
            "background": background,
            "personality": personality,
            "music_on": music_on
        }, file)



def get_rocky_response(mood_input, rock_name="Rocky", personality="Wise"):
    if personality == "Wise":
        tone_prompt = "Speak like a wise old sage. Share one thoughtful sentence or proverb-like insight. Respond in no more than 20 words."
    elif personality == "Funny":
        tone_prompt = "Be playful and make a joke or pun. Respond in one funny or silly sentence. Respond in no more than 20 words."
    elif personality == "Sassy":
        tone_prompt = "Be bold, cheeky, and a little sarcastic. Respond with one sassy comeback or dramatic remark. Respond in no more than 20 words."
    elif personality == "Motivational":
        tone_prompt = "Speak like an energetic coach. Respond with one powerful and uplifting line. Respond in no more than 20 words."
    else:
        tone_prompt = "Speak in a kind and friendly tone. Respond in no more than 20 words."

    prompt = f"You are a pet rock named {rock_name}. The user says they feel '{mood_input}'. {tone_prompt}"

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


if os.path.exists("rock_data.json"):
    rock_name, selected_background, selected_personality, music_on = load_rock_data()
    naming_phase = False

    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/forest_theme.mp3")
    if music_on:
        pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

else:
    rock_name, selected_background, selected_personality = "Rocky", "forest", "Wise"
    naming_phase = True

user_input = ''
input_active = naming_phase

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

input_box_rect = pygame.Rect(40, HEIGHT - 50, WIDTH - 80, 32)

BG_COLOR = (240, 240, 240)
FONT_PATH = "fonts/Roboto.ttf"
FONT = pygame.font.Font(FONT_PATH, 24)

if naming_phase:
    rock_response = ""
else:
    try:
        rock_response = get_rocky_response("lonely", rock_name, selected_personality)
    except Exception as e:
        rock_response = f"Oops! {rock_name or 'Rocky'} is quiet right now. Error: {e}"

clock = pygame.time.Clock()
cursor_visible = True
cursor_timer = 0
running = True

rock_img = pygame.image.load("rock.png").convert_alpha()
rock_img = pygame.transform.scale(rock_img, (200, 200))  # size adjust
rock_rect = rock_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

backgrounds = {
    "desert": pygame.image.load("backgrounds/desert.png").convert(),
    "forest": pygame.image.load("backgrounds/forest.png").convert(),
    "grass": pygame.image.load("backgrounds/grass.png").convert()
}

selected_background = "forest"

background_keys = list(backgrounds.keys())
current_bg_index = background_keys.index(selected_background)

button_rect = pygame.Rect(WIDTH - 360, 20, 160, 40)
button_font = pygame.font.SysFont("arial", 20)

personality_options = ["Wise", "Funny", "Sassy", "Motivational"]
personality_index = personality_options.index(selected_personality)
personality_button_rect = pygame.Rect(WIDTH - 180, 20, 160, 40)

current_scene = "main"

minigame_button_rect = pygame.Rect(WIDTH - 720, 20, 160, 40)
music_button_rect = pygame.Rect(WIDTH - 540, 20, 160, 40)

back_button_rect = pygame.Rect(20, 20, 100, 40)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and input_active:
            if event.key == pygame.K_RETURN:
                if naming_phase:
                    rock_name = user_input.strip() or "Rocky"
                    save_rock_data(rock_name, selected_background, selected_personality, music_on)
                    naming_phase = False

                    try:
                        rock_response = get_rocky_response("lonely", rock_name, selected_personality)
                    except Exception as e:
                        rock_response = f"Oops! {rock_name} is quiet right now. Error: {e}"
                else:
                    try:
                        rock_response = get_rocky_response(user_input, rock_name, selected_personality)
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

            if button_rect.collidepoint(event.pos):
                current_bg_index = (current_bg_index + 1) % len(background_keys)
                selected_background = background_keys[current_bg_index]
                save_rock_data(rock_name, selected_background, selected_personality)

            if personality_button_rect.collidepoint(event.pos):
                personality_index = (personality_index + 1) % len(personality_options)
                selected_personality = personality_options[personality_index]
                save_rock_data(rock_name, selected_background, selected_personality)

            if music_button_rect.collidepoint(event.pos):
                music_on = not music_on
                if music_on:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()
                save_rock_data(rock_name, selected_background, selected_personality, music_on)
            if minigame_button_rect.collidepoint(event.pos):
                current_scene = "minigame"

            if current_scene == "minigame" and back_button_rect.collidepoint(event.pos):
                current_scene = "main"

    if current_scene == "main":
        screen.fill(BG_COLOR)
        scaled_bg = pygame.transform.scale(backgrounds[selected_background], (WIDTH, HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        screen.blit(rock_img, rock_rect)
    elif current_scene == "minigame":
        screen.fill((250, 240, 200))  # distinct background for mini-game
        title_text = button_font.render("Rock-Paper-Scissors!", True, (0, 0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        pygame.draw.rect(screen, (200, 200, 200), back_button_rect)
        pygame.draw.rect(screen, (0, 0, 0), back_button_rect, 2)
        back_text = button_font.render("Back", True, (0, 0, 0))
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)

    if current_scene == "main":
        scaled_bg = pygame.transform.scale(backgrounds[selected_background], (WIDTH, HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        screen.blit(rock_img, rock_rect)

    box_color = (255, 255, 255) if input_active else (230, 230, 230)
    pygame.draw.rect(screen, box_color, input_box_rect)
    pygame.draw.rect(screen, (0, 0, 0), input_box_rect, 2)

    # Render input text inside box
    if user_input:
        input_surface = FONT.render(user_input, True, (0, 0, 0))
    else:
        placeholder = "Type your mood..." if not naming_phase else "Enter your rock's name..."
        input_surface = FONT.render(placeholder, True, (180, 180, 180))
    screen.blit(input_surface, (input_box_rect.x + 10, input_box_rect.y + 2))

    if input_active and cursor_visible:
        cursor_x = input_box_rect.x + 10 + input_surface.get_width() + 2
        cursor_y = input_box_rect.y + (input_box_rect.height - input_surface.get_height()) // 2
        cursor_height = input_surface.get_height()
        pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    response_box_rect = pygame.Rect(40, 80, WIDTH - 80, 100)
    pygame.draw.rect(screen, (255, 255, 255), response_box_rect)
    pygame.draw.rect(screen, (0, 0, 0), response_box_rect, 2)
    pygame.draw.rect(screen, (200, 200, 200), button_rect)
    pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)

    button_text = button_font.render("Change Background", True, (0, 0, 0))
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)

    pygame.draw.rect(screen, (200, 200, 200), personality_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), personality_button_rect, 2)
    personality_text = button_font.render(f"Tone: {selected_personality}", True, (0, 0, 0))
    text_rect = personality_text.get_rect(center=personality_button_rect.center)
    screen.blit(personality_text, text_rect)

    pygame.draw.rect(screen, (200, 200, 200), music_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), music_button_rect, 2)
    music_label = "Music: On" if music_on else "Music: Off"
    music_text = button_font.render(music_label, True, (0, 0, 0))
    music_text_rect = music_text.get_rect(center=music_button_rect.center)
    screen.blit(music_text, music_text_rect)

    pygame.draw.rect(screen, (200, 200, 200), minigame_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), minigame_button_rect, 2)
    minigame_text = button_font.render("Mini Games", True, (0, 0, 0))
    minigame_text_rect = minigame_text.get_rect(center=minigame_button_rect.center)
    screen.blit(minigame_text, minigame_text_rect)

    padding = 10
    if naming_phase:
        render_wrapped_text("What would you like to name your pet rock?", FONT, (0, 0, 0), screen,
                            response_box_rect.x + padding,
                            response_box_rect.y + padding,
                            response_box_rect.width - 2 * padding)
    else:
        clean_response = remove_emojis(rock_response)
        render_wrapped_text(clean_response, FONT, (0, 0, 0), screen,
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
