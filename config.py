import os

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)

# --- CRITICAL: THESE MUST BE PRESENT ---
RED = (255, 50, 50)      # Hunter Color
BLUE = (50, 150, 255)    # Survivor Color
# ---------------------------------------

GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 255)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
AGENT_HEATMAP_DIR = os.path.join(DATA_DIR, "memory") 
AGENT_BRAIN_DIR = os.path.join(DATA_DIR, "brains")