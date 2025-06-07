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
# == Mini Games Icon ==
mini_games_icon = pygame.image.load("assets/ui/mini_games_icon.png").convert_alpha()
mini_games_icon = pygame.transform.scale(mini_games_icon, (40, 40))  # adjust size as needed

# == Thinking emote ==
thinking_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (150, 100))
    for path in sorted(glob.glob("assets/thinking/frame_*.png"))
]
# == Happy emote ==
happy_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (125, 125))  # Size of the bubble
    for path in sorted(glob.glob("assets/emotes/happy/frame_*.png"))
]
# == Sleep emote ==
sleep_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (125, 125))
    for path in sorted(glob.glob("assets/emotes/sleep/frame_*.png"))
]
# == Bee Pet Frames ==
bee_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (60, 60))
    for path in sorted(glob.glob("assets/pets/bee/frame_*.png"))
]
# == Bat Pet Frames ==
bat_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (60, 60))
    for path in sorted(glob.glob("assets/pets/bat/frame_*.png"))
]
# == Pig Pet Frames ==
pig_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (120, 120))
    for path in sorted(glob.glob("assets/pets/pig/frame_*.png"))
]
# == Fox Frames ==
fox_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (80, 80))
    for path in sorted(glob.glob("assets/pets/fox/frame_*.png"))
]
# == Troll Frames ==
troll_frames = [
    pygame.transform.scale(pygame.image.load(path).convert_alpha(), (120, 120))
    for path in sorted(glob.glob("assets/pets/troll/frame_*.png"))
]
# == Pet Timers ==
bat_index = 0
bat_timer = 0

bee_index = 0
bee_timer = 0

pig_index = 0
pig_timer = 0

fox_index = 0
fox_timer = 0

troll_timer = 0
troll_index = 0

# === rps icons ===
rps_icons = {
    "rock": pygame.image.load("assets/rps/rock.png").convert_alpha(),
    "paper": pygame.image.load("assets/rps/paper.png").convert_alpha(),
    "scissors": pygame.image.load("assets/rps/scissors.png").convert_alpha()
}

for key in rps_icons:
    rps_icons[key] = pygame.transform.scale(rps_icons[key], (64, 64))

# Unlockable background item
unlockable_bgs = ["beach", "mountains", "city", "night"]
bg_unlocks = {bg: False for bg in unlockable_bgs}

thinking_frame_index = 0
thinking_timer = 0
is_thinking = False
typed_text = ""
typing_timer = 0
char_index = 0
typing_speed = 2  # Adjustable remember lower is faster
show_happy_emote = False
happy_emote_index = 0
happy_emote_timer = 0

from assets import load_assets

rock_img, rock_rect, backgrounds, coin_img = load_assets()
gear_icon = pygame.image.load("assets/ui/gear.png").convert_alpha()
gear_icon = pygame.transform.scale(gear_icon, (40, 40))
gear_rect = pygame.Rect(20, 20, 40, 40)
sombrero_img = pygame.image.load("assets/clothes/sombrero.png").convert_alpha()
sombrero_img = pygame.transform.scale(sombrero_img, (100, 60))  # Adjust size as needed


if os.path.exists("rock_data.json"):
    rock_name, selected_background, selected_personality, music_on, coin_count, bee_unlocked, bat_unlocked, pig_unlocked, fox_unlocked, troll_unlocked = load_rock_data()
    naming_phase = False

    pygame.mixer.init()
    pygame.mixer.music.load("assets/music/forest_theme.mp3")
    if music_on:
        pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

else:
    rock_name = "Rocky"
    selected_background = "forest"
    selected_personality = "Wise"
    music_on = True
    coin_count = 0
    bee_unlocked = False
    bat_unlocked = False
    naming_phase = True
    pig_unlocked = False

user_input = ''
input_active = naming_phase

input_box_rect = pygame.Rect(40, HEIGHT - 50, WIDTH - 80, 32)

BG_COLOR = (240, 240, 240)
FONT_PATH = "fonts/Roboto.ttf"
FONT = pygame.font.Font(FONT_PATH, 24)

if naming_phase:
    rock_response = ""
else:
    try:
        rock_response = get_rocky_response("I'm gone and now I'm back.", rock_name, selected_personality)
    except Exception as e:
        rock_response = f"Oops! {rock_name or 'Rocky'} is quiet right now. Error: {e}"

