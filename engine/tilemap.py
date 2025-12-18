import pygame
from config import TILE_SIZE, WHITE, GREY, BLACK, RED, BLUE, GREEN

class TileMap:
    def __init__(self, grid):
        """
        grid: A list of lists (or strings) representing the map.
        """
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0
        # Initialize visibility mask for Fog of War (False = hidden)
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]

    def draw(self, surface, camera_x=0, camera_y=0):
        # Define 3D Colors
        WALL_TOP = (100, 100, 110)   # Lighter Grey
        WALL_SIDE = (60, 60, 70)     # Darker Grey for depth
        FLOOR_COLOR = (25, 25, 30)   # Dark Blue-Grey
        GRID_COLOR = (35, 35, 40)    # Slightly lighter for grid lines
        
        # Draw Floor Background (Optimization: Fill screen once instead of per tile)
        # But for grid effect, we draw tiles:
        
        # Calculate visible range to optimize rendering
        start_x = max(0, int(camera_x // TILE_SIZE))
        end_x = min(self.width, int((camera_x + surface.get_width()) // TILE_SIZE) + 1)
        start_y = max(0, int(camera_y // TILE_SIZE))
        end_y = min(self.height, int((camera_y + surface.get_height()) // TILE_SIZE) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                # FOG CHECK: If not visited, skip completely (Draws Black background)
                if not self.visited[y][x]:
                    continue 

                tile = self.grid[y][x]
                
                # Screen Position
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

                # --- 1. DRAW FLOOR ---
                pygame.draw.rect(surface, FLOOR_COLOR, rect)
                # Draw subtle grid line
                pygame.draw.rect(surface, GRID_COLOR, rect, 1)

                # --- 2. DRAW WALLS (Pseudo-3D) ---
                if tile == '#':
                    # Draw "Side" (Bottom part, darker)
                    side_rect = pygame.Rect(screen_x, screen_y + 10, TILE_SIZE, TILE_SIZE - 10)
                    pygame.draw.rect(surface, WALL_SIDE, side_rect)
                    
                    # Draw "Top" (Top part, lighter, shifted up)
                    top_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE - 10)
                    pygame.draw.rect(surface, WALL_TOP, top_rect)
                
                # --- 3. DRAW OBJECTS ---
                elif tile == 'E':
                    # Glowing Exit
                    pygame.draw.rect(surface, (0, 200, 0), rect) 
                    pygame.draw.rect(surface, (100, 255, 100), rect.inflate(-10, -10))
                elif tile == 'k':
                    # Gold Key (Diamond shape)
                    center = rect.center
                    pygame.draw.circle(surface, (255, 215, 0), center, 8)
                    pygame.draw.circle(surface, (255, 255, 100), center, 4)
    def is_wall(self, x, y):
        """Helper to check if a specific coordinate is a wall."""
        # Force coordinates to be integers
        ix, iy = int(x), int(y)
        
        if 0 <= ix < self.width and 0 <= iy < self.height:
            return self.grid[iy][ix] == '#'
        return True # Treat out-of-bounds as walls