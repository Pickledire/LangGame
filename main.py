import pygame
import random
import os
import sys
import json
from collections import defaultdict
import math

# Initialize Pygame
pygame.init()

# Get screen info for fullscreen mode
screen_info = pygame.display.Info()
FULLSCREEN_WIDTH = screen_info.current_w
FULLSCREEN_HEIGHT = screen_info.current_h

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 144  # Increased FPS for smoother gameplay
FULLSCREEN = True  # Flag to control fullscreen mode
CHUNK_SIZE = 16  # Number of tiles in a chunk (16x16)

# Window mode constants
WINDOW_MODE_WINDOWED = 0
WINDOW_MODE_FULLSCREEN = 1
WINDOW_MODE_BORDERLESS = 2
CURRENT_WINDOW_MODE = WINDOW_MODE_FULLSCREEN  # Default window mode

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (76, 187, 23)  # Brighter green for better visibility
BLUE = (30, 144, 255)  # Dodger blue - more vibrant
RED = (255, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)  # For stone highlights and details
YELLOW = (255, 255, 0)
BROWN = (160, 82, 45)  # Richer brown color
LIGHT_BROWN = (205, 133, 63)  # For tree trunks
DARK_BROWN = (101, 67, 33)  # Darker brown for doors and details
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (144, 238, 144)  # For grass details
LIGHT_YELLOW = (255, 255, 153)
CYAN = (0, 255, 255)
ORANGE = (255, 140, 0)  # Darker orange for better contrast
PINK = (255, 105, 180)  # Hot pink for flowers
FOREST_GREEN = (34, 139, 34)  # For tree leaves
SAND_COLOR = (238, 214, 175)  # For beaches
LAVENDER = (230, 230, 250)  # For rabbits and other animals
PURPLE = (147, 112, 219)  # For flowers variation

# Game objects/items with translations
GAME_OBJECTS = [
    {"name": "tree", "english": "tree", "spanish": "árbol", "french": "arbre", "color": FOREST_GREEN, "passable": False},
    {"name": "water", "english": "water", "spanish": "agua", "french": "eau", "color": BLUE, "passable": False},
    {"name": "stone", "english": "stone", "spanish": "piedra", "french": "pierre", "color": GRAY, "passable": False},
    {"name": "house", "english": "house", "spanish": "casa", "french": "maison", "color": BROWN, "passable": False},
    {"name": "grass", "english": "grass", "spanish": "hierba", "french": "herbe", "color": GREEN, "passable": True},
    {"name": "path", "english": "path", "spanish": "camino", "french": "chemin", "color": SAND_COLOR, "passable": True},
    {"name": "flower", "english": "flower", "spanish": "flor", "french": "fleur", "color": PINK, "passable": True},
    {"name": "mushroom", "english": "mushroom", "spanish": "hongo", "french": "champignon", "color": (255, 182, 193), "passable": True},
    {"name": "log", "english": "log", "spanish": "tronco", "french": "bûche", "color": LIGHT_BROWN, "passable": False},
    {"name": "bush", "english": "bush", "spanish": "arbusto", "french": "buisson", "color": GREEN, "passable": False},
    {"name": "rabbit", "english": "rabbit", "spanish": "conejo", "french": "lapin", "color": LAVENDER, "passable": True},
    {"name": "bird", "english": "bird", "spanish": "pájaro", "french": "oiseau", "color": ORANGE, "passable": True},
]

# Languages available
LANGUAGES = ["spanish", "french"]

# Direction constants
DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

