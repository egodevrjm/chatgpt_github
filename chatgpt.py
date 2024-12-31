"""
Color Dash
A fast-paced arcade game where coloured shapes fall from the top of the screen,
and the player must move three collector zones at the bottom to match the colours.

Press Left/Right to move the zones.
Match the falling shape's colour with the zone's colour to increase score.
Lose a life if you miss or if you match incorrectly.
Game gets faster with higher score.
Press Space to restart after game over.

Author: Your Name
"""

import pygame
import sys
import random
import os

# Initialise PyGame
pygame.init()

# ------------ GAME CONFIGURATION ------------
WIDTH, HEIGHT = 600, 800        # Screen dimensions
FPS = 60                         # Frames per second
SHAPE_FALL_SPEED = 3            # Initial fall speed of shapes
SPEED_INCREMENT_INTERVAL = 5    # Increase speed every N points
SPEED_INCREMENT_AMOUNT = 0.5    # Amount to increase speed

NUM_LIVES = 3                   # Starting number of lives
FONT_NAME = pygame.font.get_default_font()
TITLE_TEXT_SIZE = 64
UI_TEXT_SIZE = 24

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

# List of possible colours for shapes & collector zones
COLOUR_LIST = [RED, GREEN, BLUE]

# Positioning & sizes
ZONE_WIDTH  = 100   # Width of one collector zone
ZONE_HEIGHT = 50    # Height of one collector zone
BOTTOM_MARGIN = 50  # Distance from bottom of screen to the zones

# Timers for shape spawn
SHAPE_SPAWN_INTERVAL = 1000  # in milliseconds

# File for storing high score
HIGH_SCORE_FILE = "highscore.txt"

# Sound effect placeholders (use your own .wav if preferred)
# You can place real .wav files in the same folder or comment out if not needed
try:
    match_sound = pygame.mixer.Sound("match.wav")
    miss_sound = pygame.mixer.Sound("miss.wav")
    gameover_sound = pygame.mixer.Sound("gameover.wav")
except:
    # If no .wav files found, you could comment these out or handle differently
    match_sound = None
    miss_sound = None
    gameover_sound = None

# Set up screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Dash")
clock = pygame.time.Clock()

# ------------- GAME STATES -------------
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2


