# === Standard Library ===
import os
import re
import json
# === Third party Library ===
import requests
import pygame


def draw_button(surface, rect, text, font, bg_color=(200, 200, 200), text_color=(0, 0, 0), border_color=(0, 0, 0)):
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, 2)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


# === Text Cleanup ===
def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


# === Data Persistence ===
def load_rock_data():
    try:
        if os.path.exists("rock_data.json"):
            with open("rock_data.json", "r") as file:
                data = json.load(file)
                return (
                    data.get("name", "Rocky"),
                    data.get("background", "forest"),
                    data.get("personality", "Wise"),
                    data.get("music_on", True),
                    data.get("coins", 0),
                    data.get("bee_unlocked", False),
                    data.get("bat_unlocked", False),
                    data.get("pig_unlocked", False),
                    data.get("fox_unlocked", False)
                )

    except Exception as e:
        print(f"Failed to load rock_data.json: {e}")

    return "Rocky", "forest", "Wise", True, 0, False, False, False, False


def save_rock_data(name, background, personality, music_on=True, coins=0,
                   bee_unlocked=False, bat_unlocked=False, pig_unlocked=False, fox_unlocked=False):
    with open("rock_data.json", "w") as file:
        json.dump({
            "name": name,
            "background": background,
            "personality": personality,
            "music_on": music_on,
            "coins": coins,
            "bee_unlocked": bee_unlocked,
            "bat_unlocked": bat_unlocked,
            "pig_unlocked": pig_unlocked,
            "fox_unlocked": fox_unlocked
        }, file)


# === AI Response ===
def get_rocky_response(mood_input, rock_name="Rocky", personality="Wise"):
    if personality == "Wise":
        tone_prompt = ("Speak like a wise old sage. Share one thoughtful sentence or proverb-like insight. Respond in "
                       "no more than 20 words.")
    elif personality == "Funny":
        tone_prompt = ("Be playful and make a joke or pun. Respond in one funny or silly sentence. Respond in no more "
                       "than 20 words.")
    elif personality == "Sassy":
        tone_prompt = ("Be bold, cheeky, and a little sarcastic. Respond with one sassy comeback or dramatic remark. "
                       "Respond in no more than 20 words.")
    elif personality == "Motivational":
        tone_prompt = ("Speak like an energetic coach. Respond with one powerful and uplifting line. Respond in no "
                       "more than 20 words.")
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


# === Text Wrapping ===
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


# === Input box ===
def draw_input_box(surface, rect, text, font, active, cursor_visible, naming_phase=False):
    box_color = (255, 255, 255) if active else (230, 230, 230)
    pygame.draw.rect(surface, box_color, rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    if text:
        input_surface = font.render(text, True, (0, 0, 0))
    else:
        placeholder = "Enter your rock's name..." if naming_phase else "Type your mood..."
        input_surface = font.render(placeholder, True, (180, 180, 180))

    surface.blit(input_surface, (rect.x + 10, rect.y + 2))

    if active and cursor_visible:
        cursor_x = rect.x + 10 + input_surface.get_width() + 2
        cursor_y = rect.y + (rect.height - input_surface.get_height()) // 2
        cursor_height = input_surface.get_height()
        pygame.draw.line(surface, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)


# === Response box ===
def draw_response_box(surface, rect, font, text, naming_phase=False):
    pygame.draw.rect(surface, (255, 255, 255), rect)
    pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    padding = 10
    if naming_phase:
        display_text = "What would you like to name your pet rock?"
    else:
        display_text = remove_emojis(text)

    render_wrapped_text(display_text, font, (0, 0, 0), surface,
                        rect.x + padding,
                        rect.y + padding,
                        rect.width - 2 * padding)


# === Coin ===
def draw_coin_display(surface, coin_img, font, coin_count, x=20, y=20):
    surface.blit(coin_img, (x, y))
    coin_text = font.render(str(coin_count), True, (0, 0, 0))
    surface.blit(coin_text, (x + 45, y + 5))