clock = pygame.time.Clock()
cursor_visible = True
cursor_timer = 0
running = True

# === Sleep Logic ===
last_interaction_time = pygame.time.get_ticks()
in_sleep_mode = False
sleep_index = 0
sleep_timer = 0

selected_background = "forest"

background_keys = list(backgrounds.keys())
current_bg_index = background_keys.index(selected_background)

# === Buttons ===
buttons = {
    "change_bg": {
        "rect": pygame.Rect(WIDTH - 360, 20, 160, 40),
        "label": "Change Background"
    },
    "minigame": {
        "rect": pygame.Rect(WIDTH - 720, 20, 160, 40),
        "label": "Mini Games"
    },
    "store": {
        "rect": pygame.Rect(WIDTH - 540, 20, 160, 40),
        "label": "Store"
    }
}

# === RPS Mini-Game Buttons ===
rps_buttons = {
    "rock": pygame.Rect(150, 200, 120, 40),
    "paper": pygame.Rect(340, 200, 120, 40),
    "scissors": pygame.Rect(530, 200, 120, 40)
}
rps_choices = ["rock", "paper", "scissors"]
rps_result = ""

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
rename_input = ''
rename_input_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 80, 200, 32)
rename_input_active = False
rename_cursor_visible = True
rename_cursor_timer = 0
tone_button_pressed = False
bee_unlocked = False
fox_unlocked = False
troll_unlocked = False
active_pet = None
sombrero_unlocked = False
wearing_sombrero = False

