# === Standard Library ===
import os
import re
import json
import requests

# === Standard Library ===
import os
import re
import json
import requests


# === Text Cleanup ===
def remove_emojis(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


# === Data Persistence ===
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