class Chunk:
    """A chunk is a section of the game world"""
    def __init__(self, chunk_x, chunk_y):
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.tiles = []
        self.objects = []
        
        # Generate tiles for this chunk
        self.generate_tiles()
        
    def generate_tiles(self):
        """Generate the tiles for this chunk"""
        # Start with all grass
        self.tiles = [[next(obj for obj in GAME_OBJECTS if obj["name"] == "grass") 
                      for _ in range(CHUNK_SIZE)] for _ in range(CHUNK_SIZE)]
        
        # Set a random seed based on chunk position for consistent generation
        random.seed(f"{self.chunk_x}-{self.chunk_y}")
        
        # Add features based on chunk position
        self.generate_features()
        
        # Reset random seed
        random.seed()
        
    def generate_features(self):
        """Generate features like paths, water, trees, etc. based on chunk position"""
        # Determine if this chunk should have a path (based on proximity to origin)
        if abs(self.chunk_x) <= 2 or abs(self.chunk_y) <= 2:
            self.generate_path()
            
        # Add trees
        if random.random() < 0.7:  # 70% chance of trees in a chunk
            self.generate_trees()
            
        # Add water
        if random.random() < 0.4:  # 40% chance of water in a chunk
            self.generate_water()
            
        # Add houses (mostly near paths)
        if (abs(self.chunk_x) <= 3 and abs(self.chunk_y) <= 3) or random.random() < 0.2:
            self.generate_houses()
            
        # Add logs and bushes
        if random.random() < 0.6:  # 60% chance of logs and bushes
            self.generate_forest_elements()
            
        # Add animals (rabbits and birds)
        if random.random() < 0.4:  # 40% chance of animals
            self.generate_animals()
            
    def generate_path(self):
        """Generate a path through this chunk"""
        path_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "path")
        
        # Determine path direction (horizontal, vertical, or both)
        path_type = random.choice(["horizontal", "vertical", "both"])
        
        if path_type in ["horizontal", "both"]:
            y = random.randint(CHUNK_SIZE // 4, 3 * CHUNK_SIZE // 4)
            for x in range(CHUNK_SIZE):
                self.tiles[y][x] = path_obj
                
        if path_type in ["vertical", "both"]:
            x = random.randint(CHUNK_SIZE // 4, 3 * CHUNK_SIZE // 4)
            for y in range(CHUNK_SIZE):
                self.tiles[y][x] = path_obj
    
    def generate_trees(self):
        """Generate trees in this chunk"""
        tree_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "tree")
        
        # Create a few tree clusters
        for _ in range(random.randint(1, 3)):
            center_x = random.randint(2, CHUNK_SIZE - 3)
            center_y = random.randint(2, CHUNK_SIZE - 3)
            radius = random.randint(2, 4)
            
            for y in range(max(0, center_y - radius), min(CHUNK_SIZE, center_y + radius)):
                for x in range(max(0, center_x - radius), min(CHUNK_SIZE, center_x + radius)):
                    # Skip if it's not grass
                    if self.tiles[y][x]["name"] != "grass":
                        continue
                    
                    # Create an irregular forest
                    if random.random() < 0.6 and (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        self.tiles[y][x] = tree_obj
    
    def generate_water(self):
        """Generate water in this chunk"""
        water_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "water")
        
        # Create a water body
        center_x = random.randint(3, CHUNK_SIZE - 4)
        center_y = random.randint(3, CHUNK_SIZE - 4)
        radius = random.randint(2, 5)
        
        for y in range(max(0, center_y - radius), min(CHUNK_SIZE, center_y + radius)):
            for x in range(max(0, center_x - radius), min(CHUNK_SIZE, center_x + radius)):
                # Create an irregular shape
                if random.random() < 0.7 and (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                    self.tiles[y][x] = water_obj
    
    def generate_houses(self):
        """Generate houses in this chunk"""
        house_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "house")
        flower_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "flower")
        
        # Add houses (preferably near paths)
        for _ in range(random.randint(0, 3)):
            # Find a good spot for a house (near path if possible)
            for attempt in range(10):  # Try 10 times to find a good spot
                x = random.randint(1, CHUNK_SIZE - 2)
                y = random.randint(1, CHUNK_SIZE - 2)
                
                # Check if there's a path nearby
                has_path_nearby = False
                for ny in range(max(0, y - 1), min(CHUNK_SIZE, y + 2)):
                    for nx in range(max(0, x - 1), min(CHUNK_SIZE, x + 2)):
                        if self.tiles[ny][nx]["name"] == "path":
                            has_path_nearby = True
                            break
                    if has_path_nearby:
                        break
                
                # If this is a good spot, place the house
                if (has_path_nearby or attempt > 5) and self.tiles[y][x]["name"] not in ["water", "path", "house"]:
                    self.tiles[y][x] = house_obj
                    
                    # Add flowers around house
                    for ny in range(max(0, y - 1), min(CHUNK_SIZE, y + 2)):
                        for nx in range(max(0, x - 1), min(CHUNK_SIZE, x + 2)):
                            if (nx != x or ny != y) and self.tiles[ny][nx]["name"] == "grass" and random.random() < 0.4:
                                self.tiles[ny][nx] = flower_obj
                    break
    
    def generate_forest_elements(self):
        """Generate logs, bushes, and other forest elements"""
        log_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "log")
        bush_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "bush")
        
        # Add logs (mainly in forested areas)
        num_logs = random.randint(0, 3)
        for _ in range(num_logs):
            # Try to place log near trees
            for attempt in range(5):
                x = random.randint(0, CHUNK_SIZE - 1)
                y = random.randint(0, CHUNK_SIZE - 1)
                
                # Check if there's a tree nearby
                tree_nearby = False
                for ny in range(max(0, y - 1), min(CHUNK_SIZE, y + 2)):
                    for nx in range(max(0, x - 1), min(CHUNK_SIZE, x + 2)):
                        if self.tiles[ny][nx]["name"] == "tree":
                            tree_nearby = True
                            break
                    if tree_nearby:
                        break
                
                # Place log if near tree or after multiple attempts
                if (tree_nearby or attempt > 3) and self.tiles[y][x]["name"] == "grass":
                    self.tiles[y][x] = log_obj
                    break
        
        # Add bushes
        num_bushes = random.randint(1, 5)
        for _ in range(num_bushes):
            # Bushes can appear anywhere on grass
            for attempt in range(5):
                x = random.randint(0, CHUNK_SIZE - 1)
                y = random.randint(0, CHUNK_SIZE - 1)
                
                if self.tiles[y][x]["name"] == "grass":
                    self.tiles[y][x] = bush_obj
                    break
                    
    def generate_animals(self):
        """Generate animals in the chunk"""
        rabbit_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "rabbit")
        bird_obj = next(obj for obj in GAME_OBJECTS if obj["name"] == "bird")
        
        # Add rabbits
        num_rabbits = random.randint(0, 2)
        for _ in range(num_rabbits):
            for attempt in range(5):
                x = random.randint(0, CHUNK_SIZE - 1)
                y = random.randint(0, CHUNK_SIZE - 1)
                
                if self.tiles[y][x]["name"] == "grass":
                    self.tiles[y][x] = rabbit_obj
                    break
        
        # Add birds - more likely in trees or on grass
        num_birds = random.randint(0, 2)
        for _ in range(num_birds):
            bird_in_tree = random.random() < 0.5
            
            for attempt in range(5):
                x = random.randint(0, CHUNK_SIZE - 1)
                y = random.randint(0, CHUNK_SIZE - 1)
                
                if bird_in_tree and self.tiles[y][x]["name"] == "tree":
                    # Bird will be displayed in the tree at this position
                    self.tiles[y][x] = bird_obj
                    break
                elif not bird_in_tree and self.tiles[y][x]["name"] == "grass":
                    # Bird on the ground
                    self.tiles[y][x] = bird_obj
                    break
    
    def get_tile(self, local_x, local_y):
        """Get the tile at the local position within the chunk"""
        if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
            return self.tiles[local_y][local_x]
        return None
    
    def get_world_position(self, local_x, local_y):
        """Convert local position to world position"""
        world_x = (self.chunk_x * CHUNK_SIZE) + local_x
        world_y = (self.chunk_y * CHUNK_SIZE) + local_y
        return world_x, world_y
    
    def create_game_objects(self):
        """Create game objects from the tiles in this chunk"""
        self.objects = []
        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                world_x, world_y = self.get_world_position(x, y)
                self.objects.append(GameObject(world_x * TILE_SIZE, world_y * TILE_SIZE, self.tiles[y][x]))
        return self.objects
        
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.normal_speed = 3  # Reduced from 5 for better control
        self.sprint_speed = 8  # Fast movement when sprinting
        self.speed = self.normal_speed
        self.color = (255, 0, 0)  # Red
        self.score = 0
        self.words_learned = defaultdict(dict)  # Track learned words by language
        self.direction = DIRECTION_DOWN  # Default direction is down
        # World position in tiles
        self.tile_x = x // TILE_SIZE
        self.tile_y = y // TILE_SIZE
        # Chunk position
        self.chunk_x = self.tile_x // CHUNK_SIZE
        self.chunk_y = self.tile_y // CHUNK_SIZE
        # Clothing colors
        self.shirt_color = (50, 100, 200)  # Blue shirt
        self.pants_color = (30, 30, 100)   # Dark blue pants
        self.skin_color = (255, 213, 170)  # Light skin tone
        # Animation state
        self.animation_frame = 0
        self.is_moving = False
        self.animation_speed = 8  # Frames before animation changes
        self.animation_counter = 0
        # Interaction indicator
        self.interaction_target = None
        # Camera offset for mouse interaction
        self.camera_offset_x = 0
        self.camera_offset_y = 0

    def move(self, dx, dy, world, is_sprinting=False):
        # Apply sprint speed if shift is pressed
        if is_sprinting:
            self.speed = self.sprint_speed
        else:
            self.speed = self.normal_speed
            
        # Track if moving for animation
        self.is_moving = (dx != 0 or dy != 0)
        
        # Update animation counter if moving
        if self.is_moving:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            # Reset animation when standing still
            self.animation_frame = 0
            self.animation_counter = 0
            
        # Update player direction based on movement
        if dx > 0:
            self.direction = DIRECTION_RIGHT
        elif dx < 0:
            self.direction = DIRECTION_LEFT
        elif dy > 0:
            self.direction = DIRECTION_DOWN
        elif dy < 0:
            self.direction = DIRECTION_UP
        
        # Check boundaries before moving
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Get the screen dimensions (may be fullscreen or windowed)
        screen_w = FULLSCREEN_WIDTH if FULLSCREEN else SCREEN_WIDTH
        screen_h = FULLSCREEN_HEIGHT if FULLSCREEN else SCREEN_HEIGHT
        
        # Get the new tile position
        new_tile_x = new_x // TILE_SIZE
        new_tile_y = new_y // TILE_SIZE
        
        # Check if the tile is passable
        if world.is_tile_passable(new_tile_x, new_tile_y):
            self.x = new_x
            self.y = new_y
            
            # Update tile and chunk position
            self.tile_x = new_tile_x
            self.tile_y = new_tile_y
            self.chunk_x = self.tile_x // CHUNK_SIZE
            self.chunk_y = self.tile_y // CHUNK_SIZE
            
        # Update the interaction target
        self.update_interaction_target(world)
        
    def update_interaction_target(self, world):
        """Update the object the player is currently facing/would interact with"""
        facing_x, facing_y = self.get_facing_tile_position()
        self.interaction_target = world.get_object_at_tile(facing_x, facing_y)
        
        # Add a range attribute to track the maximum interaction distance
        self.interaction_range = 150  # Maximum distance in pixels for interaction
    
    def draw(self, screen, offset_x, offset_y):
        # Calculate the screen position
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        
        head_radius = self.width // 4
        
        # Get animation offsets for walking
        leg_offset = 0
        if self.is_moving:
            if self.animation_frame == 1:
                leg_offset = 2
            elif self.animation_frame == 3:
                leg_offset = -2
        
        # Draw the player as a person-like character based on direction
        if self.direction == DIRECTION_UP:
            # Back view
            # Body/shirt
            pygame.draw.rect(screen, self.shirt_color, 
                           (screen_x + self.width // 4, screen_y + self.height // 3, 
                            self.width // 2, self.height // 2))
            
            # Head
            pygame.draw.circle(screen, self.skin_color, 
                             (screen_x + self.width // 2, screen_y + self.height // 4), 
                             head_radius)
            
            # Hair
            pygame.draw.arc(screen, (50, 25, 0), 
                          (screen_x + self.width // 2 - head_radius, screen_y + self.height // 4 - head_radius, 
                           head_radius * 2, head_radius * 2), 
                          3.14, 0, 3)
            
            # Legs with animation - closer together for up view
            leg_width = self.width // 6
            center_x = screen_x + self.width // 2
            leg_spacing = 4 + abs(leg_offset)  # Legs move closer/further based on animation
            
            # Left leg 
            pygame.draw.rect(screen, self.pants_color, 
                           (center_x - leg_spacing - leg_width, 
                            screen_y + self.height // 3 + self.height // 2, 
                            leg_width, self.height // 4))
            # Right leg
            pygame.draw.rect(screen, self.pants_color, 
                           (center_x + leg_spacing, 
                            screen_y + self.height // 3 + self.height // 2, 
                            leg_width, self.height // 4))
        
        elif self.direction == DIRECTION_RIGHT:
            # Right view
            # Body/shirt
            pygame.draw.rect(screen, self.shirt_color, 
                           (screen_x + self.width // 4, screen_y + self.height // 3, 
                            self.width // 2, self.height // 2))
            
            # Head
            pygame.draw.circle(screen, self.skin_color, 
                             (screen_x + self.width // 2 + head_radius // 2, screen_y + self.height // 4), 
                             head_radius)
            
            # Face details
            eye_x = screen_x + self.width // 2 + head_radius // 2 + head_radius // 3
            eye_y = screen_y + self.height // 4 - head_radius // 4
            pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)
            
            # Mouth
            pygame.draw.arc(screen, BLACK, 
                          (eye_x - head_radius // 2, eye_y + head_radius // 4, 
                           head_radius // 2, head_radius // 2), 
                          0, 3.14, 1)
            
            # Legs with animation - for side view, just shift leg position for walking effect
            leg_y_offset = abs(leg_offset) if leg_offset else 0
            pygame.draw.rect(screen, self.pants_color, 
                           (screen_x + self.width // 3, 
                            screen_y + self.height // 3 + self.height // 2 - leg_y_offset, 
                            self.width // 3, self.height // 4 + leg_y_offset))
            
            # Arm with animation
            arm_y = screen_y + self.height // 3 + self.height // 6
            if leg_offset > 0:  # Swing arm opposite to leg
                arm_y += 2
            elif leg_offset < 0:
                arm_y -= 2
                
            pygame.draw.line(screen, self.shirt_color, 
                           (screen_x + self.width // 4 + self.width // 4, arm_y), 
                           (screen_x + self.width // 4 + self.width // 2, arm_y + self.height // 8), 
                           4)
        
        elif self.direction == DIRECTION_DOWN:
            # Front view
            # Body/shirt
            pygame.draw.rect(screen, self.shirt_color, 
                           (screen_x + self.width // 4, screen_y + self.height // 3, 
                            self.width // 2, self.height // 2))
            
            # Head
            pygame.draw.circle(screen, self.skin_color, 
                             (screen_x + self.width // 2, screen_y + self.height // 4), 
                             head_radius)
            
            # Face details
            eye_spacing = head_radius // 2
            eye_y = screen_y + self.height // 4 - 1
            # Left eye
            pygame.draw.circle(screen, BLACK, 
                             (screen_x + self.width // 2 - eye_spacing // 2, eye_y), 
                             2)
            # Right eye
            pygame.draw.circle(screen, BLACK, 
                             (screen_x + self.width // 2 + eye_spacing // 2, eye_y), 
                             2)
            
            # Smile
            pygame.draw.arc(screen, BLACK, 
                          (screen_x + self.width // 2 - eye_spacing // 2, eye_y, 
                           eye_spacing, head_radius // 2), 
                          0, 3.14, 1)
            
            # Hair
            pygame.draw.arc(screen, (50, 25, 0), 
                          (screen_x + self.width // 2 - head_radius, screen_y + self.height // 4 - head_radius, 
                           head_radius * 2, head_radius), 
                          3.14, 0, 3)
            
            # Legs with animation - closer together for down view
            leg_width = self.width // 6
            center_x = screen_x + self.width // 2
            leg_spacing = 4 + abs(leg_offset)  # Legs move closer/further based on animation
            
            # Left leg
            pygame.draw.rect(screen, self.pants_color, 
                           (center_x - leg_spacing - leg_width, 
                            screen_y + self.height // 3 + self.height // 2, 
                            leg_width, self.height // 4))
            # Right leg
            pygame.draw.rect(screen, self.pants_color, 
                           (center_x + leg_spacing, 
                            screen_y + self.height // 3 + self.height // 2, 
                            leg_width, self.height // 4))
        
        elif self.direction == DIRECTION_LEFT:
            # Left view
            # Body/shirt
            pygame.draw.rect(screen, self.shirt_color, 
                           (screen_x + self.width // 4, screen_y + self.height // 3, 
                            self.width // 2, self.height // 2))
            
            # Head
            pygame.draw.circle(screen, self.skin_color, 
                             (screen_x + self.width // 2 - head_radius // 2, screen_y + self.height // 4), 
                             head_radius)
            
            # Face details
            eye_x = screen_x + self.width // 2 - head_radius // 2 - head_radius // 3
            eye_y = screen_y + self.height // 4 - head_radius // 4
            pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)
            
            # Mouth
            pygame.draw.arc(screen, BLACK, 
                          (eye_x, eye_y + head_radius // 4, 
                           head_radius // 2, head_radius // 2), 
                          0, 3.14, 1)
            
            # Legs with animation - for side view, just shift leg position for walking effect
            leg_y_offset = abs(leg_offset) if leg_offset else 0
            pygame.draw.rect(screen, self.pants_color, 
                           (screen_x + self.width // 3, 
                            screen_y + self.height // 3 + self.height // 2 - leg_y_offset, 
                            self.width // 3, self.height // 4 + leg_y_offset))
            
            # Arm with animation
            arm_y = screen_y + self.height // 3 + self.height // 6
            if leg_offset > 0:  # Swing arm opposite to leg
                arm_y += 2
            elif leg_offset < 0:
                arm_y -= 2
                
            pygame.draw.line(screen, self.shirt_color, 
                           (screen_x + self.width // 4 + self.width // 4, arm_y), 
                           (screen_x + self.width // 4, arm_y + self.height // 8), 
                           4)
    
    def learn_word(self, obj_type, language):
        """Track that player has learned a word"""
        word = obj_type[language]
        english = obj_type["english"]
        name = obj_type["name"]
        
        # Update word learning count
        if name not in self.words_learned[language]:
            self.words_learned[language][name] = {
                "word": word,
                "english": english,
                "views": 1,
                "mastered": False
            }
            # First time bonus
            self.score += 10
        else:
            self.words_learned[language][name]["views"] += 1
            # Learning progress
            if self.words_learned[language][name]["views"] >= 5 and not self.words_learned[language][name]["mastered"]:
                self.words_learned[language][name]["mastered"] = True
                self.score += 50  # Mastery bonus
            elif not self.words_learned[language][name]["mastered"]:
                self.score += 2  # Regular learning bonus
        
        return self.words_learned[language][name]
    
    def get_mastery_percentage(self, language):
        """Calculate mastery percentage for a language"""
        if language not in self.words_learned or len(self.words_learned[language]) == 0:
            return 0
        
        total_words = len(self.words_learned[language])
        mastered_words = sum(1 for word_data in self.words_learned[language].values() if word_data["mastered"])
        
        return (mastered_words / total_words) * 100
    
    def get_facing_tile_position(self):
        """Get the tile position the player is facing"""
        # Get the mouse position relative to the screen
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert screen position to world position
        # These will be updated in the Game class when drawing
        world_mouse_x = mouse_x + self.camera_offset_x
        world_mouse_y = mouse_y + self.camera_offset_y
        
        # Calculate direction from player to mouse
        dx = world_mouse_x - (self.x + self.width // 2)
        dy = world_mouse_y - (self.y + self.height // 2)
        
        # Update player's facing direction based on mouse position
        if abs(dx) > abs(dy):
            if dx > 0:
                self.direction = DIRECTION_RIGHT
            else:
                self.direction = DIRECTION_LEFT
        else:
            if dy > 0:
                self.direction = DIRECTION_DOWN
            else:
                self.direction = DIRECTION_UP
        
        # Convert world mouse position to tile position
        tile_x = world_mouse_x // TILE_SIZE
        tile_y = world_mouse_y // TILE_SIZE
        
        return (tile_x, tile_y)

class GameObject:
    def __init__(self, x, y, obj_type):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.obj_type = obj_type
        self.color = obj_type["color"]
        self.revealed = False
        self.translation_shown = False
        self.mastered = False  # Tracks if this object's word has been mastered
        # Random variation for natural-looking objects
        self.variation = random.random()
        
    def get_tile_position(self):
        """Get the tile position of this object"""
        return (self.x // TILE_SIZE, self.y // TILE_SIZE)

    def draw(self, screen, offset_x, offset_y, target_language, words_learned):
        # Calculate screen position
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        
        # Skip if off screen
        screen_w = FULLSCREEN_WIDTH if FULLSCREEN else SCREEN_WIDTH
        screen_h = FULLSCREEN_HEIGHT if FULLSCREEN else SCREEN_HEIGHT
        if (screen_x + self.width < 0 or screen_x > screen_w or
            screen_y + self.height < 0 or screen_y > screen_h):
            return
        
        # Background tile
        if self.obj_type["name"] == "grass":
            # Add slight variation to grass color
            var_color = (
                max(0, min(255, self.color[0] - 15 + int(30 * self.variation))),
                max(0, min(255, self.color[1] - 15 + int(30 * self.variation))),
                max(0, min(255, self.color[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Use a global grass texture cache to improve performance
            # Create the cache if it doesn't exist
            if not hasattr(GameObject, '_grass_texture_cache'):
                GameObject._grass_texture_cache = {}
            
            # Create a cache key based on position (this ensures consistent patterns)
            cache_key = f"{self.x}_{self.y}"
            
            # Use cached texture if available
            if cache_key not in GameObject._grass_texture_cache:
                # Create a fixed pattern based on tile position
                seed_value = int(self.x) + int(self.y)  # Use position as seed
                random.seed(seed_value)  # Set seed for consistent appearance
                
                # Create a new surface with transparency for the patches
                texture = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Add small patches of lighter grass for texture
                num_patches = 3 + int(self.variation * 3)
                for i in range(num_patches):
                    patch_x = int(random.random() * self.width * 0.8) + self.width * 0.1
                    patch_y = int(random.random() * self.height * 0.8) + self.height * 0.1
                    patch_size = 2 + int(random.random() * 3)
                    
                    # Slightly lighter green for the patches
                    patch_color = (
                        min(255, var_color[0] + 20),
                        min(255, var_color[1] + 20),
                        min(255, var_color[2] + 10),
                        255  # Fully opaque
                    )
                    
                    pygame.draw.circle(texture, patch_color, (int(patch_x), int(patch_y)), patch_size)
                
                # Store texture in cache
                GameObject._grass_texture_cache[cache_key] = texture
                
                # Reset random seed
                random.seed()
            
            # Draw the cached texture
            screen.blit(GameObject._grass_texture_cache[cache_key], (screen_x, screen_y))
            
        elif self.obj_type["name"] == "path":
            # Draw main path
            pygame.draw.rect(screen, self.color, (screen_x, screen_y, self.width, self.height))
            
            # Add texture with small stones and variation
            for i in range(6):
                stone_x = screen_x + 3 + int(self.variation * 15) + (i * 5)
                stone_y = screen_y + 5 + int(self.variation * 20)
                stone_size = 1 + int(self.variation * 3)
                stone_color = (
                    max(0, min(255, LIGHT_GRAY[0] - 20 + int(40 * random.random()))),
                    max(0, min(255, LIGHT_GRAY[1] - 20 + int(40 * random.random()))),
                    max(0, min(255, LIGHT_GRAY[2] - 20 + int(40 * random.random())))
                )
                pygame.draw.circle(screen, stone_color, (stone_x, stone_y), stone_size)
        
        elif self.obj_type["name"] == "water":
            # Base water tile with gradient
            base_color = (max(0, self.color[0] - 20), max(0, self.color[1] - 20), self.color[2])
            pygame.draw.rect(screen, base_color, (screen_x, screen_y, self.width, self.height))
            
            # Add wave details with light blue and animation
            wave_period = pygame.time.get_ticks() // 150  # Faster animation
            
            # Multiple waves with varying sizes
            for i in range(4):
                wave_y = 5 + (i * 7) + (wave_period % 8)
                wave_width = self.width * 0.8
                wave_height = 2 + int(self.variation * 3)
                wave_x = screen_x + (self.width - wave_width) // 2
                
                # Alternate between different shades of blue for waves
                wave_color = LIGHT_BLUE if i % 2 == 0 else (140, 210, 240)
                
                pygame.draw.arc(screen, wave_color, 
                               (wave_x, screen_y + wave_y, 
                                wave_width, wave_height * 2), 
                               0, 3.14, 2)
                
            # Add sparkle effect occasionally
            if (wave_period % 20) < 3:  # Only show sparkles occasionally
                sparkle_x = screen_x + 5 + int(random.random() * (self.width - 10))
                sparkle_y = screen_y + 5 + int(random.random() * (self.height - 10))
                pygame.draw.circle(screen, (240, 240, 255), (sparkle_x, sparkle_y), 1)
        
        # Draw custom shapes based on object type
        elif self.obj_type["name"] == "tree":
            # Tree trunk
            trunk_width = self.width // 3
            trunk_height = self.height * 0.6
            trunk_x = screen_x + (self.width - trunk_width) // 2
            trunk_y = screen_y + self.height - trunk_height
            
            # Draw trunk with wood grain texture
            trunk_color = (139, 69, 19)  # Brown
            pygame.draw.rect(screen, trunk_color, (trunk_x, trunk_y, trunk_width, trunk_height))
            
            # Add wood grain details
            grain_color = (120, 60, 15)  # Darker brown
            for i in range(3):
                grain_y = trunk_y + 5 + i * (trunk_height - 10) // 3
                grain_curve = 2 + int(self.variation * 3)
                pygame.draw.line(screen, grain_color, 
                               (trunk_x, grain_y + grain_curve),
                               (trunk_x + trunk_width, grain_y - grain_curve),
                               1)
            
            # Highlight on one side of trunk
            pygame.draw.line(screen, (160, 82, 45),  # Lighter brown
                           (trunk_x + trunk_width - 2, trunk_y),
                           (trunk_x + trunk_width - 2, trunk_y + trunk_height),
                           2)
            
            # Tree foliage - different shapes based on variation
            if self.variation < 0.4:
                # Pine tree - triangular shape
                for i in range(3):  # Multiple layers of foliage
                    foliage_width = self.width - (i * 4)
                    foliage_height = self.height * 0.35 - (i * 2)
                    foliage_x = screen_x + (self.width - foliage_width) // 2
                    foliage_y = screen_y + (i * self.height * 0.15)
                    
                    # Slightly different greens for each layer
                    pine_color = (
                        max(0, min(255, FOREST_GREEN[0] - 5 + i * 15)),
                        max(0, min(255, FOREST_GREEN[1] - 5 + i * 15)),
                        max(0, min(255, FOREST_GREEN[2] - 5 + i * 10))
                    )
                    
                    # Draw triangle
                    pygame.draw.polygon(screen, pine_color, [
                        (foliage_x, foliage_y + foliage_height),
                        (foliage_x + foliage_width, foliage_y + foliage_height),
                        (foliage_x + foliage_width // 2, foliage_y)
                    ])
                    
                    # Add highlight/texture
                    highlight_color = (
                        min(255, pine_color[0] + 20),
                        min(255, pine_color[1] + 20),
                        min(255, pine_color[2] + 10)
                    )
                    pygame.draw.line(screen, highlight_color,
                                   (foliage_x + foliage_width // 2, foliage_y),
                                   (foliage_x + foliage_width // 2, foliage_y + foliage_height),
                                   1)
            
            else:
                # Bushy tree - multiple circles
                center_x = trunk_x + trunk_width // 2
                base_y = trunk_y
                
                # Different greens for visual interest
                foliage_colors = [
                    (FOREST_GREEN[0] - 10, FOREST_GREEN[1] - 20, FOREST_GREEN[2] - 5),  # Darker green
                    FOREST_GREEN,  # Base forest green
                    (FOREST_GREEN[0] + 20, FOREST_GREEN[1] + 30, FOREST_GREEN[2] + 10)  # Lighter green
                ]
                
                # Large base circles
                circle_sizes = [self.width * 0.55, self.width * 0.5, self.width * 0.45]
                for i, size in enumerate(circle_sizes):
                    center_y = base_y - self.height * 0.2 - (i * self.height * 0.1)
                    
                    # Draw main foliage circle
                    pygame.draw.circle(screen, foliage_colors[i % len(foliage_colors)], 
                                     (int(center_x), int(center_y)), 
                                     int(size))
                    
                    # Add highlights - small lighter patches
                    if i < 2:  # Only on the bottom two circles
                        highlight_positions = [
                            (0.3, 0.3), (0.7, 0.4), (0.5, 0.7)
                        ]
                        for h_pos in highlight_positions:
                            h_x = center_x + (h_pos[0] - 0.5) * size * 1.2
                            h_y = center_y + (h_pos[1] - 0.5) * size * 1.2
                            h_size = size * 0.2
                            
                            highlight_color = (
                                min(255, foliage_colors[i][0] + 30),
                                min(255, foliage_colors[i][1] + 30),
                                min(255, foliage_colors[i][2] + 15)
                            )
                            pygame.draw.circle(screen, highlight_color, 
                                             (int(h_x), int(h_y)), 
                                             int(h_size))
        
        elif self.obj_type["name"] == "house":
            # Draw grass background first
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Make house much bigger with scale factor
            scale = 3.5  # Increased scale for larger houses
            
            # House dimensions
            house_width = int(self.width * scale)
            house_height = int(self.height * scale)
            
            # Center the house on its tile, accounting for large size by extending it to multiple tiles
            house_x = screen_x - (house_width - self.width) // 2
            house_y = screen_y - (house_height - self.height) // 2
            
            # House variations based on the random seed
            house_variation = int(self.variation * 3)  # 0, 1, or 2
            
            # House colors based on variation
            if house_variation == 0:
                wall_color = (180, 130, 80)  # Warm brown
                roof_color = (180, 40, 40)   # Dark red
                trim_color = (100, 70, 30)   # Dark brown trim
            elif house_variation == 1:
                wall_color = (240, 240, 220)  # Off-white/cream
                roof_color = (80, 40, 20)     # Dark brown roof
                trim_color = (140, 90, 40)    # Medium brown trim
            else:
                wall_color = (150, 170, 190)  # Blue-gray
                roof_color = (70, 70, 90)     # Slate gray
                trim_color = (50, 50, 60)     # Dark trim
            
            # House proportions
            roof_height = house_height // 3
            body_height = house_height - roof_height
            
            # House foundation - small darker base
            foundation_height = house_height // 10
            pygame.draw.rect(screen, trim_color, 
                           (house_x - 4, house_y + house_height - foundation_height, 
                            house_width + 8, foundation_height))
            
            # House body with proper proportions
            pygame.draw.rect(screen, wall_color, 
                           (house_x, house_y + roof_height, 
                            house_width, body_height - foundation_height))
            
            # Roof design based on variation
            if house_variation == 0:
                # Traditional triangular roof with overhang
                roof_overhang = house_width // 10
                pygame.draw.polygon(screen, roof_color, [
                    (house_x - roof_overhang, house_y + roof_height), 
                    (house_x + house_width // 2, house_y), 
                    (house_x + house_width + roof_overhang, house_y + roof_height)
                ])
                
                # Roof detail - ridge line
                pygame.draw.line(screen, trim_color, 
                               (house_x + house_width // 2, house_y), 
                               (house_x + house_width // 2, house_y + roof_height), 
                               3)
                
                # Roof trim at the bottom edge
                pygame.draw.line(screen, trim_color, 
                               (house_x - roof_overhang, house_y + roof_height), 
                               (house_x + house_width + roof_overhang, house_y + roof_height), 
                               3)
                
            elif house_variation == 1:
                # Hipped roof (sloped on all sides)
                roof_overhang = house_width // 12
                
                # Main roof surfaces
                pygame.draw.polygon(screen, roof_color, [
                    (house_x - roof_overhang, house_y + roof_height),  # Bottom left
                    (house_x + house_width // 5, house_y + roof_height // 3),  # Mid-left
                    (house_x + house_width // 2, house_y + 5),  # Top middle
                    (house_x + house_width - house_width // 5, house_y + roof_height // 3),  # Mid-right
                    (house_x + house_width + roof_overhang, house_y + roof_height)  # Bottom right
                ])
                
                # Roof trim at bottom edge
                pygame.draw.line(screen, trim_color, 
                               (house_x - roof_overhang, house_y + roof_height), 
                               (house_x + house_width + roof_overhang, house_y + roof_height), 
                               3)
                
                # Roof ridge lines
                pygame.draw.line(screen, trim_color, 
                               (house_x + house_width // 5, house_y + roof_height // 3), 
                               (house_x + house_width // 2, house_y + 5), 
                               2)
                pygame.draw.line(screen, trim_color, 
                               (house_x + house_width // 2, house_y + 5), 
                               (house_x + house_width - house_width // 5, house_y + roof_height // 3), 
                               2)
            else:
                # Modern flat/low-pitched roof with overhang
                roof_overhang = house_width // 8
                
                # Main roof - low pitch
                pygame.draw.polygon(screen, roof_color, [
                    (house_x - roof_overhang, house_y + roof_height),  # Bottom left
                    (house_x, house_y + roof_height // 4),  # Top left
                    (house_x + house_width, house_y + roof_height // 4),  # Top right
                    (house_x + house_width + roof_overhang, house_y + roof_height)  # Bottom right
                ])
                
                # Roof edge detail
                pygame.draw.line(screen, trim_color, 
                               (house_x - roof_overhang, house_y + roof_height), 
                               (house_x + house_width + roof_overhang, house_y + roof_height), 
                               3)
                
                # Modern roof edge cap
                pygame.draw.rect(screen, trim_color, 
                               (house_x - roof_overhang, house_y + roof_height // 4 - 3, 
                                house_width + 2 * roof_overhang, 6))
            
            # Windows based on house variation
            # Window sizing and positioning relative to house size
            window_margin = house_width // 6
            window_width = (house_width - 3 * window_margin) // 2
            window_height = body_height // 3
            window_y = house_y + roof_height + body_height // 4
            
            # Left window coordinates
            left_window_x = house_x + window_margin
            
            # Right window coordinates
            right_window_x = house_x + 2 * window_margin + window_width
            
            # Window colors
            window_color = LIGHT_BLUE
            frame_color = WHITE if house_variation != 2 else trim_color
            
            if house_variation == 2:  # Modern house
                # Tall rectangular windows
                window_height = body_height // 2
                
                # Left window
                # Window frame
                pygame.draw.rect(screen, frame_color, 
                               (left_window_x - 2, window_y - 2, 
                                window_width + 4, window_height + 4))
                # Window glass
                pygame.draw.rect(screen, window_color, 
                               (left_window_x, window_y, 
                                window_width, window_height))
                
                # Simple window divider
                pygame.draw.line(screen, frame_color, 
                               (left_window_x + window_width // 2, window_y), 
                               (left_window_x + window_width // 2, window_y + window_height), 
                               2)
                
                # Right window 
                # Window frame
                pygame.draw.rect(screen, frame_color, 
                               (right_window_x - 2, window_y - 2, 
                                window_width + 4, window_height + 4))
                # Window glass
                pygame.draw.rect(screen, window_color, 
                               (right_window_x, window_y, 
                                window_width, window_height))
                
                # Simple window divider
                pygame.draw.line(screen, frame_color, 
                               (right_window_x + window_width // 2, window_y), 
                               (right_window_x + window_width // 2, window_y + window_height), 
                               2)
                
            else:  # Traditional windows
                # Left window with frame
                # Window frame
                pygame.draw.rect(screen, frame_color, 
                               (left_window_x - 3, window_y - 3, 
                                window_width + 6, window_height + 6))
                # Window glass
                pygame.draw.rect(screen, window_color, 
                               (left_window_x, window_y, 
                                window_width, window_height))
                
                # Window panes - 4 pane classic window
                # Vertical divider
                pygame.draw.line(screen, frame_color, 
                               (left_window_x + window_width // 2, window_y), 
                               (left_window_x + window_width // 2, window_y + window_height), 
                               2)
                # Horizontal divider
                pygame.draw.line(screen, frame_color, 
                               (left_window_x, window_y + window_height // 2), 
                               (left_window_x + window_width, window_y + window_height // 2), 
                               2)
                
                # Right window with frame
                # Window frame
                pygame.draw.rect(screen, frame_color, 
                               (right_window_x - 3, window_y - 3, 
                                window_width + 6, window_height + 6))
                # Window glass
                pygame.draw.rect(screen, window_color, 
                               (right_window_x, window_y, 
                                window_width, window_height))
                
                # Window panes
                # Vertical divider
                pygame.draw.line(screen, frame_color, 
                               (right_window_x + window_width // 2, window_y), 
                               (right_window_x + window_width // 2, window_y + window_height), 
                               2)
                # Horizontal divider
                pygame.draw.line(screen, frame_color, 
                               (right_window_x, window_y + window_height // 2), 
                               (right_window_x + window_width, window_y + window_height // 2), 
                               2)
                
                # Add window sills for traditional houses
                sill_height = 4
                pygame.draw.rect(screen, trim_color, 
                               (left_window_x - 5, window_y + window_height + 1, 
                                window_width + 10, sill_height))
                pygame.draw.rect(screen, trim_color, 
                               (right_window_x - 5, window_y + window_height + 1, 
                                window_width + 10, sill_height))
                
                # Window flower boxes
                if house_variation == 0 and self.variation > 0.5:
                    # Flower box dimensions
                    box_height = window_height // 4
                    
                    # Left window flower box
                    pygame.draw.rect(screen, BROWN, 
                                   (left_window_x - 2, window_y + window_height + sill_height + 1, 
                                    window_width + 4, box_height))
                    
                    # Flowers in left box
                    for i in range(5):
                        flower_x = left_window_x + (i+0.5) * window_width // 5
                        flower_y = window_y + window_height + sill_height + box_height // 2 + 1
                        flower_color = PINK if i % 2 == 0 else RED
                        pygame.draw.circle(screen, flower_color, (int(flower_x), int(flower_y)), 4)
                    
                    # Right window flower box
                    pygame.draw.rect(screen, BROWN, 
                                   (right_window_x - 2, window_y + window_height + sill_height + 1, 
                                    window_width + 4, box_height))
                    
                    # Flowers in right box
                    for i in range(5):
                        flower_x = right_window_x + (i+0.5) * window_width // 5
                        flower_y = window_y + window_height + sill_height + box_height // 2 + 1
                        flower_color = RED if i % 2 == 0 else PINK
                        pygame.draw.circle(screen, flower_color, (int(flower_x), int(flower_y)), 4)
            
            # Door with proper proportions
            door_width = house_width // 4
            door_height = body_height // 2 + body_height // 10
            door_x = house_x + (house_width - door_width) // 2
            door_y = house_y + house_height - door_height - foundation_height // 2
            
            # Door style based on house variation
            if house_variation == 2:  # Modern door
                # Simple rectangular door with minimal detail
                
                # Door frame
                pygame.draw.rect(screen, trim_color, 
                               (door_x - 2, door_y - 2, 
                                door_width + 4, door_height + 4))
                
                # Door
                pygame.draw.rect(screen, (60, 60, 70), 
                               (door_x, door_y, 
                                door_width, door_height))
                
                # Modern handle
                handle_x = door_x + door_width - 8
                handle_y = door_y + door_height // 2
                pygame.draw.rect(screen, LIGHT_GRAY, 
                               (handle_x, handle_y - 15, 
                                4, 30))
                
                # House number
                if self.variation > 0.3:
                    number = int(self.variation * 100)
                    font = pygame.font.SysFont('Arial', int(door_width // 4))
                    num_text = font.render(f"{number}", True, WHITE)
                    screen.blit(num_text, (door_x + door_width // 2 - num_text.get_width() // 2, 
                                              door_y + door_height // 4))
                    
            else:  # Traditional door
                # Classic paneled door
                
                # Door frame
                pygame.draw.rect(screen, trim_color, 
                               (door_x - 3, door_y - 3, 
                                door_width + 6, door_height + 6))
                
                # Door base
                door_color = DARK_BROWN if house_variation == 0 else (120, 60, 20)  # Rich brown
                pygame.draw.rect(screen, door_color, 
                               (door_x, door_y, 
                                door_width, door_height))
                
                # Door panels - 6 panel traditional door
                panel_width = door_width - 6
                small_panel_height = door_height // 5
                large_panel_height = (door_height - 2 * small_panel_height - 12) // 2
                
                # Panel color slightly different from door
                panel_color = (
                    max(0, min(255, door_color[0] - 20)),
                    max(0, min(255, door_color[1] - 10)),
                    max(0, min(255, door_color[2] - 10))
                )
                
                # Top panels
                pygame.draw.rect(screen, panel_color, 
                               (door_x + 3, door_y + 3, 
                                panel_width // 2 - 3, small_panel_height))
                pygame.draw.rect(screen, panel_color, 
                               (door_x + panel_width // 2 + 3, door_y + 3, 
                                panel_width // 2 - 3, small_panel_height))
                
                # Middle panels
                pygame.draw.rect(screen, panel_color, 
                               (door_x + 3, door_y + small_panel_height + 6, 
                                panel_width // 2 - 3, large_panel_height))
                pygame.draw.rect(screen, panel_color, 
                               (door_x + panel_width // 2 + 3, door_y + small_panel_height + 6, 
                                panel_width // 2 - 3, large_panel_height))
                
                # Bottom panels
                pygame.draw.rect(screen, panel_color, 
                               (door_x + 3, door_y + small_panel_height + large_panel_height + 9, 
                                panel_width // 2 - 3, large_panel_height))
                pygame.draw.rect(screen, panel_color, 
                               (door_x + panel_width // 2 + 3, door_y + small_panel_height + large_panel_height + 9, 
                                panel_width // 2 - 3, large_panel_height))
                
                # Doorknob
                doorknob_x = door_x + door_width - door_width // 6
                doorknob_y = door_y + door_height // 2
                pygame.draw.circle(screen, YELLOW, (doorknob_x, doorknob_y), 3)
                
                # Add a small window in the door for variation 1
                if house_variation == 1 and self.variation > 0.4:
                    small_window_width = door_width - 10
                    small_window_height = small_panel_height + 4
                    small_window_x = door_x + 5
                    small_window_y = door_y + 3
                    
                    pygame.draw.rect(screen, LIGHT_BLUE, 
                                   (small_window_x, small_window_y, 
                                    small_window_width, small_window_height))
                    
                    # Window detail
                    pygame.draw.line(screen, door_color, 
                                   (small_window_x + small_window_width // 2, small_window_y), 
                                   (small_window_x + small_window_width // 2, small_window_y + small_window_height), 
                                   1)
            
            # Chimney for traditional houses
            if house_variation < 2 and self.variation > 0.3:
                chimney_width = house_width // 8
                chimney_height = roof_height + chimney_width * 2
                
                # Chimney position varies
                if self.variation > 0.7:
                    # Left side chimney
                    chimney_x = house_x + house_width // 4 - chimney_width // 2
                else:
                    # Right side chimney
                    chimney_x = house_x + house_width - house_width // 4 - chimney_width // 2
                
                # Base chimney height calculation
                if house_variation == 0:
                    # For triangle roof
                    x_ratio = (chimney_x + chimney_width // 2 - house_x) / house_width
                    roof_height_at_chimney = roof_height * (1 - abs(2 * x_ratio - 1))
                    chimney_y = house_y + roof_height_at_chimney - chimney_width
                else:
                    # For hipped roof
                    x_ratio = (chimney_x + chimney_width // 2 - house_x) / house_width
                    roof_height_at_chimney = roof_height * (1 - 0.8 * abs(2 * x_ratio - 1))
                    chimney_y = house_y + roof_height_at_chimney - chimney_width
                
                # Draw chimney
                pygame.draw.rect(screen, wall_color, 
                               (chimney_x, chimney_y, 
                                chimney_width, chimney_height))
                
                # Chimney cap
                chimney_cap_width = chimney_width + 4
                pygame.draw.rect(screen, trim_color, 
                               (chimney_x - 2, chimney_y, 
                                chimney_cap_width, chimney_width // 2))
                
                # Smoke animation (if variation high enough)
                if self.variation > 0.6:
                    time_offset = (pygame.time.get_ticks() // 500) % 4
                    
                    # Smoke colors
                    smoke_color = (220, 220, 220, 150)  # Light gray, semi-transparent
                    
                    # Create smoke surface with transparency
                    smoke_surface = pygame.Surface((chimney_width * 3, chimney_width * 5), pygame.SRCALPHA)
                    
                    # Draw multiple smoke puffs
                    for i in range(3):
                        puff_y = chimney_width * 3 - i * chimney_width - time_offset * 3
                        puff_size = chimney_width * (0.6 + i * 0.2)
                        puff_x = chimney_width + (i % 2) * 4 - 2
                        
                        # Draw only if in visible range
                        if puff_y > 0:
                            pygame.draw.circle(smoke_surface, smoke_color, 
                                             (puff_x, puff_y), 
                                             puff_size)
                    
                    # Apply smoke to screen
                    screen.blit(smoke_surface, 
                                   (chimney_x - chimney_width, chimney_y - chimney_width * 3))
        
        elif self.obj_type["name"] == "stone":
            # Multiple stones for more natural look
            base_size = self.width // 2
            
            # Main large stone
            pygame.draw.ellipse(screen, GRAY, (screen_x + 2, screen_y + self.height - base_size - 2, 
                                             base_size + 8, base_size))
            
            # Highlight on stone
            pygame.draw.arc(screen, LIGHT_GRAY, 
                          (screen_x + 4, screen_y + self.height - base_size, base_size + 2, base_size - 4), 
                          0.8, 2.2, 2)
            
            # Smaller stones around
            small_size = base_size // 2
            pygame.draw.ellipse(screen, GRAY, (screen_x + base_size + 4, screen_y + self.height - small_size - 1, 
                                             small_size, small_size - 2))
            pygame.draw.ellipse(screen, LIGHT_GRAY, (screen_x, screen_y + self.height - small_size, 
                                                  small_size - 2, small_size - 3))
            
        elif self.obj_type["name"] == "flower":
            # Draw grass background first
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Draw stem
            stem_color = (0, 140, 0)
            pygame.draw.line(screen, stem_color, 
                          (screen_x + self.width // 2, screen_y + self.height // 3), 
                          (screen_x + self.width // 2, screen_y + self.height - 2), 
                          2)
            
            # Draw leaves with more detail
            leaf_size = 4
            # First leaf
            pygame.draw.ellipse(screen, LIGHT_GREEN, 
                              (screen_x + self.width // 2 - 2, screen_y + self.height // 2, 
                               leaf_size + 4, leaf_size))
            # Second leaf - slightly different shape
            pygame.draw.ellipse(screen, (100, 180, 80), 
                              (screen_x + self.width // 2 - leaf_size - 2, screen_y + self.height // 2 + 3, 
                               leaf_size + 4, leaf_size))
            
            # Add leaf vein detail
            pygame.draw.line(screen, (80, 160, 60),
                           (screen_x + self.width // 2 - 2, screen_y + self.height // 2 + leaf_size // 2),
                           (screen_x + self.width // 2 + leaf_size + 2, screen_y + self.height // 2 + leaf_size // 2),
                           1)
            
            # Flower type based on variation
            flower_x = screen_x + self.width // 2
            flower_y = screen_y + self.height // 3
            
            if self.variation < 0.33:
                # Pink flower with petals
                for angle in range(0, 360, 45):  # More petals (8 instead of 6)
                    rad = math.radians(angle)
                    petal_x = flower_x + 6 * math.cos(rad)
                    petal_y = flower_y + 6 * math.sin(rad)
                    
                    # Vary petal colors slightly
                    petal_color = (
                        max(0, min(255, PINK[0] - 10 + int(20 * random.random()))),
                        max(0, min(255, PINK[1] - 10 + int(20 * random.random()))),
                        max(0, min(255, PINK[2] - 10 + int(20 * random.random())))
                    )
                    
                    pygame.draw.circle(screen, petal_color, (int(petal_x), int(petal_y)), 4)
                # Yellow center with more detail
                pygame.draw.circle(screen, YELLOW, (flower_x, flower_y), 3)
                pygame.draw.circle(screen, (200, 150, 0), (flower_x, flower_y), 2)
                
            elif self.variation < 0.66:
                # Purple flower with curved petals
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    petal_x = flower_x + 6 * math.cos(rad)
                    petal_y = flower_y + 6 * math.sin(rad)
                    
                    # Elliptical petals for more interesting shape
                    petal_width = 4
                    petal_height = 6
                    
                    # Create a surface for the petal to rotate it
                    petal_surface = pygame.Surface((petal_width * 2, petal_height * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(petal_surface, PURPLE, 
                                      (0, 0, petal_width * 2, petal_height * 2))
                    
                    # Rotate and position the petal
                    petal_rect = petal_surface.get_rect(center=(petal_x, petal_y))
                    rotated_petal = pygame.transform.rotate(petal_surface, angle)
                    rotated_rect = rotated_petal.get_rect(center=petal_rect.center)
                    
                    screen.blit(rotated_petal, rotated_rect)
                
                # White center with detail
                pygame.draw.circle(screen, WHITE, (flower_x, flower_y), 3)
                pygame.draw.circle(screen, (255, 255, 200), (flower_x, flower_y), 2)
                
            else:
                # Red/orange flower - more vibrant with gradient effect
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    petal_distance = 7
                    petal_x = flower_x + petal_distance * math.cos(rad)
                    petal_y = flower_y + petal_distance * math.sin(rad)
                    
                    # Gradient from orange to red
                    petal_color = (
                        220 + int(35 * math.cos(rad)),  # R: varies between 185-255
                        20 + int(80 * abs(math.sin(rad))),  # G: varies between 20-100
                        0  # B: always 0
                    )
                    
                    pygame.draw.circle(screen, petal_color, (int(petal_x), int(petal_y)), 5)
                
                # Yellow center with orange ring
                pygame.draw.circle(screen, (255, 180, 0), (flower_x, flower_y), 4)
                pygame.draw.circle(screen, YELLOW, (flower_x, flower_y), 2)
        
        elif self.obj_type["name"] == "mushroom":
            # Draw grass background
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Stem
            stem_height = self.height // 2 - 2
            stem_width = self.width // 4
            stem_x = screen_x + (self.width - stem_width) // 2
            stem_y = screen_y + self.height - stem_height
            
            # Stem with slight gradient and shadow
            stem_top_color = (250, 240, 220)  # Lighter at top
            stem_bottom_color = (230, 220, 200)  # Darker at bottom
            
            for y in range(stem_height):
                progress = y / stem_height
                r = int(stem_top_color[0] * (1 - progress) + stem_bottom_color[0] * progress)
                g = int(stem_top_color[1] * (1 - progress) + stem_bottom_color[1] * progress)
                b = int(stem_top_color[2] * (1 - progress) + stem_bottom_color[2] * progress)
                
                pygame.draw.line(screen, (r, g, b),
                               (stem_x, stem_y + y),
                               (stem_x + stem_width, stem_y + y),
                               1)
            
            # Add shadow on one side
            pygame.draw.line(screen, (200, 190, 180),
                           (stem_x, stem_y),
                           (stem_x, stem_y + stem_height),
                           1)
            
            # Cap
            cap_width = self.width - 6
            cap_height = self.height // 2
            cap_x = screen_x + 3
            cap_y = screen_y + stem_y - cap_height + 2
            
            if self.variation < 0.5:
                # Red mushroom with white spots
                # Cap with gradient effect
                cap_color_top = (220, 20, 60)  # Bright red
                cap_color_bottom = (180, 10, 30)  # Darker red
                
                # Draw cap with gradient
                for y in range(cap_height):
                    progress = y / cap_height
                    r = int(cap_color_top[0] * (1 - progress) + cap_color_bottom[0] * progress)
                    g = int(cap_color_top[1] * (1 - progress) + cap_color_bottom[1] * progress)
                    b = int(cap_color_top[2] * (1 - progress) + cap_color_bottom[2] * progress)
                    
                    # Calculate width for the current y to create round cap shape
                    y_progress = 2 * (0.5 - abs(0.5 - progress))  # 0->1->0
                    current_width = int(cap_width * (0.7 + 0.3 * y_progress))
                    current_x = cap_x + (cap_width - current_width) // 2
                    
                    pygame.draw.line(screen, (r, g, b),
                                   (current_x, cap_y + y),
                                   (current_x + current_width, cap_y + y),
                                   1)
                
                # White spots with more natural distribution
                spot_count = 6
                spot_positions = [
                    (0.2, 0.3), (0.7, 0.2), (0.5, 0.5),
                    (0.3, 0.7), (0.8, 0.6), (0.1, 0.5)
                ]
                
                for i in range(spot_count):
                    rel_x, rel_y = spot_positions[i]
                    spot_x = cap_x + int(rel_x * cap_width)
                    spot_y = cap_y + int(rel_y * cap_height)
                    spot_size = 2 + int(random.random() * 2)
                    
                    pygame.draw.circle(screen, WHITE, (spot_x, spot_y), spot_size)
                    # Add slight shadow to spots
                    pygame.draw.arc(screen, (230, 230, 230),
                                  (spot_x - spot_size, spot_y - spot_size,
                                   spot_size * 2, spot_size * 2),
                                  0.8, 2.8, 1)
            else:
                # Brown mushroom with more detailed texturing
                cap_color = (205, 133, 63)
                
                # Draw cap base
                pygame.draw.ellipse(screen, cap_color, (cap_x, cap_y, cap_width, cap_height))
                
                # Add highlight to top of cap
                highlight_width = cap_width * 0.7
                highlight_height = cap_height * 0.3
                pygame.draw.ellipse(screen, (225, 153, 83),
                                  (cap_x + (cap_width - highlight_width) // 2,
                                   cap_y + cap_height * 0.1,
                                   highlight_width, highlight_height))
                
                # Texture lines - more natural pattern
                for i in range(5):
                    curve_offset = random.random() * 0.2 + 0.1
                    pygame.draw.arc(screen, (139, 69, 19), 
                                  (cap_x, cap_y + i * (cap_height / 5), 
                                   cap_width, cap_height - i * (cap_height / 5)), 
                                  curve_offset, 3.14 - curve_offset, 1)
                
                # Add small gills underneath
                if self.variation > 0.75:
                    gill_y = cap_y + cap_height - 1
                    for i in range(5):
                        gill_x = cap_x + 5 + i * (cap_width - 10) // 4
                        pygame.draw.line(screen, (180, 120, 60),
                                       (gill_x, gill_y),
                                       (stem_x + stem_width // 2, stem_y),
                                       1)
        
        elif self.obj_type["name"] == "log":
            # Base log shape
            log_color = (139, 69, 19)  # Brown
            pygame.draw.rect(screen, log_color, (screen_x, screen_y, self.width, self.height))
            
            # Determine orientation based on variation
            horizontal = self.variation > 0.5
            
            if horizontal:
                # Horizontal log
                # End caps - circular texture at both ends
                end_radius = self.height // 2
                end_color = (120, 60, 15)  # Darker brown
                
                # Left end cap
                pygame.draw.ellipse(screen, end_color, 
                                  (screen_x, screen_y, end_radius * 2, self.height))
                # Right end cap
                pygame.draw.ellipse(screen, end_color, 
                                  (screen_x + self.width - end_radius * 2, screen_y, 
                                   end_radius * 2, self.height))
                
                # Add wood grain lines
                grain_color = (160, 82, 45)  # Lighter brown for grain
                grain_count = 4
                for i in range(grain_count):
                    y_pos = screen_y + (i + 1) * self.height // (grain_count + 1)
                    
                    # Add wave to the grain
                    grain_points = []
                    segments = 8
                    for s in range(segments + 1):
                        x = screen_x + s * self.width / segments
                        wave = math.sin(s * 0.8 + i * 1.5) * 2
                        grain_points.append((x, y_pos + wave))
                    
                    # Draw the wavy grain line
                    if len(grain_points) >= 2:
                        pygame.draw.lines(screen, grain_color, False, grain_points, 1)
                
                # Add some knots in the wood
                knot_count = 1 if self.variation < 0.8 else 2
                for i in range(knot_count):
                    knot_x = screen_x + end_radius * 2 + int((self.width - end_radius * 4) * ((i + 1) / (knot_count + 1)))
                    knot_y = screen_y + self.height // 2
                    knot_radius = 3 + int(self.variation * 2)
                    
                    # Draw knot with gradient effect
                    pygame.draw.circle(screen, (110, 55, 15), (knot_x, knot_y), knot_radius)
                    pygame.draw.circle(screen, (90, 45, 10), (knot_x, knot_y), knot_radius - 1)
                    
                    # Add highlight to knot
                    pygame.draw.arc(screen, (160, 82, 45),
                                  (knot_x - knot_radius, knot_y - knot_radius,
                                   knot_radius * 2, knot_radius * 2),
                                  0.7, 2.5, 1)
                
            else:
                # Vertical log (stump)
                # Top circular texture (rings)
                top_color = (120, 60, 15)  # Darker brown
                pygame.draw.ellipse(screen, top_color, 
                                  (screen_x, screen_y, self.width, self.height // 3))
                
                # Add tree rings
                ring_count = 3
                for i in range(ring_count):
                    ring_radius = (self.width // 2) * (1 - (i * 0.25))
                    ring_x = screen_x + self.width // 2
                    ring_y = screen_y + self.height // 6
                    
                    # Alternate between darker and lighter rings
                    ring_color = (110, 55, 15) if i % 2 == 0 else (130, 65, 25)
                    
                    pygame.draw.circle(screen, ring_color, (ring_x, ring_y), ring_radius, 1)
                
                # Add bark texture to sides
                bark_color = (100, 50, 15)  # Dark brown for bark
                texture_count = 6
                for i in range(texture_count):
                    texture_height = self.height * 2 // 3
                    start_y = screen_y + self.height // 3
                    
                    # Left side texture
                    texture_x = screen_x + i * (self.width // texture_count)
                    pygame.draw.line(screen, bark_color,
                                   (texture_x, start_y),
                                   (texture_x, start_y + texture_height),
                                   1)
                    
                    # Right side texture
                    texture_x = screen_x + self.width - i * (self.width // texture_count)
                    pygame.draw.line(screen, bark_color,
                                   (texture_x, start_y),
                                   (texture_x, start_y + texture_height),
                                   1)
                
                # Highlight
                pygame.draw.arc(screen, (160, 82, 45),
                              (screen_x, screen_y, self.width, self.height // 3),
                              0.8, 2.4, 1)
        
        elif self.obj_type["name"] == "bush":
            # Draw grass background first
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Bush type based on variation
            bush_type = int(self.variation * 3)  # 0, 1, or 2
            
            # Bush center position
            center_x = screen_x + self.width // 2
            center_y = screen_y + self.height // 2 + self.height // 8
            
            # Base bush size
            base_size = self.width // 2
            
            if bush_type == 0:  # Round bush
                # Multiple overlapping circles for fullness
                bush_colors = [(0, 160, 0), (0, 140, 0), (0, 180, 0)]
                for i in range(3):
                    offset_x = -2 + i * 2
                    offset_y = -2 + i * 2
                    # Each layer has a slightly different color
                    pygame.draw.circle(screen, bush_colors[i], 
                                     (center_x + offset_x, center_y + offset_y), 
                                     base_size - i * 2)
                
                # Add berries or flowers if it's a special bush
                if self.variation > 0.8:
                    # Red berries
                    for i in range(5):
                        berry_angle = i * 72  # Spread berries evenly
                        berry_distance = base_size * 0.6
                        berry_x = center_x + math.cos(math.radians(berry_angle)) * berry_distance
                        berry_y = center_y + math.sin(math.radians(berry_angle)) * berry_distance
                        pygame.draw.circle(screen, RED, 
                                         (int(berry_x), int(berry_y)), 
                                         2)
            
            elif bush_type == 1:  # Wide spreading bush
                # Wider, lower bush with multiple tufts
                for i in range(4):
                    tuft_x = center_x - base_size + i * base_size // 2
                    tuft_y = center_y - 2 + (i % 2) * 4
                    tuft_color = (0, 130 + i * 15, 0)
                    pygame.draw.circle(screen, tuft_color, 
                                     (tuft_x, tuft_y), 
                                     base_size // 2)
                
            else:  # Tall pointy bush/shrub
                # Taller, more vertical bush
                pygame.draw.polygon(screen, (0, 150, 0), [
                    (center_x - base_size, center_y + base_size // 2),
                    (center_x, center_y - base_size),
                    (center_x + base_size, center_y + base_size // 2)
                ])
                
                # Add some texture/detail
                pygame.draw.polygon(screen, (0, 170, 0), [
                    (center_x - base_size // 2, center_y + base_size // 4),
                    (center_x, center_y - base_size * 3 // 4),
                    (center_x + base_size // 2, center_y + base_size // 4)
                ])
            
            # Add a small stem/trunk at the bottom
            pygame.draw.rect(screen, BROWN, 
                           (center_x - 2, center_y + base_size // 2, 
                            4, base_size // 4))
            
        elif self.obj_type["name"] == "rabbit":
            # Draw grass background first
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Rabbit animation/position based on time and variation
            time_offset = (pygame.time.get_ticks() // 500) % 4
            is_hopping = (time_offset == 1 or time_offset == 3)
            is_looking = time_offset == 2
            
            # Rabbit position
            rabbit_x = screen_x + self.width // 2
            
            # When hopping, rabbit is higher off the ground
            if is_hopping:
                rabbit_y = screen_y + self.height // 2 - 4
            else:
                rabbit_y = screen_y + self.height // 2
            
            # Rabbit color - white or brown
            if self.variation < 0.5:
                rabbit_color = (250, 250, 250)  # White
                eye_color = RED
            else:
                rabbit_color = (150, 120, 80)  # Brown
                eye_color = BLACK
            
            # Rabbit body
            body_width = self.width // 3
            body_height = self.height // 4
            pygame.draw.ellipse(screen, rabbit_color, 
                              (rabbit_x - body_width // 2, rabbit_y - body_height // 2, 
                               body_width, body_height))
            
            # Rabbit head
            head_size = body_width // 2
            if is_looking:
                # Looking up - head higher
                head_y = rabbit_y - body_height // 2 - head_size // 2
            else:
                # Normal position
                head_y = rabbit_y - body_height // 4
                
            pygame.draw.circle(screen, rabbit_color, 
                             (rabbit_x, head_y), 
                             head_size)
            
            # Rabbit ears
            ear_width = head_size // 3
            ear_height = head_size
            
            # Left ear
            pygame.draw.ellipse(screen, rabbit_color, 
                              (rabbit_x - head_size // 2, head_y - ear_height, 
                               ear_width, ear_height))
            # Inner left ear
            pygame.draw.ellipse(screen, PINK, 
                              (rabbit_x - head_size // 2 + 1, head_y - ear_height + 1, 
                               ear_width - 2, ear_height // 1.5))
            
            # Right ear
            pygame.draw.ellipse(screen, rabbit_color, 
                              (rabbit_x + head_size // 2 - ear_width, head_y - ear_height, 
                               ear_width, ear_height))
            # Inner right ear
            pygame.draw.ellipse(screen, PINK, 
                              (rabbit_x + head_size // 2 - ear_width + 1, head_y - ear_height + 1, 
                               ear_width - 2, ear_height // 1.5))
            
            # Eyes
            pygame.draw.circle(screen, eye_color, 
                             (rabbit_x - head_size // 3, head_y - head_size // 4), 
                             2)
            pygame.draw.circle(screen, eye_color, 
                             (rabbit_x + head_size // 3, head_y - head_size // 4), 
                             2)
            
            # Nose
            pygame.draw.circle(screen, PINK, 
                             (rabbit_x, head_y + head_size // 4), 
                             2)
            
            # Legs - only show when not hopping
            if not is_hopping:
                # Front legs
                leg_width = 3
                leg_height = body_height // 2
                pygame.draw.rect(screen, rabbit_color, 
                               (rabbit_x - body_width // 4, rabbit_y, 
                                leg_width, leg_height))
                pygame.draw.rect(screen, rabbit_color, 
                               (rabbit_x + body_width // 4 - leg_width, rabbit_y, 
                                leg_width, leg_height))
                
            # Tail
            pygame.draw.circle(screen, WHITE, 
                             (rabbit_x - body_width // 2, rabbit_y), 
                             body_width // 6)
            
        elif self.obj_type["name"] == "bird":
            # Draw an appropriate background
            var_color = (
                max(0, min(255, GREEN[0] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[1] - 15 + int(30 * self.variation))),
                max(0, min(255, GREEN[2]))
            )
            pygame.draw.rect(screen, var_color, (screen_x, screen_y, self.width, self.height))
            
            # Bird animation based on time
            time_offset = (pygame.time.get_ticks() // 300) % 6
            is_flying = (time_offset == 1 or time_offset == 3 or time_offset == 5)
            
            # Bird position
            bird_x = screen_x + self.width // 2
            bird_y = screen_y + self.height // 2
            
            # Adjust position if in a tree
            in_tree = not self.revealed
            if in_tree:
                bird_y = screen_y + self.height // 3
            
            # Bird color based on variation
            if self.variation < 0.3:
                bird_color = RED  # Red
            elif self.variation < 0.6:
                bird_color = (30, 30, 150)  # Blue
            else:
                bird_color = (200, 200, 50)  # Yellow
            
            # Draw bird
            if is_flying:
                # Body
                pygame.draw.circle(screen, bird_color, 
                                 (bird_x, bird_y), 
                                 self.width // 10)
                
                # Wings up
                pygame.draw.ellipse(screen, bird_color, 
                                  (bird_x - self.width // 5, bird_y - self.height // 10, 
                                   self.width // 5, self.height // 20))
                pygame.draw.ellipse(screen, bird_color, 
                                  (bird_x, bird_y - self.height // 10, 
                                   self.width // 5, self.height // 20))
            else:
                # Body
                pygame.draw.circle(screen, bird_color, 
                                 (bird_x, bird_y), 
                                 self.width // 10)
                
                # Wings down
                pygame.draw.ellipse(screen, bird_color, 
                                  (bird_x - self.width // 5, bird_y, 
                                   self.width // 5, self.height // 10))
                pygame.draw.ellipse(screen, bird_color, 
                                  (bird_x, bird_y, 
                                   self.width // 5, self.height // 10))
            
            # Head
            pygame.draw.circle(screen, bird_color, 
                             (bird_x + self.width // 15, bird_y - self.height // 15), 
                             self.width // 15)
            
            # Eye
            pygame.draw.circle(screen, BLACK, 
                             (bird_x + self.width // 12, bird_y - self.height // 12), 
                             1)
            
            # Beak
            pygame.draw.polygon(screen, YELLOW, [
                (bird_x + self.width // 10, bird_y - self.height // 15),
                (bird_x + self.width // 6, bird_y - self.height // 15),
                (bird_x + self.width // 8, bird_y - self.height // 20)
            ])
            
        # Check if this word has been mastered
        name = self.obj_type["name"]
        is_mastered = False
        if (target_language in words_learned and 
            name in words_learned[target_language] and 
            words_learned[target_language][name]["mastered"]):
            is_mastered = True
            self.mastered = True
            
        # If object is revealed, show its name
        if self.revealed:
            # Use different color for mastered words
            bg_color = YELLOW if is_mastered else WHITE
            
            font = pygame.font.SysFont('Arial', 10)
            
            # Show either the target language word or its English translation
            if self.translation_shown:
                text = font.render(f"{self.obj_type['english']}", True, BLACK, bg_color)
            else:
                text = font.render(f"{self.obj_type[target_language]}", True, BLACK, bg_color)
                
            text_rect = text.get_rect(center=(screen_x + self.width // 2, screen_y - 5))
            screen.blit(text, text_rect)
    
    def toggle_translation(self):
        self.translation_shown = not self.translation_shown

class World:
    """Manages the infinite world generation"""
    def __init__(self):
        self.chunks = {}  # Dictionary of loaded chunks
        self.active_chunks = set()  # Set of chunk coordinates that are active
        self.render_distance = 2  # Increase render distance for smoother transitions
        
    def get_chunk(self, chunk_x, chunk_y):
        """Get a chunk at the given coordinates, generating it if needed"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key not in self.chunks:
            # Create a new chunk
            self.chunks[chunk_key] = Chunk(chunk_x, chunk_y)
        return self.chunks[chunk_key]
    
    def get_tile(self, tile_x, tile_y):
        """Get the tile at the given world coordinates"""
        # Calculate chunk coordinates
        chunk_x = tile_x // CHUNK_SIZE
        chunk_y = tile_y // CHUNK_SIZE
        
        # Calculate local coordinates within the chunk
        local_x = tile_x % CHUNK_SIZE
        local_y = tile_y % CHUNK_SIZE
        
        # Get the chunk and return the tile
        chunk = self.get_chunk(chunk_x, chunk_y)
        return chunk.get_tile(local_x, local_y)
    
    def is_tile_passable(self, tile_x, tile_y):
        """Check if a tile is passable"""
        tile = self.get_tile(tile_x, tile_y)
        if tile:
            return tile.get("passable", True)
        return False
    
    def update_active_chunks(self, player_chunk_x, player_chunk_y):
        """Update which chunks are active based on player position"""
        # Optimization: Only update chunks when player moves to a new chunk
        if hasattr(self, 'last_player_chunk') and (player_chunk_x, player_chunk_y) == self.last_player_chunk:
            return
            
        # Store current player chunk for future checks
        self.last_player_chunk = (player_chunk_x, player_chunk_y)
        
        # Calculate chunk distance based on screen size for better performance
        # This ensures we only load chunks that are visible or nearly visible
        new_active_chunks = set()
        
        # Keep previous active chunks in memory to prevent flickering
        # Only add new chunks to active set
        for y in range(player_chunk_y - self.render_distance, player_chunk_y + self.render_distance + 1):
            for x in range(player_chunk_x - self.render_distance, player_chunk_x + self.render_distance + 1):
                # Optimization: Skip chunks that are completely out of view
                # Calculate manhattan distance for simplified distance check
                manhattan_dist = abs(x - player_chunk_x) + abs(y - player_chunk_y)
                if manhattan_dist > self.render_distance * 1.5:
                    continue
                    
                chunk_key = (x, y)
                new_active_chunks.add(chunk_key)
                
                if chunk_key not in self.active_chunks:
                    # Ensure the chunk is loaded
                    self.get_chunk(x, y)
        
        # Quickly remove chunks that are no longer active
        # This is faster than checking each chunk individually
        self.active_chunks = new_active_chunks
    
    def get_objects_in_active_chunks(self):
        """Get all game objects in active chunks"""
        objects = []
        for chunk_coord in self.active_chunks:
            chunk = self.chunks[chunk_coord]
            
            # Create game objects if not already created
            if not chunk.objects:
                chunk.create_game_objects()
            
            objects.extend(chunk.objects)
        return objects
    
    def get_object_at_tile(self, tile_x, tile_y):
        """Get the game object at the given tile position"""
        # Calculate chunk coordinates
        chunk_x = tile_x // CHUNK_SIZE
        chunk_y = tile_y // CHUNK_SIZE
        chunk_key = (chunk_x, chunk_y)
        
        if chunk_key in self.chunks:
            chunk = self.chunks[chunk_key]
            for obj in chunk.objects:
                obj_x, obj_y = obj.get_tile_position()
                if obj_x == tile_x and obj_y == tile_y:
                    return obj
        return None

class Game:
    def __init__(self):
        # Set up display based on window mode
        self.setup_display()
        pygame.display.set_caption("Language Learning Game")
        self.clock = pygame.time.Clock()
        
        # Performance optimization variables
        self.frame_count = 0
        self.last_fps = 0
        self.show_fps = True  # Show FPS counter for performance monitoring
        
        # Game state
        self.target_language = "spanish"  # Default language to learn
        self.running = True
        self.show_menu = False
        self.show_vocabulary = False
        self.show_settings = False  # New flag for settings menu
        self.show_word_display = False
        self.word_display_timer = 0
        self.current_word_data = None
        self.word_display_showing_translation = False  # Track if showing translation
        self.font = pygame.font.SysFont('Arial', 16)
        self.large_font = pygame.font.SysFont('Arial', 32)
        
        # Camera/viewport
        self.camera_x = 0
        self.camera_y = 0
        
        # Create the infinite world
        self.world = World()
        
        # Load saved progress if it exists
        self.load_progress()
        
        # Create player
        self.player = Player(0, 0) if not hasattr(self, 'player') else self.player
        
        # Update active chunks around player
        self.world.update_active_chunks(self.player.chunk_x, self.player.chunk_y)
    
    def setup_display(self):
        """Set up the display based on the current window mode"""
        global CURRENT_WINDOW_MODE
        
        if CURRENT_WINDOW_MODE == WINDOW_MODE_FULLSCREEN:
            self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
            self.screen_width = FULLSCREEN_WIDTH
            self.screen_height = FULLSCREEN_HEIGHT
        elif CURRENT_WINDOW_MODE == WINDOW_MODE_BORDERLESS:
            # Borderless takes up the full screen but allows mouse movement between monitors
            self.screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.NOFRAME)
            self.screen_width = FULLSCREEN_WIDTH
            self.screen_height = FULLSCREEN_HEIGHT
        else:  # WINDOW_MODE_WINDOWED
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen_width = SCREEN_WIDTH
            self.screen_height = SCREEN_HEIGHT
        
    def change_window_mode(self, new_mode):
        """Change the window mode and update the display"""
        global CURRENT_WINDOW_MODE
        
        if new_mode == CURRENT_WINDOW_MODE:
            return  # No change needed
            
        CURRENT_WINDOW_MODE = new_mode
        self.setup_display()
    
    def save_progress(self):
        """Save player progress to a file"""
        global CURRENT_WINDOW_MODE
        
        save_data = {
            "score": self.player.score,
            "words_learned": self.player.words_learned,
            "position": {
                "x": self.player.x,
                "y": self.player.y
            },
            "settings": {
                "language": self.target_language,
                "window_mode": CURRENT_WINDOW_MODE
            }
        }
        
        with open("save_game.json", "w") as f:
            json.dump(save_data, f)
    
    def load_progress(self):
        """Load player progress from a file if it exists"""
        global CURRENT_WINDOW_MODE
        
        try:
            with open("save_game.json", "r") as f:
                save_data = json.load(f)
                
                # Create player with saved data
                pos_x = save_data.get("position", {}).get("x", 0)
                pos_y = save_data.get("position", {}).get("y", 0)
                self.player = Player(pos_x, pos_y)
                self.player.score = save_data["score"]
                
                # Convert defaultdict structure from JSON
                for language, words in save_data["words_learned"].items():
                    for word, data in words.items():
                        self.player.words_learned[language][word] = data
                
                # Load settings if they exist
                if "settings" in save_data:
                    settings = save_data["settings"]
                    self.target_language = settings.get("language", "spanish")
                    CURRENT_WINDOW_MODE = settings.get("window_mode", WINDOW_MODE_FULLSCREEN)
                    self.setup_display()  # Update display with loaded settings
                        
            print("Game progress loaded successfully!")
        except (FileNotFoundError, json.JSONDecodeError):
            # No save file or corrupted save
            print("No save file found or corrupted save. Starting fresh.")
            pass
    
    def handle_events(self):
        """Handle player input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_progress()
                self.running = False
            
            # Handle key presses
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Toggle menu
                    self.show_menu = not self.show_menu
                    
                # Menu mode keys
                elif self.show_menu:
                    if event.key == pygame.K_v and not self.show_settings:
                        # Toggle vocabulary list
                        self.show_vocabulary = not self.show_vocabulary
                        self.show_settings = False
                    elif event.key == pygame.K_1 and not self.show_settings:
                        # Switch to Spanish
                        self.target_language = "spanish"
                    elif event.key == pygame.K_2 and not self.show_settings:
                        # Switch to French
                        self.target_language = "french"
                    elif event.key == pygame.K_o and not self.show_vocabulary:
                        # Show settings menu
                        self.show_settings = not self.show_settings
                        self.show_vocabulary = False
                    elif event.key == pygame.K_s and self.show_menu:
                        # Save progress
                        self.save_progress()
                        print("Game progress saved!")
                    elif event.key == pygame.K_q and self.show_menu:
                        # Quit the game
                        self.save_progress()
                        self.running = False
                    elif event.key == pygame.K_f and self.show_menu and not self.show_settings:
                        # Toggle between windowed and fullscreen when not in settings
                        if CURRENT_WINDOW_MODE != WINDOW_MODE_FULLSCREEN:
                            self.change_window_mode(WINDOW_MODE_FULLSCREEN)
                        else:
                            self.change_window_mode(WINDOW_MODE_WINDOWED)
                    elif event.key == pygame.K_t and self.show_word_display:
                        # Toggle the word display language directly using T key
                        self.word_display_showing_translation = not self.word_display_showing_translation
                        # Reset timer on manual toggle
                        self.word_display_timer = 180
                        
                    # Handle settings menu key presses
                    if self.show_settings:
                        if event.key == pygame.K_1:  # Windowed mode
                            self.change_window_mode(WINDOW_MODE_WINDOWED)
                        elif event.key == pygame.K_2:  # Fullscreen mode
                            self.change_window_mode(WINDOW_MODE_FULLSCREEN)
                        elif event.key == pygame.K_3:  # Borderless mode
                            self.change_window_mode(WINDOW_MODE_BORDERLESS)
            
            # Handle mouse click for interaction
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.show_menu:
                if event.button == 1:  # Left mouse button
                    self.handle_mouse_interaction()
        
        # Only process movement when not in menu
        if not self.show_menu:
            # Handle continuous key presses for movement
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx -= self.player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx += self.player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy -= self.player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy += self.player.speed
                
            # Check if shift is pressed for sprinting
            is_sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.world, is_sprinting)
                
        # Update player's facing direction based on mouse position (continuous update)
        self.player.get_facing_tile_position()
    
    def handle_mouse_interaction(self):
        """Handle interaction via mouse click"""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convert to world coordinates
        world_mouse_x = mouse_x + self.camera_x
        world_mouse_y = mouse_y + self.camera_y
        
        # Calculate distance from player to mouse click
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2
        distance = math.sqrt((world_mouse_x - player_center_x)**2 + (world_mouse_y - player_center_y)**2)
        
        # Check if click is within interaction range
        if distance <= self.player.interaction_range:
            # Convert world position to tile coordinates
            tile_x = world_mouse_x // TILE_SIZE
            tile_y = world_mouse_y // TILE_SIZE
            
            # Find the object at this position
            obj = self.world.get_object_at_tile(tile_x, tile_y)
            
            if obj:
                if obj.revealed:
                    obj.toggle_translation()
                    # Get word data for display
                    word_key = obj.obj_type["name"]
                    if word_key in self.player.words_learned[self.target_language]:
                        self.current_word_data = self.player.words_learned[self.target_language][word_key]
                        self.show_word_display = True
                        self.word_display_timer = 180  # Show for 3 seconds (60 FPS * 3)
                        # Toggle the display language
                        self.word_display_showing_translation = obj.translation_shown
                else:
                    obj.revealed = True
                    # Add to learned words when revealing a new object
                    word_data = self.player.learn_word(obj.obj_type, self.target_language)
                    self.current_word_data = word_data
                    self.show_word_display = True
                    self.word_display_timer = 432  # Show for 3 seconds (144 FPS * 3)
                    self.word_display_showing_translation = False  # Start with target language
    
    def draw_menu(self):
        """Draw the game menu"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Menu title
        title_font = pygame.font.SysFont('Arial', 36)
        title = title_font.render("Game Menu", True, WHITE)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))
        
        # Menu options
        options = [
            f"Score: {self.player.score}",
            f"Learning: {self.target_language.capitalize()}",
            f"Mastery: {self.player.get_mastery_percentage(self.target_language):.1f}%",
            "",
            "1: Switch to Spanish",
            "2: Switch to French",
            "V: View Vocabulary",
            "O: Options Menu",
            "S: Save Game",
            "Q: Quit Game",
            "ESC: Close Menu"
        ]
        
        y_pos = 150
        for option in options:
            if option:  # Skip empty lines
                option_text = self.font.render(option, True, WHITE)
                self.screen.blit(option_text, (self.screen_width // 2 - option_text.get_width() // 2, y_pos))
            y_pos += 30
            
    def draw_settings_menu(self):
        """Draw the settings menu"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Settings title
        title_font = pygame.font.SysFont('Arial', 36)
        title = title_font.render("Options Menu", True, WHITE)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 50))
        
        # Get current window mode text
        if CURRENT_WINDOW_MODE == WINDOW_MODE_WINDOWED:
            current_mode = "Windowed"
        elif CURRENT_WINDOW_MODE == WINDOW_MODE_FULLSCREEN:
            current_mode = "Fullscreen"
        else:
            current_mode = "Borderless"
        
        # Settings options
        options = [
            f"Current Window Mode: {current_mode}",
            "",
            "1: Windowed Mode",
            "2: Fullscreen Mode",
            "3: Borderless Fullscreen Mode",
            "",
            "ESC: Back to Menu"
        ]
        
        # Add explanation text for each mode
        explanations = [
            "",
            "",
            "Standard window with borders",
            "Full screen exclusive mode",
            "Fullscreen window that allows mouse to move between monitors",
            "",
            ""
        ]
        
        y_pos = 150
        for i, option in enumerate(options):
            if option:  # Skip empty lines
                color = YELLOW if i > 0 and i < 4 and option.startswith(str(i)) else WHITE
                option_text = self.font.render(option, True, color)
                self.screen.blit(option_text, (self.screen_width // 2 - option_text.get_width() // 2, y_pos))
                
                # Add explanation if applicable
                if explanations[i]:
                    explanation_text = self.font.render(explanations[i], True, LIGHT_GRAY)
                    self.screen.blit(explanation_text, 
                                    (self.screen_width // 2 - explanation_text.get_width() // 2, y_pos + 20))
                    y_pos += 20  # Extra space for explanation
            y_pos += 30
            
    def draw_vocabulary_list(self):
        """Draw the vocabulary list UI"""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw the vocabulary title
        title_font = pygame.font.SysFont('Arial', 24)
        title = title_font.render(f"Vocabulary - {self.target_language.capitalize()}", True, WHITE)
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 20))
        
        # Draw language selection instructions
        lang_text = self.font.render("Press 1 for Spanish, 2 for French", True, WHITE)
        self.screen.blit(lang_text, (self.screen_width // 2 - lang_text.get_width() // 2, 50))
        
        # Draw mastery information
        mastery = self.player.get_mastery_percentage(self.target_language)
        mastery_text = self.font.render(f"Mastery: {mastery:.1f}%", True, WHITE)
        self.screen.blit(mastery_text, (self.screen_width // 2 - mastery_text.get_width() // 2, 70))
        
        # Draw the vocabulary list
        if self.target_language in self.player.words_learned:
            words = self.player.words_learned[self.target_language]
            
            if not words:
                no_words = self.font.render("No words learned yet in this language.", True, WHITE)
                self.screen.blit(no_words, (self.screen_width // 2 - no_words.get_width() // 2, self.screen_height // 2))
            else:
                # Table headers
                y_pos = 100
                x_pos_word = self.screen_width // 4
                x_pos_trans = self.screen_width // 2
                x_pos_views = 3 * self.screen_width // 4
                
                headers = [
                    self.font.render(self.target_language.capitalize(), True, YELLOW),
                    self.font.render("English", True, YELLOW),
                    self.font.render("Views", True, YELLOW)
                ]
                
                self.screen.blit(headers[0], (x_pos_word - headers[0].get_width() // 2, y_pos))
                self.screen.blit(headers[1], (x_pos_trans - headers[1].get_width() // 2, y_pos))
                self.screen.blit(headers[2], (x_pos_views - headers[2].get_width() // 2, y_pos))
                
                y_pos += 30
                
                # Sort words by mastery and name
                sorted_words = sorted(words.items(), 
                                     key=lambda x: (-x[1]["mastered"], x[1]["word"]))
                
                for i, (_, word_data) in enumerate(sorted_words):
                    if y_pos > self.screen_height - 50:  # Don't go off screen
                        break
                        
                    # Highlight mastered words
                    color = YELLOW if word_data["mastered"] else WHITE
                    
                    word_text = self.font.render(word_data["word"], True, color)
                    eng_text = self.font.render(word_data["english"], True, color)
                    views_text = self.font.render(f"{word_data['views']}", True, color)
                    
                    self.screen.blit(word_text, (x_pos_word - word_text.get_width() // 2, y_pos))
                    self.screen.blit(eng_text, (x_pos_trans - eng_text.get_width() // 2, y_pos))
                    self.screen.blit(views_text, (x_pos_views - views_text.get_width() // 2, y_pos))
                    
                    y_pos += 25
        
        # Draw close instructions
        close_text = self.font.render("Press ESC to return to menu", True, WHITE)
        self.screen.blit(close_text, (self.screen_width // 2 - close_text.get_width() // 2, self.screen_height - 30))
    
    def draw_word_display(self):
        """Draw the current word in a larger display in the corner"""
        if not self.current_word_data or not self.show_word_display:
            return
            
        word = self.current_word_data["word"]
        english = self.current_word_data["english"]
        is_mastered = self.current_word_data["mastered"]
        views = self.current_word_data["views"]
        
        # Create a semi-transparent background
        display_width = 200
        display_height = 120  # Increase height to fit views count
        display_x = self.screen_width - display_width - 20
        display_y = 20
        
        # Draw background
        bg_color = (0, 0, 80, 200)  # Semi-transparent blue
        bg_surface = pygame.Surface((display_width, display_height), pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        self.screen.blit(bg_surface, (display_x, display_y))
        
        # Determine which word to show based on the translation toggle
        if self.word_display_showing_translation:
            primary_word = english
            secondary_word = word
            primary_label = "English:"
            secondary_label = f"{self.target_language.capitalize()}:"
        else:
            primary_word = word
            secondary_word = english
            primary_label = f"{self.target_language.capitalize()}:"
            secondary_label = "English:"
        
        # Draw primary word (larger)
        word_color = YELLOW if is_mastered else WHITE
        
        # Draw label for primary word
        label_text = self.font.render(primary_label, True, WHITE)
        self.screen.blit(label_text, (display_x + 10, display_y + 5))
        
        # Draw primary word
        word_text = self.large_font.render(primary_word, True, word_color)
        self.screen.blit(word_text, (display_x + display_width // 2 - word_text.get_width() // 2, 
                                    display_y + 25))
        
        # Draw label for secondary word
        label2_text = self.font.render(secondary_label, True, WHITE)
        self.screen.blit(label2_text, (display_x + 10, display_y + 55))
        
        # Draw secondary word
        eng_text = self.font.render(secondary_word, True, WHITE)
        self.screen.blit(eng_text, (display_x + display_width // 2 - eng_text.get_width() // 2, 
                                    display_y + 75))
        
        # Draw mastery info and views
        status_text = f"Views: {views}" + (" (Mastered!)" if is_mastered else "")
        views_text = self.font.render(status_text, True, YELLOW if is_mastered else WHITE)
        self.screen.blit(views_text, (display_x + display_width // 2 - views_text.get_width() // 2, 
                                     display_y + 100))
        
        # Draw instruction to toggle
        if self.word_display_timer > 288:  # Only show for the first 2 seconds (144 FPS * 2)
            toggle_text = self.font.render("Press T to toggle language", True, (180, 180, 180))
            self.screen.blit(toggle_text, (display_x + display_width // 2 - toggle_text.get_width() // 2, 
                                        display_y + display_height + 5))
    
    def update(self):
        """Update game state"""
        # Set camera to follow player
        self.camera_x = self.player.x - self.screen_width // 2
        self.camera_y = self.player.y - self.screen_height // 2
        
        # Update player's camera offset (needed for mouse position calculations)
        self.player.camera_offset_x = self.camera_x
        self.player.camera_offset_y = self.camera_y
        
        # Update active chunks based on player position
        player_chunk_x = self.player.x // (CHUNK_SIZE * TILE_SIZE)
        player_chunk_y = self.player.y // (CHUNK_SIZE * TILE_SIZE)
        self.world.update_active_chunks(player_chunk_x, player_chunk_y)
        
        # Word display timer
        if self.show_word_display and self.word_display_timer > 0:
            self.word_display_timer -= 1
            if self.word_display_timer <= 0:
                self.show_word_display = False
    
    def draw(self):
        """Draw the game world"""
        # Clear the screen
        self.screen.fill(BLACK)
        
        # Adjust screen size based on window mode
        screen_w = self.screen_width
        screen_h = self.screen_height
        
        # Get all objects in the currently active chunks
        game_objects = self.world.get_objects_in_active_chunks()
        
        # First draw objects without layer information or with background layer
        for obj in game_objects:
            # Check if the object type has a layer key
            layer = obj.obj_type.get("layer", "background")  # Default to background if no layer specified
            if layer == "background":
                obj.draw(self.screen, self.camera_x, self.camera_y, self.target_language, self.player.words_learned)
        
        # Draw player
        self.player.draw(self.screen, self.camera_x, self.camera_y)
        
        # Then draw foreground objects on top
        for obj in game_objects:
            layer = obj.obj_type.get("layer", "background")
            if layer == "foreground":
                obj.draw(self.screen, self.camera_x, self.camera_y, self.target_language, self.player.words_learned)
        
        # Draw interaction range indicator (for debugging or UI feedback)
        player_screen_x = self.player.x + self.player.width // 2 - self.camera_x
        player_screen_y = self.player.y + self.player.height // 2 - self.camera_y
        
        # Get mouse position to draw a line to cursor when in range
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance = math.sqrt((mouse_x - player_screen_x)**2 + (mouse_y - player_screen_y)**2)
        
        # Draw line from player to mouse cursor if in range
        if distance <= self.player.interaction_range:
            # Draw a line with a slight glow effect
            pygame.draw.line(self.screen, (180, 180, 255, 150), 
                           (player_screen_x, player_screen_y), 
                           (mouse_x, mouse_y), 2)
        
        # Draw compass in top left
        self.draw_compass()
        
        # Draw word display if active
        if self.show_word_display:
            self.draw_word_display()
        
        # Draw menu, vocabulary, or settings if active
        if self.show_menu:
            if self.show_vocabulary:
                self.draw_vocabulary_list()
            elif self.show_settings:
                self.draw_settings_menu()
            else:
                self.draw_menu()
        
        # Update and display FPS counter (every 10 frames to avoid performance hit)
        self.frame_count += 1
        if self.frame_count >= 10:
            self.last_fps = int(self.clock.get_fps())
            self.frame_count = 0
            
        if self.show_fps:
            fps_text = self.font.render(f"FPS: {self.last_fps}", True, WHITE)
            fps_rect = fps_text.get_rect(topright=(screen_w - 10, 10))
            # Add background to make text more readable
            pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                           (fps_rect.x - 5, fps_rect.y - 2, fps_rect.width + 10, fps_rect.height + 4))
            self.screen.blit(fps_text, fps_rect)
        
        pygame.display.flip()
    
    def draw_compass(self):
        """Draw a simple compass in the top left corner"""
        # Compass parameters
        compass_radius = 30
        compass_x = 50
        compass_y = 50
        
        # Draw compass background
        compass_bg = pygame.Surface((compass_radius * 2 + 10, compass_radius * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(compass_bg, (0, 0, 0, 150), 
                         (compass_radius + 5, compass_radius + 5), compass_radius + 5)
        self.screen.blit(compass_bg, (compass_x - compass_radius - 5, compass_y - compass_radius - 5))
        
        # Draw compass circle
        pygame.draw.circle(self.screen, (230, 230, 230), (compass_x, compass_y), compass_radius)
        pygame.draw.circle(self.screen, (0, 0, 0), (compass_x, compass_y), compass_radius, 2)
        
        # Draw cardinal directions
        font = pygame.font.SysFont('Arial', 14)
        # North
        north_text = font.render("N", True, (0, 0, 0))
        self.screen.blit(north_text, (compass_x - north_text.get_width() // 2, 
                                    compass_y - compass_radius + 5))
        # East
        east_text = font.render("E", True, (0, 0, 0))
        self.screen.blit(east_text, (compass_x + compass_radius - east_text.get_width() - 5, 
                                   compass_y - east_text.get_height() // 2))
        # South
        south_text = font.render("S", True, (0, 0, 0))
        self.screen.blit(south_text, (compass_x - south_text.get_width() // 2, 
                                    compass_y + compass_radius - south_text.get_height() - 5))
        # West
        west_text = font.render("W", True, (0, 0, 0))
        self.screen.blit(west_text, (compass_x - compass_radius + 5, 
                                   compass_y - west_text.get_height() // 2))
        
        # Draw needle pointing north
        # Calculate player's position relative to the world origin to determine direction
        player_offset_x = self.player.x
        player_offset_y = self.player.y
        
        # Calculate angle (0 = north, 90 = east, 180 = south, 270 = west)
        if player_offset_x == 0 and player_offset_y == 0:
            angle = 0  # Default to north if at origin
        else:
            angle = math.degrees(math.atan2(player_offset_x, -player_offset_y))
            if angle < 0:
                angle += 360
                
        # Draw the needle
        needle_length = compass_radius - 10
        
        # Red needle (north pointer)
        end_x = compass_x + needle_length * math.sin(math.radians(angle))
        end_y = compass_y - needle_length * math.cos(math.radians(angle))
        pygame.draw.line(self.screen, (200, 0, 0), (compass_x, compass_y), 
                       (end_x, end_y), 3)
        
        # White needle (south pointer)
        end_x = compass_x + needle_length * math.sin(math.radians(angle + 180))
        end_y = compass_y - needle_length * math.cos(math.radians(angle + 180))
        pygame.draw.line(self.screen, (255, 255, 255), (compass_x, compass_y), 
                       (end_x, end_y), 3)
        
        # Center dot
        pygame.draw.circle(self.screen, (0, 0, 0), (compass_x, compass_y), 3)
    
    def run(self):
        """Main game loop"""
        # Set up vsync if available for smoother rendering
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT) if not FULLSCREEN else (0, 0), 
                              pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE if FULLSCREEN else pygame.DOUBLEBUF,
                              vsync=1)  # Enable vsync
        
        # Performance monitoring variables
        frame_time = 0
        frame_count = 0
        last_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time between frames (for smoother movement)
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0  # Convert to seconds
            last_time = current_time
            
            # Cap delta time to prevent physics issues on slow frames
            if dt > 0.25:
                dt = 0.25
            
            # Process input
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Render
            self.draw()
            
            # Limit framerate while allowing uncapped FPS when possible
            self.clock.tick(FPS)

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit() 