# === Standard Library ===
import sys
import os
import threading

# === Third-Party Libraries ===
import pygame
import glob

# === Local Modules ===
from helpers import (
    remove_emojis,
    load_rock_data,
    save_rock_data,
    get_rocky_response,
    render_wrapped_text,
    draw_button,
    draw_input_box,
    draw_response_box,
    draw_coin_display
)

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pet Rock AI")

thinking_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (150, 100))
    for path in sorted(glob.glob("assets/thinking/frame_*.png"))
]

thinking_frame_index = 0
thinking_timer = 0
is_thinking = False

from assets import load_assets

rock_img, rock_rect, backgrounds, coin_img = load_assets()

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
coin_count = 0
input_active = naming_phase

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

selected_background = "forest"

background_keys = list(backgrounds.keys())
current_bg_index = background_keys.index(selected_background)

# === Buttons ===
buttons = {
    "change_bg": {
        "rect": pygame.Rect(WIDTH - 360, 20, 160, 40),
        "label": "Change Background"
    },
    "tone": {
        "rect": pygame.Rect(WIDTH - 180, 20, 160, 40),
        "label": lambda: f"Tone: {selected_personality}"
    },
    "settings": {
        "rect": pygame.Rect(WIDTH - 540, 20, 160, 40),
        "label": "Settings"
    },
    "minigame": {
        "rect": pygame.Rect(WIDTH - 720, 20, 160, 40),
        "label": "Mini Games"
    }
}

button_font = pygame.font.SysFont("arial", 20)

personality_options = ["Wise", "Funny", "Sassy", "Motivational"]
personality_index = personality_options.index(selected_personality)

# Flags
show_settings = False
current_scene = "main"
music_button_pressed = False
name_button_pressed = False
show_name_tag = False
renaming_mode = False
new_name_input = ''
rename_input_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 32)


back_button_rect = pygame.Rect(20, 20, 100, 40)


def handle_response(prompt):
    global rock_response, is_thinking
    try:
        rock_response = get_rocky_response(prompt, rock_name, selected_personality)
    except Exception as e:
        rock_response = f"Oops! {rock_name or 'Rocky'} is quiet right now. Error: {e}"
    is_thinking = False


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
                    prompt = "lonely"
                else:
                    prompt = user_input

                is_thinking = True
                threading.Thread(target=handle_response, args=(prompt,)).start()
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

            if buttons["change_bg"]["rect"].collidepoint(event.pos):
                current_bg_index = (current_bg_index + 1) % len(background_keys)
                selected_background = background_keys[current_bg_index]
                save_rock_data(rock_name, selected_background, selected_personality)

            if buttons["tone"]["rect"].collidepoint(event.pos):
                personality_index = (personality_index + 1) % len(personality_options)
                selected_personality = personality_options[personality_index]
                save_rock_data(rock_name, selected_background, selected_personality)

            if buttons["settings"]["rect"].collidepoint(event.pos):
                show_settings = not show_settings
                if music_on:
                    pygame.mixer.music.play(-1)
                else:
                    pygame.mixer.music.stop()
                save_rock_data(rock_name, selected_background, selected_personality, music_on)

            if buttons["minigame"]["rect"].collidepoint(event.pos):
                current_scene = "minigame"
            if current_scene == "minigame" and back_button_rect.collidepoint(event.pos):
                current_scene = "main"

    if current_scene == "main":
        screen.fill(BG_COLOR)
        scaled_bg = pygame.transform.scale(backgrounds[selected_background], (WIDTH, HEIGHT))
        screen.blit(scaled_bg, (0, 0))
        screen.blit(rock_img, rock_rect)
        if show_name_tag:
            name_surface = button_font.render(rock_name, True, (50, 50, 50))
            name_x = rock_rect.centerx - name_surface.get_width() // 2
            name_y = rock_rect.top - 30
            screen.blit(name_surface, (name_x, name_y))

        if show_settings:
            # popup background
            settings_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
            pygame.draw.rect(screen, (200, 200, 200), settings_rect)
            pygame.draw.rect(screen, (50, 50, 50), settings_rect, 4)
            # Close (X) button
            close_btn_rect = pygame.Rect(settings_rect.right - 30, settings_rect.top + 10, 20, 20)
            pygame.draw.rect(screen, (255, 80, 80), close_btn_rect)
            x_text = button_font.render("X", True, (255, 255, 255))
            screen.blit(x_text, (close_btn_rect.x + 3, close_btn_rect.y - 2))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if close_btn_rect.collidepoint(event.pos):
                    show_settings = False

            # Music toggle button
            music_btn_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 60, 200, 40)
            music_label = "Music: On" if music_on else "Music: Off"
            draw_button(screen, music_btn_rect, music_label, button_font)

            # Name tag toggle button
            name_toggle_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 110, 200, 40)
            name_label = "Show Name: On" if show_name_tag else "Show Name: Off"
            draw_button(screen, name_toggle_rect, name_label, button_font)

            # Change name button
            name_change_btn_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 160, 200, 40)
            draw_button(screen, name_change_btn_rect, "Change Name", button_font)

            if name_change_btn_rect.collidepoint(event.pos):
                renaming_mode = True
                input_active = True

            # Handle click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if name_toggle_rect.collidepoint(event.pos) and not name_button_pressed:
                    show_name_tag = not show_name_tag
                    name_button_pressed = True

            # Detect clicks on music button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if music_btn_rect.collidepoint(event.pos) and not music_button_pressed:
                    music_on = not music_on
                    music_button_pressed = True
                    if music_on:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
                    save_rock_data(rock_name, selected_background, selected_personality, music_on)

            if event.type == pygame.MOUSEBUTTONUP:
                music_button_pressed = False
                name_button_pressed = False

        if is_thinking and thinking_frames:
            thinking_timer += 1
            if thinking_timer % 6 == 0:
                thinking_frame_index = (thinking_frame_index + 1) % len(thinking_frames)

            thinking_img = thinking_frames[thinking_frame_index]
            thinking_x = rock_rect.right - 20  # ADJUST
            thinking_y = rock_rect.top - thinking_img.get_height() + 60  # ADJUST
            screen.blit(thinking_img, (thinking_x, thinking_y))

        # Coin display
        draw_coin_display(screen, coin_img, button_font, coin_count)

    elif current_scene == "minigame":
        screen.fill((250, 240, 200))  # distinct background for mini-game
        title_text = button_font.render("Rock-Paper-Scissors!", True, (0, 0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        draw_button(screen, back_button_rect, "Back", button_font)

    # === Draw Render ===
    for btn in buttons.values():
        label = btn["label"]() if callable(btn["label"]) else btn["label"]
        draw_button(screen, btn["rect"], label, button_font)

    # === Input Box ===
    draw_input_box(screen, input_box_rect, user_input, FONT, input_active, cursor_visible, naming_phase)

    # == Response Box ==
    response_box_rect = pygame.Rect(40, 80, WIDTH - 80, 100)
    draw_response_box(screen, response_box_rect, FONT, rock_response, naming_phase)

    # cursor blink
    cursor_visible = (cursor_timer % 60) < 30
    cursor_timer += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
