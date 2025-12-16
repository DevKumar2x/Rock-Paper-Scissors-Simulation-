import pygame
import random
import math
import os

# Initialize pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
ENTITY_RADIUS = 5
SPEED = 3
DETECTION_RADIUS = 100
CONVERSION_RADIUS = 20
EDGE_AVOID_RADIUS = 50
REPULSION_RADIUS = 20
ICON_WIDTH = 30
ICON_HEIGHT = 30

# Set up display FIRST
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Rock Paper Scissors Simulation")
clock = pygame.time.Clock()

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load and scale the background image with error handling
bg_path = os.path.join(script_dir, 'photos' , 'bg.jpg')
if not os.path.exists(bg_path):
    print(f"Warning: Background image not found at {bg_path}")
    background_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    background_image.fill((50, 50, 50))  # Dark gray fallback
else:
    try:
        background_image = pygame.image.load(bg_path)
        background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        print(f"Background loaded successfully from {bg_path}")
    except pygame.error as e:
        print(f"Error loading background: {e}")
        background_image = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background_image.fill((50, 50, 50))


# Load and scale entity icons with error handling
def load_image(filename, width, height):
    path = os.path.join(script_dir, filename)
    if not os.path.exists(path):
        print(f"Warning: Image not found at {path}")
        surface = pygame.Surface((width, height))
        surface.fill((100, 100, 100))
        return surface
    try:
        img = pygame.image.load(path)
        scaled_img = pygame.transform.scale(img, (width, height))
        print(f"Image loaded successfully: {filename}")
        return scaled_img
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        surface = pygame.Surface((width, height))
        surface.fill((100, 100, 100))
        return surface

rock_icon = load_image('photos/rock.png', ICON_WIDTH, ICON_HEIGHT)
paper_icon = load_image('photos/paper.png', ICON_WIDTH, ICON_HEIGHT)
scissors_icon = load_image('photos/scissor_02.png', ICON_WIDTH, ICON_HEIGHT)

print(f"Script directory: {script_dir}")
print(f"Looking for images in: {script_dir}")


class Entity:
    # Initialization method
    def __init__(self, x, y, tribe):
        self.x = x
        self.y = y
        self.tribe = tribe

    # Move towards method
    def move_towards(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x += (SPEED + random.uniform(-0.3, 0.3)) * math.cos(angle)
        self.y += (SPEED + random.uniform(-0.3, 0.3)) * math.sin(angle)
        self.avoid_edges()

    # Move away method
    def move_away_from(self, target_x, target_y):
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.x -= (SPEED + random.uniform(-0.3, 0.3)) * math.cos(angle)
        self.y -= (SPEED + random.uniform(-0.3, 0.3)) * math.sin(angle)
        self.avoid_edges()

    # Distance calculation method
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    # Repulsion method
    def repel_from(self, other):
        if self.distance_to(other) < REPULSION_RADIUS:
            self.move_away_from(other.x, other.y)

    # Draw method
    def draw(self, screen):
        if self.tribe == 'rock':
            screen.blit(rock_icon, (self.x - ICON_WIDTH//2, self.y - ICON_HEIGHT//2))
        elif self.tribe == 'paper':
            screen.blit(paper_icon, (self.x - ICON_WIDTH//2, self.y - ICON_HEIGHT//2))
        elif self.tribe == 'scissors':
            screen.blit(scissors_icon, (self.x - ICON_WIDTH//2, self.y - ICON_HEIGHT//2))

    # Edge avoidance method
    def avoid_edges(self):
        if self.x < EDGE_AVOID_RADIUS :
            self.move_towards(self.x + EDGE_AVOID_RADIUS, self.y)
        elif self.x > WINDOW_WIDTH - EDGE_AVOID_RADIUS:
            self.move_towards(self.x - EDGE_AVOID_RADIUS, self.y)
        if self.y < EDGE_AVOID_RADIUS :
            self.move_towards(self.x, self.y + EDGE_AVOID_RADIUS)
        elif self.y > WINDOW_HEIGHT - EDGE_AVOID_RADIUS:
            self.move_towards(self.x, self.y - EDGE_AVOID_RADIUS)

# Initialize entities
entities = [Entity(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), 'rock') for _ in range(50)] + \
           [Entity(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), 'paper') for _ in range(50)] + \
           [Entity(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), 'scissors') for _ in range(50)]

# Adjust movement function
def adjust_movement(screen):
    for entity in entities:
        if entity.tribe == 'rock':
            targets = [e for e in entities if e.tribe == 'scissors']
            threats = [e for e in entities if e.tribe == 'paper']
        elif entity.tribe == 'paper':
            targets = [e for e in entities if e.tribe == 'rock']
            threats = [e for e in entities if e.tribe == 'scissors']
        else:
            targets = [e for e in entities if e.tribe == 'paper']
            threats = [e for e in entities if e.tribe == 'rock']

        # Repel from same tribe
        for other in entities:
            if entity != other and entity.tribe == other.tribe:
                entity.repel_from(other)
        # Find closest target and threat
        closest_target = min(targets, key=entity.distance_to, default=None)
        closest_threat = min(threats, key=entity.distance_to, default=None)
        # Decide movement
        if closest_threat and entity.distance_to(closest_threat) < DETECTION_RADIUS:
            entity.move_away_from(closest_threat.x, closest_threat.y)
        elif closest_target and entity.distance_to(closest_target) < DETECTION_RADIUS:
            entity.move_towards(closest_target.x, closest_target.y)
            if entity.distance_to(closest_target) < CONVERSION_RADIUS:
                closest_target.tribe = entity.tribe
        else:
            entity.move_towards(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT))

        entity.draw(screen)

running = True

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background_image, (0, 0)) # Draw background
    adjust_movement(screen) # handles logic for how entities move, chase, and flees.

    rock_count = sum(1 for entity in entities if entity.tribe == 'rock') 
    paper_count = sum(1 for entity in entities if entity.tribe == 'paper') 
    scissors_count = sum(1 for entity in entities if entity.tribe == 'scissors')

    # Check for winner
    winner_text = None
    if rock_count == len(entities):
        winner_text = "Rock"
    elif paper_count == len(entities):
        winner_text = "Paper"
    elif scissors_count == len(entities):
        winner_text = "Scissors"
    
    # Display winner
    if winner_text:
        pygame.font.init()
        font_large = pygame.font.Font(None, 100)
        font_small = pygame.font.Font(None, 74)

        winner_title_surface = font_large.render("Winner!", True, pygame.Color("#6aff9b"))
        tribe_name_surface = font_small.render(winner_text, True, (255, 255, 255))

        padding = 20
        box_width = max(winner_title_surface.get_width(), tribe_name_surface.get_width()) + 2 * padding
        box_height = winner_title_surface.get_height() + tribe_name_surface.get_height() + 3 * padding

        pygame.draw.rect(screen, (0, 0, 0), (WINDOW_WIDTH // 2 - box_width // 2, WINDOW_HEIGHT // 2 - box_height // 2, box_width, box_height))
        screen.blit(winner_title_surface, (WINDOW_WIDTH // 2 - winner_title_surface.get_width() // 2, WINDOW_HEIGHT // 2 - box_height // 2 + padding))
        screen.blit(tribe_name_surface, (WINDOW_WIDTH // 2 - tribe_name_surface.get_width() // 2, WINDOW_HEIGHT // 2 + padding))

        pygame.display.flip() # Update display to show winner
        pygame.time.wait(3000)
        running = False

    pygame.display.flip() # Update display
    clock.tick(60)

pygame.quit() 