def load_high_score():
    """
    Reads high score from a local file.
    If file doesn't exist, returns 0.
    """
    if not os.path.exists(HIGH_SCORE_FILE):
        return 0
    with open(HIGH_SCORE_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_high_score(score):
    """
    Saves the given score to a local file as the new high score.
    """
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


class CollectorZones:
    """
    Class representing the three collector zones at the bottom of the screen.
    We will display them side-by-side but only one is the "active" zone.
    The player can move left or right to shift the colours.
    """
    def __init__(self):
        # The zone colours are in the same order as COLOUR_LIST: [RED, GREEN, BLUE]
        self.index = 0  # which colour is in the left-most position
        # We'll store them in a list in a cyclical manner
        # The center zone effectively is the 'target' zone that must match the falling shape's colour
        self.x = WIDTH // 2 - ZONE_WIDTH  # Start with the middle zone in the centre
        self.y = HEIGHT - BOTTOM_MARGIN
        self.colours = COLOUR_LIST[:]  # [RED, GREEN, BLUE]
    
    def move_left(self):
        """
        Moves the collector colour set one to the left.
        That effectively changes which colour is in the middle.
        """
        self.index = (self.index - 1) % 3
    
    def move_right(self):
        """
        Moves the collector colour set one to the right.
        """
        self.index = (self.index + 1) % 3
    
    def get_centre_colour(self):
        """
        Returns the colour that is in the centre zone,
        which is the 'active' zone to match the falling shape.
        """
        # The centre zone is index (self.index + 1) % 3
        return self.colours[(self.index + 1) % 3]
    
    def draw(self, surface):
        """
        Draws the three zones at the bottom of the screen.
        The centre zone is the active matching zone.
        """
        for i in range(3):
            # zone_x is offset by i * ZONE_WIDTH
            zone_x = self.x + (i * ZONE_WIDTH)
            colour = self.colours[(self.index + i) % 3]
            
            pygame.draw.rect(
                surface,
                colour,
                (zone_x, self.y, ZONE_WIDTH, ZONE_HEIGHT)
            )


class FallingShape:
    """
    Represents a single falling shape (circle, square, or triangle).
    It has a random colour chosen from COLOUR_LIST
    and a random shape type.
    """
    def __init__(self, fall_speed):
        self.colour = random.choice(COLOUR_LIST)
        self.shape_type = random.choice(["circle", "square", "triangle"])
        self.x = random.randint(50, WIDTH - 50)
        self.y = -50  # start above the screen
        self.speed = fall_speed  # how fast it falls each frame
        self.size = 30  # arbitrary size for drawing
    
    def update(self):
        """
        Moves the shape down the screen by its speed.
        """
        self.y += self.speed
    
    def is_off_screen(self):
        """
        Check if the shape has gone below the bottom of the screen.
        """
        return self.y - self.size > HEIGHT
    
    def draw(self, surface):
        """
        Draws the shape on the screen.
        We only use basic PyGame shapes: circle, rect, polygon for triangle.
        """
        if self.shape_type == "circle":
            pygame.draw.circle(surface, self.colour, (self.x, int(self.y)), self.size)
        elif self.shape_type == "square":
            pygame.draw.rect(surface, self.colour, 
                             (self.x - self.size, int(self.y) - self.size, self.size * 2, self.size * 2))
        elif self.shape_type == "triangle":
            # An upward pointing triangle by default
            points = [
                (self.x, self.y - self.size),
                (self.x - self.size, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
            pygame.draw.polygon(surface, self.colour, points)


def draw_text(surface, text, size, x, y, colour=WHITE, centre=True):
    """
    Helper function to draw text onto the screen.
    If centre=True, the text is centre-aligned at (x, y).
    Otherwise, draws from top-left at (x, y).
    """
    font = pygame.font.Font(FONT_NAME, size)
    rendered_text = font.render(text, True, colour)
    rect = rendered_text.get_rect()
    if centre:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered_text, rect)


def main():
    # Game loop variables
    running = True
    
    # Load or initialise high score
    high_score = load_high_score()
    
    # Current game state
    game_state = STATE_TITLE
    
    # Prepare collector zones
    collector = CollectorZones()
    
    # Shapes container
    shapes = []

    # Score and lives
    score = 0
    lives = NUM_LIVES
    current_fall_speed = SHAPE_FALL_SPEED
    
    # Timers
    last_spawn_time = pygame.time.get_ticks()
    
    while running:
        clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                # Title screen -> Press any key to start
                if game_state == STATE_TITLE:
                    game_state = STATE_PLAYING
                    # Reset everything
                    score = 0
                    lives = NUM_LIVES
                    shapes = []
                    collector = CollectorZones()
                    current_fall_speed = SHAPE_FALL_SPEED
                    last_spawn_time = pygame.time.get_ticks()
                
                # Gameplay controls
                elif game_state == STATE_PLAYING:
                    if event.key == pygame.K_LEFT:
                        collector.move_left()
                    elif event.key == pygame.K_RIGHT:
                        collector.move_right()
                
                # Game over -> Press space to restart
                elif game_state == STATE_GAMEOVER:
                    if event.key == pygame.K_SPACE:
                        game_state = STATE_TITLE
        
        # --- UPDATE LOGIC ---
        if game_state == STATE_PLAYING:
            # Spawn new shapes at intervals
            current_time = pygame.time.get_ticks()
            if current_time - last_spawn_time > SHAPE_SPAWN_INTERVAL:
                shapes.append(FallingShape(current_fall_speed))
                last_spawn_time = current_time
            
            # Update shapes
            for shape in shapes:
                shape.update()
            
            # Check for shape collisions / off-screen
            # We'll check if the shape has reached near the collector zone's y
            # The zone is at collector.y, shape has size ~ 30, so let's define a "hit zone".
            to_remove = []
            
            for shape in shapes:
                if shape.y + shape.size >= collector.y:
                    # If shape colour matches centre zone colour -> success
                    if shape.colour == collector.get_centre_colour():
                        score += 1
                        # Play match sound
                        if match_sound:
                            match_sound.play()
                        
                        # Speed up after certain intervals
                        if score % SPEED_INCREMENT_INTERVAL == 0:
                            current_fall_speed += SPEED_INCREMENT_AMOUNT
                        
                    else:
                        # Wrong match
                        lives -= 1
                        # Play miss sound
                        if miss_sound:
                            miss_sound.play()
                    
                    to_remove.append(shape)
                
                elif shape.is_off_screen():
                    # If it passed off screen, it's a miss
                    lives -= 1
                    # Play miss sound
                    if miss_sound:
                        miss_sound.play()
                    to_remove.append(shape)
            
            # Remove the shapes that have either collided or gone off screen
            for shape in to_remove:
                if shape in shapes:
                    shapes.remove(shape)
            
            # Check if game over
            if lives <= 0:
                # Update high score
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                
                # Play game over sound
                if gameover_sound:
                    gameover_sound.play()
                
                game_state = STATE_GAMEOVER
        
        # --- DRAW SECTION ---
        screen.fill(BLACK)
        
        if game_state == STATE_TITLE:
            # Draw title screen
            draw_text(screen, "COLOR DASH", TITLE_TEXT_SIZE, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, "Press any key to start", UI_TEXT_SIZE, WIDTH // 2, HEIGHT // 2 + 20)
        
        elif game_state == STATE_PLAYING:
            # Draw shapes
            for shape in shapes:
                shape.draw(screen)
            
            # Draw collector zones
            collector.draw(screen)
            
            # Draw UI text: Score, High Score, Lives
            draw_text(screen, f"Score: {score}", UI_TEXT_SIZE, 10, 10, WHITE, centre=False)
            draw_text(screen, f"High Score: {high_score}", UI_TEXT_SIZE, 10, 40, WHITE, centre=False)
            draw_text(screen, f"Lives: {lives}", UI_TEXT_SIZE, WIDTH - 10, 10, WHITE, centre=False)
        
        elif game_state == STATE_GAMEOVER:
            # Draw "Game Over"
            draw_text(screen, "GAME OVER", TITLE_TEXT_SIZE, WIDTH // 2, HEIGHT // 2 - 60)
            draw_text(screen, f"Final Score: {score}", UI_TEXT_SIZE, WIDTH // 2, HEIGHT // 2)
            draw_text(screen, f"High Score: {high_score}", UI_TEXT_SIZE, WIDTH // 2, HEIGHT // 2 + 40)
            draw_text(screen, "Press SPACE to return to title", UI_TEXT_SIZE, WIDTH // 2, HEIGHT // 2 + 80)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
