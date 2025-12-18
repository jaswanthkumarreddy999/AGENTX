import random
import math

# Constants
WALL = '#'
FLOOR = '.'
PLAYER_START = 'P'
KILLER_START = 'A'
EXIT = 'E'
KEY = 'k'

class MazeGenerator:
    def __init__(self, width, height):
        self.width = max(5, width)
        self.height = max(5, height)
        self.grid = []
        self.placed_positions = [] # Tracks (x,y) of all critical items

    def generate(self, level=1):
        # 1. Initialize Grid
        map_w = self.width * 2 + 1
        map_h = self.height * 2 + 1
        self.grid = [[WALL for _ in range(map_w)] for _ in range(map_h)]

        # 2. Recursive Backtracker
        start_x, start_y = 1, 1
        self.grid[start_y][start_x] = FLOOR
        stack = [(start_x, start_y)]

        while stack:
            current_x, current_y = stack[-1]
            neighbors = self._get_unvisited_neighbors(current_x, current_y)

            if neighbors:
                next_x, next_y = random.choice(neighbors)
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2
                self.grid[wall_y][wall_x] = FLOOR
                self.grid[next_y][next_x] = FLOOR
                stack.append((next_x, next_y))
            else:
                stack.pop()

        # 3. Add Loops (Braiding) - 10%
        self._add_loops(chance=0.1)

        # 4. Place Entities with Distance Checks
        self._place_entities(level)

        return self.grid

    def _get_unvisited_neighbors(self, x, y):
        candidates = [(x, y - 2), (x, y + 2), (x - 2, y), (x + 2, y)]
        neighbors = []
        rows = len(self.grid)
        cols = len(self.grid[0])
        for nx, ny in candidates:
            if 0 < nx < cols - 1 and 0 < ny < rows - 1:
                if self.grid[ny][nx] == WALL:
                    neighbors.append((nx, ny))
        return neighbors

    def _add_loops(self, chance):
        rows = len(self.grid)
        cols = len(self.grid[0])
        for y in range(1, rows - 1):
            for x in range(1, cols - 1):
                if self.grid[y][x] == WALL:
                    if self.grid[y-1][x] == FLOOR and self.grid[y+1][x] == FLOOR:
                        if random.random() < chance: self.grid[y][x] = FLOOR
                    elif self.grid[y][x-1] == FLOOR and self.grid[y][x+1] == FLOOR:
                        if random.random() < chance: self.grid[y][x] = FLOOR

    def _place_entities(self, level):
        self.placed_positions = [] # Reset tracker
        
        # Player (Top Left)
        self.grid[1][1] = PLAYER_START
        self.placed_positions.append((1,1))

        # Killer (Bottom Right)
        killer_x = (self.width * 2) - 1
        killer_y = (self.height * 2) - 1
        self.grid[killer_y][killer_x] = KILLER_START
        
        # KEYS: Min Distance = 8 Tiles
        keys_required = 3 + (level // 2)
        total_keys = keys_required + 1
        self._place_random_item(KEY, total_keys, min_dist=8)
        
        # EXITS: Min Distance = 10 Tiles (Should be far apart)
        self._place_random_item(EXIT, 2, min_dist=10)

    def _place_random_item(self, item_char, count, min_dist=5):
        placed = 0
        attempts = 0
        rows = len(self.grid)
        cols = len(self.grid[0])
        
        while placed < count and attempts < 3000:
            rx = random.randint(1, cols - 2)
            ry = random.randint(1, rows - 2)
            
            if self.grid[ry][rx] == FLOOR:
                # 1. Distance Check vs Player Start
                if math.hypot(rx - 1, ry - 1) < 6:
                    attempts += 1; continue
                    
                # 2. Distance Check vs ALL other Critical Items (Keys, Exits)
                too_close = False
                for px, py in self.placed_positions:
                    dist = math.hypot(rx - px, ry - py)
                    if dist < min_dist:
                        too_close = True
                        break
                
                if not too_close:
                    self.grid[ry][rx] = item_char
                    self.placed_positions.append((rx, ry))
                    placed += 1
            attempts += 1
        
        # Fallback (Relaxed Distance)
        if placed < count:
            # Try again with smaller distance (3) just to ensure spawning
            self._place_random_item_fallback(item_char, count - placed, min_dist=3)

    def _place_random_item_fallback(self, item_char, count, min_dist=2):
        placed = 0
        rows = len(self.grid)
        cols = len(self.grid[0])
        for _ in range(1000):
            if placed >= count: return
            rx = random.randint(1, cols - 2)
            ry = random.randint(1, rows - 2)
            if self.grid[ry][rx] == FLOOR:
                self.grid[ry][rx] = item_char
                placed += 1

    def save_to_file(self, filepath):
        try:
            with open(filepath, 'w') as f:
                for row in self.grid:
                    f.write("".join(row) + "\n")
        except: pass