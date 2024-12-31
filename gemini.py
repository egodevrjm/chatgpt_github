import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 800

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)

# Collector zone colors (can be customized)
zone_colors = [red, green, blue]

# Shape colors (must match zone colors)
shape_colors = zone_colors

# Screen setup
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Color Dash")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Font settings
font_style = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 60)

# --- Sound settings ---
sound_on = False  # Flag to control sound (True by default)

# Sound effects (load only if sound_on is True)
if sound_on:
    try:
        match_sound = pygame.mixer.Sound("match.wav")
        wrong_match_sound = pygame.mixer.Sound("wrong.wav")
        game_over_sound = pygame.mixer.Sound("game_over.wav")
    except pygame.error:
        print("Error loading sound files. Sound will be disabled.")
        sound_on = False
        match_sound = None
        wrong_match_sound = None
        game_over_sound = None
else:
    match_sound = None
    wrong_match_sound = None
    game_over_sound = None


def play_sound(sound):
    """Plays a sound if sound_on is True."""
    if sound_on and sound:
        sound.play()


def display_message(message, color, y_offset=0, font=font_style):
    """Displays a text message on the screen."""
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (screen_width / 2, screen_height / 2 + y_offset)
    screen.blit(text_surface, text_rect)


def load_high_score():
    """Loads the high score from a file."""
    try:
        with open("high_score.txt", "r") as file:
            return int(file.read())
    except FileNotFoundError:
        return 0


def save_high_score(score):
    """Saves the high score to a file."""
    with open("high_score.txt", "w") as file:
        file.write(str(score))


def draw_collector_zones(zones):
    """Draws the collector zones at the bottom of the screen."""
    for zone in zones:
        pygame.draw.rect(screen, zone["color"], zone["rect"])


def draw_shape(shape):
    """Draws a falling shape."""
    color = shape["color"]
    x = shape["rect"].x
    y = shape["rect"].y
    size = shape["rect"].width  # Assuming square shapes for simplicity

    if shape["type"] == "circle":
        pygame.draw.circle(screen, color, (x + size // 2, y + size // 2), size // 2)
    elif shape["type"] == "square":
        pygame.draw.rect(screen, color, shape["rect"])
    elif shape["type"] == "triangle":
        points = [
            (x + size // 2, y),
            (x, y + size),
            (x + size, y + size),
        ]  # Triangle points
        pygame.draw.polygon(screen, color, points)


def game_intro():
    """Displays the game's title screen."""
    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    intro = False
                if event.key == pygame.K_s:
                    global sound_on
                    sound_on = not sound_on

        screen.fill(black)
        display_message("Color Dash", white, -100, title_font)
        display_message("Press Space to Start", white, 0)
        sound_status = "ON" if sound_on else "OFF"
        display_message(f"Sound: {sound_status} (Press 'S' to toggle)", white, 50)
        pygame.display.update()
        clock.tick(15)


def game_over_screen(score, high_score):
    """Displays the game over screen."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_loop()  # Restart the game

        screen.fill(black)
        display_message("Game Over", red, -50)
        display_message(f"Score: {score}", white, 0)
        display_message(f"High Score: {high_score}", white, 50)
        display_message("Press Space to Restart", white, 100)
        pygame.display.update()
        clock.tick(15)


def game_loop():
    """Main game loop."""
    game_over = False

    # --- Game variables ---
    score = 0
    high_score = load_high_score()
    lives = 3
    shape_speed = 5  # Initial falling speed
    speed_increase_interval = 20  # Increase speed every 20 points
    zone_width = screen_width // 3
    zone_height = 50
    shape_size = 40

    # --- Collector zones setup ---
    zones = [
        {"color": zone_colors[0], "rect": pygame.Rect(0, screen_height - zone_height, zone_width, zone_height)},
        {"color": zone_colors[1], "rect": pygame.Rect(zone_width, screen_height - zone_height, zone_width, zone_height)},
        {"color": zone_colors[2], "rect": pygame.Rect(zone_width * 2, screen_height - zone_height, zone_width, zone_height)},
    ]
    zone_position = 1  # Start with the middle zone (index 1)

    # --- Falling shapes setup ---
    shapes = []
    shape_types = ["circle", "square", "triangle"]
    last_shape_time = time.time()
    shape_spawn_delay = 1.5  # Initial delay in seconds

    # --- Game loop ---
    while not game_over:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    zone_position = max(0, zone_position - 1)  # Move zones left
                elif event.key == pygame.K_RIGHT:
                    zone_position = min(len(zones) - 1, zone_position + 1)  # Move zones right

        # --- Move the collector zones ---
        # Update zone positions based on the current zone_position index
        for i, zone in enumerate(zones):
            zone["rect"].x = (zone_position - 1 + i) * zone_width

        # --- Spawn new shapes ---
        current_time = time.time()
        if current_time - last_shape_time > shape_spawn_delay:
            new_shape = {
                "type": random.choice(shape_types),
                "color": random.choice(shape_colors),
                "rect": pygame.Rect(
                    random.randint(0, screen_width - shape_size),
                    0 - shape_size,
                    shape_size,
                    shape_size,
                ),
            }
            shapes.append(new_shape)
            last_shape_time = current_time

        # --- Move shapes down ---
        for shape in shapes:
            shape["rect"].y += shape_speed

        # --- Collision detection and scoring ---
        for shape in shapes[:]:  # Iterate over a copy to allow removing
            if shape["rect"].y > screen_height:
                shapes.remove(shape)  # Remove if it goes off-screen
                lives -= 1
                play_sound(wrong_match_sound)
                if lives == 0:
                    play_sound(game_over_sound)
                    game_over = True

            else:
                for zone in zones:
                    if shape["rect"].colliderect(zone["rect"]):
                        if shape["color"] == zone["color"]:
                            score += 1
                            play_sound(match_sound)
                            if score > high_score:
                                high_score = score
                            if score % speed_increase_interval == 0:
                                shape_speed += 1  # Increase speed
                                shape_spawn_delay = max(0.5, shape_spawn_delay-0.1)
                            # Basic animation: Make the shape disappear quickly
                            shape["rect"].y = screen_height  # Move off-screen
                        else:
                            lives -= 1
                            play_sound(wrong_match_sound)
                            if lives == 0:
                                play_sound(game_over_sound)
                                game_over = True

                        shapes.remove(shape)
                        break

        # --- Drawing ---
        screen.fill(black)  # Clear the screen
        draw_collector_zones(zones)
        for shape in shapes:
            draw_shape(shape)

        # --- Display score, high score, and lives ---
        display_message(f"Score: {score}", white, -screen_height // 2 + 50, font=font_style)
        display_message(f"High Score: {high_score}", white, -screen_height // 2 + 80, font=font_style)
        display_message(f"Lives: {lives}", white, -screen_height // 2 + 110, font=font_style)

        pygame.display.update()  # Update the display
        clock.tick(60)  # Limit to 60 frames per second

    # --- Game over sequence ---
    save_high_score(high_score)
    game_over_screen(score, high_score)


# --- Start the game ---
game_intro()
game_loop()
pygame.quit()
quit()