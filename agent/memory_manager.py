import json
import os
import time
import glob
from config import AGENT_HEATMAP_DIR

class MemoryManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heatmap = [[0 for _ in range(width)] for _ in range(height)]
        self.ensure_directory()
        
        # This list will store the "Hotspots" (tiles the player visits often)
        self.predicted_hotspots = []
        
        # --- NEW ATTRIBUTES FOR EXPLORATION TRACKING ---
        self.total_walkable_cells = 0
        # A set to track unique cells that have been visited (faster lookup)
        self.visited_cells = set() 
        # -----------------------------------------------

    def ensure_directory(self):
        if not os.path.exists(AGENT_HEATMAP_DIR):
            os.makedirs(AGENT_HEATMAP_DIR)

    # MODIFIED: Now tracks unique visits in a set
    def visit(self, x, y):
        """Record a visit to a specific tile coordinate."""
        ix, iy = int(x), int(y)
        if 0 <= iy < self.height and 0 <= ix < self.width:
            self.heatmap[iy][ix] += 1
            self.visited_cells.add((ix, iy)) # Track unique visits

    # --- NEW METHOD: Initialization using the map grid ---
    def initialize_map_data(self, map_grid):
        """Calculates the total number of non-wall tiles on the current map."""
        walkable_count = 0
        for y in range(self.height):
            for x in range(self.width):
                # Assuming '#' is a wall and everything else is walkable
                if map_grid[y][x] != '#':
                    walkable_count += 1
        self.total_walkable_cells = walkable_count
    # ----------------------------------------------------

    # --- NEW METHOD: Calculates Exploration Percentage ---
    def get_exploration_percentage(self):
        """Returns the ratio of visited unique cells to total walkable cells."""
        if self.total_walkable_cells == 0:
            return 0.0
        
        visited_count = len(self.visited_cells)
        return visited_count / self.total_walkable_cells
    # ----------------------------------------------------

    # --- FIX: ADDED MISSING is_hotspot METHOD ---
    def is_hotspot(self, x, y):
        """Checks if the given tile coordinates are in the list of predicted hotspots."""
        return (int(x), int(y)) in self.predicted_hotspots
    # --------------------------------------------

    def save(self, level_num=1):
        """Save the current heatmap to a JSON file."""
        timestamp = int(time.time())
        filename = f"heatmap_level{level_num}_{timestamp}.json"
        filepath = os.path.join(AGENT_HEATMAP_DIR, filename)
        
        data = {
            "level": level_num,
            "dimensions": {"width": self.width, "height": self.height},
            "heatmap": self.heatmap
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            print(f"Agent memory saved to {filepath}")
        except Exception as e:
            print(f"Failed to save memory: {e}")

    def load_smart_patrol_data(self, level_num):
        """
        Loads ALL past heatmaps for this level and finds the most visited tiles.
        Returns a list of (x, y) tuples representing 'Hotspots'.
        """
        pattern = os.path.join(AGENT_HEATMAP_DIR, f"heatmap_level{level_num}_*.json")
        files = glob.glob(pattern)
        
        if not files:
            print("No memory found. Agent is guessing randomly.")
            return []

        # Create a blank grid to sum up all history
        total_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        print(f"Agent is learning from {len(files)} previous games...")
        
        for file in files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    # Check if dimensions match (in case map size changed)
                    if data["dimensions"]["width"] == self.width and data["dimensions"]["height"] == self.height:
                        saved_map = data["heatmap"]
                        for y in range(self.height):
                            for x in range(self.width):
                                total_grid[y][x] += saved_map[y][x]
            except:
                continue # Skip broken files

        # Find tiles with high traffic (Above average visits)
        hotspots = []
        max_visits = 0
        for y in range(self.height):
            for x in range(self.width):
                if total_grid[y][x] > max_visits:
                    max_visits = total_grid[y][x]
        
        # If we have data, filter for the top 30% most visited tiles
        threshold = max_visits * 0.3 
        if threshold > 0:
            for y in range(self.height):
                for x in range(self.width):
                    if total_grid[y][x] > threshold:
                        hotspots.append((x, y))
        
        self.predicted_hotspots = hotspots
        print(f"Agent identified {len(hotspots)} strategic hotspots.")
        return hotspots