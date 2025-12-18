import os
from engine.tilemap import TileMap

class LevelLoader:
    def __init__(self):
        pass

    def load_from_file(self, filename):
        """
        Reads a text file and returns a TileMap object.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Level file not found: {filename}")

        grid = []
        with open(filename, 'r') as f:
            for line in f:
                # Strip newline characters but keep spaces (if any)
                row = line.rstrip('\n')
                if row:
                    grid.append(list(row))
        
        # Create and return the TileMap
        # We pass the grid directly. 
        # Note: If your TileMap __init__ works differently, let me know!
        return TileMap(grid)