# === Background purchase ===
bg_unlock_cost = 25
# === RPS Cooldown ===
rps_cooldown = False
rps_cooldown_timer = 0
# === Cooldown Bar Setup ===
cooldown_bar_rect = pygame.Rect(WIDTH // 2 - 50, 350, 100, 10)
cooldown_duration = 2000

back_button_rect = pygame.Rect(20, 20, 100, 40)


def handle_response(prompt):
    global rock_response, is_thinking, typed_text, char_index, typing_timer
    try:
        rock_response = get_rocky_response(prompt, rock_name, selected_personality)
    except Exception as e:
        rock_response = f"Oops! {rock_name or 'Rocky'} is quiet right now. Error: {e}"
    is_thinking = False
    typed_text = ""
    char_index = 0
    typing_timer = 0


# === MAIN LOOP ===
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # === Clothing Store Clicks ===
            if current_scene == "clothing_store":
                if back_button_rect.collidepoint(event.pos):
                    current_scene = "store"

            # === Pet Store Clicks ===
            if current_scene == "pet_store":
                if back_button_rect.collidepoint(event.pos):
                    current_scene = "store"

                if bee_card_rect.collidepoint(event.pos):
                    if not bee_unlocked and coin_count >= 50:
                        bee_unlocked = True
                        coin_count -= 50
                    if bee_unlocked:
                        active_pet = "bee"

                if bat_card_rect.collidepoint(event.pos):
                    if not bat_unlocked and coin_count >= 50:
                        bat_unlocked = True
                        coin_count -= 50
                    if bat_unlocked:
                        active_pet = "bat"

                if pig_card_rect.collidepoint(event.pos):
                    if not pig_unlocked and coin_count >= 50:
                        pig_unlocked = True
                        coin_count -= 50
                    if pig_unlocked:
                        active_pet = "pig"

                if fox_card_rect.collidepoint(event.pos):
                    if not fox_unlocked and coin_count >= 50:
                        fox_unlocked = True
                        coin_count -= 50
                    active_pet = "fox"

                if troll_card_rect.collidepoint(event.pos):
                    if not troll_unlocked and coin_count >= 50:
                        troll_unlocked = True
                        coin_count -= 50
                    active_pet = "troll"

        if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
            last_interaction_time = pygame.time.get_ticks()

        if event.type == pygame.KEYDOWN and input_active:
            if naming_phase or renaming_mode:
                if event.key == pygame.K_RETURN:
                    rock_name = user_input.strip() or "Rocky"
                    save_rock_data(rock_name, selected_background, selected_personality, music_on)
                    if naming_phase:
                        naming_phase = False
                        is_thinking = True
                        threading.Thread(target=handle_response, args=("lonely",)).start()
                    if renaming_mode:
                        renaming_mode = False
                    user_input = ''
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode
            else:
                if event.key == pygame.K_RETURN:
                    prompt = user_input
                    is_thinking = True
                    threading.Thread(target=handle_response, args=(prompt,)).start()
                    user_input = ''
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                else:
                    user_input += event.unicode

        if pygame.time.get_ticks() - last_interaction_time > 30000:  # seconds
            in_sleep_mode = True

        if rps_cooldown and pygame.time.get_ticks() - rps_cooldown_timer > 2000:  # 2 seconds
            rps_cooldown = False

        else:
            in_sleep_mode = False  #TESTING THE ZZZ
            sleep_index = 0
            sleep_timer = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box_rect.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False

            if gear_rect.collidepoint(event.pos):
                show_settings = not show_settings

            # === Happy Emote MouseDown ===
            if rock_rect.collidepoint(event.pos) and not is_thinking:
                show_happy_emote = True
                happy_emote_index = 0
                happy_emote_timer = 0

            # === Change Background ===
            if buttons["change_bg"]["rect"].collidepoint(event.pos):
                current_bg_index = (current_bg_index + 1) % len(background_keys)
                selected_background = background_keys[current_bg_index]
                save_rock_data(rock_name, selected_background, selected_personality, music_on)
            # === Store ===
            if buttons["store"]["rect"].collidepoint(event.pos):
                current_scene = "store"

            if buttons["minigame"]["rect"].collidepoint(event.pos):
                current_scene = "minigame"
            if current_scene == "minigame" and back_button_rect.collidepoint(event.pos):
                current_scene = "main"
            if current_scene == "store" and back_button_rect.collidepoint(event.pos):
                current_scene = "main"

            if current_scene == "minigame":
                for choice in rps_choices:
                    if rps_buttons[choice].collidepoint(event.pos):

                        if not rps_cooldown:
                            import random

                            player = choice
                            cpu = random.choice(rps_choices)

                            if player == cpu:
                                rps_result = "Draw!"
                            elif (player == "rock" and cpu == "scissors") or \
                                    (player == "paper" and cpu == "rock") or \
                                    (player == "scissors" and cpu == "paper"):
                                rps_result = f"You win! ({player} beats {cpu})"
                                coin_count += 1
                                save_rock_data(rock_name, selected_background, selected_personality, music_on,
                                               coin_count)
                            else:
                                rps_result = f"You lose! ({cpu} beats {player})"

                            rps_cooldown = True
                            rps_cooldown_timer = pygame.time.get_ticks()

                            if rps_cooldown:
                                elapsed = pygame.time.get_ticks() - rps_cooldown_timer
                                fill_width = min(100, (elapsed / cooldown_duration) * 100)
                                pygame.draw.rect(screen, (180, 180, 180), cooldown_bar_rect)
                                pygame.draw.rect(screen, (100, 200, 100),
                                                 cooldown_bar_rect.copy().inflate(-2, -2).move(0, 0).clip(
                                                     pygame.Rect(cooldown_bar_rect.x, cooldown_bar_rect.y, fill_width,
                                                                 10)))

    if current_scene == "main":
        screen.fill(BG_COLOR)
        scaled_bg = pygame.transform.scale(backgrounds[selected_background], (WIDTH, HEIGHT))
        screen.blit(scaled_bg, (0, 0))

        screen.blit(rock_img, rock_rect)

        # === Active Pet Animation ===
        if active_pet == "bee" and bee_unlocked and bee_frames:
            bee_timer += 1
            if bee_timer % 6 == 0:
                bee_index = (bee_index + 1) % len(bee_frames)
            bee_img = bee_frames[bee_index]
            pet_x = rock_rect.left - bee_img.get_width() - 10
            pet_y = rock_rect.top - bee_img.get_height() + 20
            screen.blit(bee_img, (pet_x, pet_y))

        elif active_pet == "bat" and bat_unlocked and bat_frames:
            bat_timer += 1
            if bat_timer % 6 == 0:
                bat_index = (bat_index + 1) % len(bat_frames)
            bat_img = bat_frames[bat_index]
            pet_x = rock_rect.left - bat_img.get_width() - 10
            pet_y = rock_rect.top - bat_img.get_height() + 20
            screen.blit(bat_img, (pet_x, pet_y))

        elif active_pet == "pig" and pig_unlocked and pig_frames:
            pig_timer += 1
            if pig_timer % 6 == 0:
                pig_index = (pig_index + 1) % len(pig_frames)
            pig_img = pig_frames[pig_index]
            pet_x = rock_rect.left - pig_img.get_width() - 10
            pet_y = rock_rect.top - pig_img.get_height() + 180
            screen.blit(pig_img, (pet_x, pet_y))

        elif active_pet == "fox" and fox_unlocked and fox_frames:
            fox_timer += 1
            if fox_timer % 6 == 0:
                fox_index = (fox_index + 1) % len(fox_frames)
            fox_img = fox_frames[fox_index]
            pet_x = rock_rect.left - fox_img.get_width() - 10
            pet_y = rock_rect.top - fox_img.get_height() + 180
            screen.blit(fox_img, (pet_x, pet_y))

        elif active_pet == "troll" and troll_unlocked and troll_frames:
            troll_timer += 1
            if troll_timer % 6 == 0:
                troll_index = (troll_index + 1) % len(troll_frames)
            troll_img = troll_frames[troll_index]
            pet_x = rock_rect.left - troll_img.get_width() - 10
            pet_y = rock_rect.top - troll_img.get_height() + 180
            screen.blit(troll_img, (pet_x, pet_y))

        # === Sleep Logic ===
        if in_sleep_mode and sleep_frames:
            sleep_timer += 1
            if sleep_timer % 5 == 0:
                sleep_index = (sleep_index + 1) % len(sleep_frames)

            sleep_img = sleep_frames[sleep_index]
            sleep_x = rock_rect.centerx - sleep_img.get_width() // 2 + 80
            sleep_y = rock_rect.centery - sleep_img.get_height() - 40
            screen.blit(sleep_img, (sleep_x, sleep_y))

        if show_name_tag:
            name_surface = button_font.render(rock_name, True, (50, 50, 50))
            name_x = rock_rect.centerx - name_surface.get_width() // 2
            name_y = rock_rect.top - 30
            screen.blit(name_surface, (name_x, name_y))

        if show_happy_emote and happy_frames:
            happy_emote_timer += 1
            if happy_emote_timer % 4 == 0:
                happy_emote_index += 1
                if happy_emote_index >= len(happy_frames):
                    show_happy_emote = False
                    happy_emote_index = 0
            # === Happy Emote logic ===
            if happy_emote_index < len(happy_frames):
                frame = happy_frames[happy_emote_index]
                emote_x = rock_rect.centerx - frame.get_width() // 2 + 100
                emote_y = rock_rect.centery - frame.get_height() - 40
                screen.blit(frame, (emote_x, emote_y))

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

            # Tone cycle button
            tone_btn_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 10, 200, 40)
            tone_label = f"Tone: {selected_personality}"
            draw_button(screen, tone_btn_rect, tone_label, button_font)

            # Handle tone change
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tone_btn_rect.collidepoint(event.pos) and not tone_button_pressed:
                    personality_index = (personality_index + 1) % len(personality_options)
                    selected_personality = personality_options[personality_index]
                    tone_button_pressed = True
                    save_rock_data(rock_name, selected_background, selected_personality)

            # Change name button
            name_change_btn_rect = pygame.Rect(settings_rect.x + 50, settings_rect.y + 160, 200, 40)
            draw_button(screen, name_change_btn_rect, "Change Name", button_font)

            # Handle click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if name_toggle_rect.collidepoint(event.pos) and not name_button_pressed:
                    show_name_tag = not show_name_tag
                    name_button_pressed = True
                if name_change_btn_rect.collidepoint(event.pos):
                    renaming_mode = True
                    input_active = True

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
            # === Spam Prevention ===
            if event.type == pygame.MOUSEBUTTONUP:
                music_button_pressed = False
                name_button_pressed = False
                tone_button_pressed = False

        if is_thinking and thinking_frames:
            thinking_timer += 1
            if thinking_timer % 6 == 0:
                thinking_frame_index = (thinking_frame_index + 1) % len(thinking_frames)

            thinking_img = thinking_frames[thinking_frame_index]
            thinking_x = rock_rect.right - 20  # ADJUST
            thinking_y = rock_rect.top - thinking_img.get_height() + 60  # ADJUST
            screen.blit(thinking_img, (thinking_x, thinking_y))

        # Coin display
        draw_coin_display(screen, coin_img, button_font, coin_count, x=20, y=400)
        # === Store Scene ===
    elif current_scene == "store":
        screen.fill((230, 245, 250))
        title = button_font.render("Rock Store", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        draw_button(screen, back_button_rect, "Back", button_font)

        # Pets button
        pets_button_rect = pygame.Rect(WIDTH // 2 - 100, 500, 200, 40)
        draw_button(screen, pets_button_rect, "Pets", button_font)

        # Clothing button
        clothing_button_rect = pygame.Rect(WIDTH // 2 - 100, 550, 200, 40)
        draw_button(screen, clothing_button_rect, "Clothing", button_font)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pets_button_rect.collidepoint(event.pos):
                current_scene = "pet_store"
            if clothing_button_rect.collidepoint(event.pos):
                current_scene = "clothing_store"

        for i, bg in enumerate(unlockable_bgs):
            y_offset = 150 + i * 60
            rect = pygame.Rect(WIDTH // 2 - 100, y_offset, 200, 40)

            if bg_unlocks.get(bg, False):
                draw_button(screen, rect, f"{bg.title()} BG Unlocked!", button_font)
            else:
                draw_button(screen, rect, f"Buy {bg.title()} BG ({bg_unlock_cost} coins)", button_font)
                if event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos):
                    if coin_count >= bg_unlock_cost:
                        bg_unlocks[bg] = True
                        selected_background = bg
                        coin_count -= bg_unlock_cost
                        save_rock_data(rock_name, selected_background, selected_personality, music_on, coin_count)

    elif current_scene == "pet_store":
        screen.fill((240, 240, 250))
        title = button_font.render("Pet Store", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Pet card rectangles
        # Row 1 (top 3)
        bee_card_rect = pygame.Rect(WIDTH // 2 - 310, 100, 180, 200)
        bat_card_rect = pygame.Rect(WIDTH // 2 - 90, 100, 180, 200)
        pig_card_rect = pygame.Rect(WIDTH // 2 + 130, 100, 180, 200)

        # Row 2 (bottom 2)
        fox_card_rect = pygame.Rect(WIDTH // 2 - 180, 320, 180, 200)
        troll_card_rect = pygame.Rect(WIDTH // 2 + 20, 320, 180, 200)

        pygame.draw.rect(screen, (220, 220, 220), bee_card_rect)
        pygame.draw.rect(screen, (220, 220, 220), bat_card_rect)

        pygame.draw.rect(screen, (0, 0, 0), bee_card_rect, 2)
        pygame.draw.rect(screen, (0, 0, 0), bat_card_rect, 2)

        pygame.draw.rect(screen, (220, 220, 220), pig_card_rect)
        pygame.draw.rect(screen, (0, 0, 0), pig_card_rect, 2)

        pygame.draw.rect(screen, (220, 220, 220), fox_card_rect)
        pygame.draw.rect(screen, (0, 0, 0), fox_card_rect, 2)

        pygame.draw.rect(screen, (220, 220, 220), troll_card_rect)
        pygame.draw.rect(screen, (0, 0, 0), troll_card_rect, 2)

        # Bee image inside card
        if bee_frames:
            bee_img = bee_frames[0]
            bee_img_x = bee_card_rect.x + (bee_card_rect.width - bee_img.get_width()) // 2
            bee_img_y = bee_card_rect.y + 20
            screen.blit(bee_img, (bee_img_x, bee_img_y))

        # Bat image inside card
        if bat_frames:
            bat_img = bat_frames[0]
            bat_img_x = bat_card_rect.x + (bat_card_rect.width - bat_img.get_width()) // 2
            bat_img_y = bat_card_rect.y + 20
            screen.blit(bat_img, (bat_img_x, bat_img_y))

        # Pig image inside card
        if pig_frames:
            pig_img = pig_frames[0]
            pig_img_x = pig_card_rect.x + (pig_card_rect.width - pig_img.get_width()) // 2
            pig_img_y = pig_card_rect.y + 20
            screen.blit(pig_img, (pig_img_x, pig_img_y))

        # Fox image inside card
        if fox_frames:
            fox_img = fox_frames[0]
            fox_img_x = fox_card_rect.x + (fox_card_rect.width - fox_img.get_width()) // 2
            fox_img_y = fox_card_rect.y + 20
            screen.blit(fox_img, (fox_img_x, fox_img_y))

        # Troll image inside card
            if troll_frames:
                troll_img = troll_frames[0]
                troll_img_x = troll_card_rect.x + (troll_card_rect.width - troll_img.get_width()) // 2
                troll_img_y = troll_card_rect.y + 20
                screen.blit(troll_img, (troll_img_x, troll_img_y))

        # Dark overlay for locked pets
        if not bee_unlocked:
            overlay = pygame.Surface((bee_card_rect.width, bee_card_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))  # semi-transparent black
            screen.blit(overlay, bee_card_rect.topleft)

        if not bat_unlocked:
            overlay = pygame.Surface((bat_card_rect.width, bat_card_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, bat_card_rect.topleft)

        if not pig_unlocked:
            overlay = pygame.Surface((pig_card_rect.width, pig_card_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, pig_card_rect.topleft)

        if not fox_unlocked:
            overlay = pygame.Surface((fox_card_rect.width, fox_card_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, fox_card_rect.topleft)

        if not troll_unlocked:
            overlay = pygame.Surface((troll_card_rect.width, troll_card_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, troll_card_rect.topleft)

        # Bee label
        bee_label = "Unlocked" if bee_unlocked else "Buy (50 coins)"
        bee_label_surface = button_font.render(f"Bee - {bee_label}", True, (0, 0, 0))
        bee_label_x = bee_card_rect.x + (bee_card_rect.width - bee_label_surface.get_width()) // 2
        bee_label_y = bee_card_rect.y + bee_card_rect.height - 35
        screen.blit(bee_label_surface, (bee_label_x, bee_label_y))

        # Bat label
        bat_label = "Unlocked" if bat_unlocked else "Buy (50 coins)"
        bat_label_surface = button_font.render(f"Bat - {bat_label}", True, (0, 0, 0))
        bat_label_x = bat_card_rect.x + (bat_card_rect.width - bat_label_surface.get_width()) // 2
        bat_label_y = bat_card_rect.y + bat_card_rect.height - 35
        screen.blit(bat_label_surface, (bat_label_x, bat_label_y))

        # Pig label
        pig_label = "Unlocked" if pig_unlocked else "Buy (50 coins)"
        pig_label_surface = button_font.render(f"Pig - {pig_label}", True, (0, 0, 0))
        pig_label_x = pig_card_rect.x + (pig_card_rect.width - pig_label_surface.get_width()) // 2
        pig_label_y = pig_card_rect.y + pig_card_rect.height - 35
        screen.blit(pig_label_surface, (pig_label_x, pig_label_y))

        # Fox label
        fox_label = "Unlocked" if fox_unlocked else "Buy (50 coins)"
        fox_label_surface = button_font.render(f"Fox - {fox_label}", True, (0, 0, 0))
        fox_label_x = fox_card_rect.x + (fox_card_rect.width - fox_label_surface.get_width()) // 2
        fox_label_y = fox_card_rect.y + fox_card_rect.height - 35
        screen.blit(fox_label_surface, (fox_label_x, fox_label_y))

        # Troll label
        troll_label = "Unlocked" if troll_unlocked else "Buy (50 coins)"
        troll_label_surface = button_font.render(f"Troll - {troll_label}", True, (0, 0, 0))
        troll_label_x = troll_card_rect.x + (troll_card_rect.width - troll_label_surface.get_width()) // 2
        troll_label_y = troll_card_rect.y + troll_card_rect.height - 35
        screen.blit(troll_label_surface, (troll_label_x, troll_label_y))

        draw_button(screen, back_button_rect, "Back", button_font)

        # === Pet Card Click Logic ==
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_scene == "clothing_store":
                if back_button_rect.collidepoint(event.pos):
                    current_scene = "store"

                if bee_card_rect.collidepoint(event.pos):
                    if not bee_unlocked and coin_count >= 50:
                        bee_unlocked = True
                        coin_count -= 50
                    if bee_unlocked:
                        active_pet = "bee"

                if bat_card_rect.collidepoint(event.pos):
                    if not bat_unlocked and coin_count >= 50:
                        bat_unlocked = True
                        coin_count -= 50
                    if bat_unlocked:
                        active_pet = "bat"

                if fox_card_rect.collidepoint(event.pos):
                    if not fox_unlocked and coin_count >= 50:
                        fox_unlocked = True
                        coin_count -= 50
                    if fox_unlocked:
                        active_pet = "fox"

        # === Pet Logic ===
        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button_rect.collidepoint(event.pos):
                current_scene = "store"

            if bee_card_rect.collidepoint(event.pos):
                if not bee_unlocked and coin_count >= 50:
                    bee_unlocked = True
                    coin_count -= 50
                active_pet = "bee"

            if bat_card_rect.collidepoint(event.pos):
                if not bat_unlocked and coin_count >= 50:
                    bat_unlocked = True
                    coin_count -= 50
                active_pet = "bat"

    elif current_scene == "clothing_store":
        screen.fill((245, 235, 255))
        title = button_font.render("Clothing Store (Coming Soon)", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # === Sombrero Card ===
        sombrero_card_rect = pygame.Rect(WIDTH // 2 - 90, 150, 180, 200)
        pygame.draw.rect(screen, (220, 220, 220), sombrero_card_rect)
        pygame.draw.rect(screen, (0, 0, 0), sombrero_card_rect, 2)

        # Sombrero Image
        screen.blit(sombrero_img, (sombrero_card_rect.x + 40, sombrero_card_rect.y + 30))

        # Sombrero Label
        sombrero_label = "Equipped" if wearing_sombrero else ("Unlocked" if sombrero_unlocked else "Buy (25 coins)")
        label_surface = button_font.render(f"Sombrero - {sombrero_label}", True, (0, 0, 0))
        screen.blit(label_surface, (sombrero_card_rect.x + 10, sombrero_card_rect.y + 150))

        draw_button(screen, back_button_rect, "Back", button_font)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if back_button_rect.collidepoint(event.pos):
                current_scene = "store"


    elif current_scene == "minigame":
        screen.fill((250, 240, 200))  # distinct background for mini-game
        title_text = button_font.render("Rock-Paper-Scissors!", True, (0, 0, 0))
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        draw_button(screen, back_button_rect, "Back", button_font)

        # === Show RPS Result ===
        if rps_result:
            result_text = button_font.render(rps_result, True, (0, 0, 0))
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, 300))

        for i, choice in enumerate(rps_choices):
            rect = rps_buttons[choice]
            screen.blit(rps_icons[choice], rect.topleft)

        # === Cooldown Bar ===
        if rps_cooldown:
            cooldown_duration = 2000  # 2 seconds
            time_elapsed = pygame.time.get_ticks() - rps_cooldown_timer
            time_ratio = min(time_elapsed / cooldown_duration, 1)

            bar_width = 200
            bar_height = 15
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = 100

            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))  # background
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * time_ratio), bar_height))  # fill

    # === Draw Render ==
    if current_scene == "main":
        for btn in buttons.values():
            label = btn["label"]() if callable(btn["label"]) else btn["label"]
            draw_button(screen, btn["rect"], label, button_font)

    # === Hover Icon ===
    if current_scene == "main":
        mouse_pos = pygame.mouse.get_pos()
        if gear_rect.collidepoint(mouse_pos):
            hover_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
            hover_surface.fill((255, 255, 255, 50))
            screen.blit(gear_icon, gear_rect.topleft)
            screen.blit(hover_surface, gear_rect.topleft)
        else:
            screen.blit(gear_icon, gear_rect.topleft)

    if current_scene == "main":
        draw_input_box(screen, input_box_rect, user_input, FONT, input_active, cursor_visible,
                       naming_phase or renaming_mode)

        response_box_rect = pygame.Rect(40, 80, WIDTH - 80, 100)

        if is_thinking:
            typed_text = ""
            char_index = 0
        elif char_index < len(rock_response):
            typing_timer += 1
            if typing_timer % typing_speed == 0:
                char_index += 1
            typed_text = rock_response[:char_index]
        else:
            typed_text = rock_response

        draw_response_box(screen, response_box_rect, FONT, typed_text, naming_phase)

    # cursor blink
    cursor_visible = (cursor_timer % 60) < 30
    cursor_timer += 1
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
