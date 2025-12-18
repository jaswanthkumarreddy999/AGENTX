import json
import os

class SurvivorMemory:
    def __init__(self, level_num):
        self.level_num = level_num
        self.filename = f"data/memory/survivor_level_{level_num}.json"
        self.ensure_directory()
        
        # What the survivor remembers across games
        self.known_keys = []
        self.known_exit = None
        self.visited_tiles = [] # List of (x,y)
        
        self.load()

    def ensure_directory(self):
        if not os.path.exists("data/memory"):
            os.makedirs("data/memory")

    def update(self, keys, exit_pos, visited):
        """Updates internal memory with new findings."""
        # Convert sets to lists for JSON serialization
        current_keys = list(keys)
        current_visited = list(visited)
        
        # Merge new data with old data
        # We only add keys if we haven't seen them before
        for k in current_keys:
            if k not in self.known_keys:
                self.known_keys.append(k)
        
        if exit_pos:
            self.known_exit = exit_pos
            
        for v in current_visited:
            if v not in self.visited_tiles:
                self.visited_tiles.append(v)

    def save(self):
        data = {
            "level": self.level_num,
            "keys": self.known_keys,
            "exit": self.known_exit,
            "visited": self.visited_tiles
        }
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f)
            print(f"[Survivor] Memory saved for Level {self.level_num}")
        except Exception as e:
            print(f"[Survivor] Save failed: {e}")

    def load(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                
            # Restore memory
            # Convert lists back to tuples for Python sets
            self.known_keys = [tuple(k) for k in data.get("keys", [])]
            exit_data = data.get("exit")
            self.known_exit = tuple(exit_data) if exit_data else None
            self.visited_tiles = [tuple(v) for v in data.get("visited", [])]
            
            print(f"[Survivor] Loaded memory: {len(self.known_keys)} keys, {len(self.visited_tiles)} tiles explored.")
        except Exception as e:
            print(f"[Survivor] Load failed: {e}")