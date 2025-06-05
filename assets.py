import pygame


def load_assets():
    WIDTH, HEIGHT = 800, 600

    rock_img = pygame.image.load("rock.png").convert_alpha()
    rock_img = pygame.transform.scale(rock_img, (200, 200))
    rock_rect = rock_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))

    backgrounds = {
        "desert": pygame.image.load("backgrounds/desert.png").convert(),
        "forest": pygame.image.load("backgrounds/forest.png").convert(),
        "grass": pygame.image.load("backgrounds/grass.png").convert(),
        "beach": pygame.image.load("backgrounds/beach.png").convert()
    }

    coin_img = pygame.image.load("assets/icons/coin.png").convert_alpha()
    coin_img = pygame.transform.scale(coin_img, (30, 30))

    return rock_img, rock_rect, backgrounds, coin_img
