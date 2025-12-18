import json
import os
import math
import time
from config import *

# File to store persistent level/XP data
AGENT_STATE_FILE = os.path.join(DATA_DIR, "agent_state.json")

class GameRecorder:
    def __init__(self):
        self.frames = []
        self.events = []
        self.history = [] 
        self.key_start_locations = []
        
        # Load persistent state immediately on startup
        self.current_xp = 0.0
        self.agent_level = 1
        self._load_state()

    def _load_state(self):
        """Loads XP and Level from the JSON file."""
        if os.path.exists(AGENT_STATE_FILE):
            try:
                with open(AGENT_STATE_FILE, "r") as f:
                    data = json.load(f)
                    self.current_xp = float(data.get("total_xp", 0.0))
                    self.agent_level = int(data.get("level", 1))
                print(f"[Recorder] Loaded State -> XP: {self.current_xp}, Level: {self.agent_level}")
            except Exception as e:
                print(f"[Recorder] Error loading state: {e}")
        else:
            print("[Recorder] No saved state found. Starting fresh (Level 1).")

    def save_state(self):
        """Saves current XP and Level to the JSON file."""
        data = {
            "total_xp": self.current_xp,
            "level": self.agent_level
        }
        try:
            with open(AGENT_STATE_FILE, "w") as f:
                json.dump(data, f, indent=4)
            print("[Recorder] State saved successfully.")
        except Exception as e:
            print(f"[Recorder] Failed to save state: {e}")

    def reset(self):
        self.frames = []
        self.events = []
        self.key_start_locations = []

    def log_key_location(self, x, y):
        if (x, y) not in self.key_start_locations:
             self.key_start_locations.append((x, y))

    def record_frame(self, t, player, agent):
        # --- FIX: Collect traps from BOTH Player and Agent ---
        all_traps = []
        
        # 1. Add Player Traps (If Human is Hunter)
        if hasattr(player, 'active_traps'):
            all_traps.extend(player.active_traps)
            
        # 2. Add Agent Traps (If AI is Hunter)
        if hasattr(agent, 'active_traps'):
            all_traps.extend(agent.active_traps)
            
        # Capture scanning state (Visuals)
        is_scanning = False
        if hasattr(player, 'is_scanning') and player.is_scanning: is_scanning = True
        if hasattr(agent, 'is_scanning') and agent.is_scanning: is_scanning = True
        
        frame_data = {
            "t": round(t, 2),
            "p_pos": (round(player.x, 2), round(player.y, 2)),
            "a_pos": (round(agent.x, 2), round(agent.y, 2)),
            "traps": list(all_traps), # Save the combined list
            "scanning": is_scanning
        }
        self.frames.append(frame_data)

    def log_event(self, t, name):
        self.events.append({"t": round(t, 2), "name": name})

    def get_metrics(self, map_obj, winner="SURVIVOR"):
        if not self.frames: return {}
        duration = self.frames[-1]['t']
        keys_found = len([e for e in self.events if "KEY" in e['name']])
        
        score = 1000 + (duration * 10) + (keys_found * 500)
        if winner == "SURVIVOR": score += 2000
        
        metrics = {
            "duration": duration,
            "keys_found": keys_found,
            "player_score": int(score),
            "winner": winner,
            "frames": self.frames,
            "map_grid": [row[:] for row in map_obj.grid],
            "map_width": map_obj.width,
            "map_height": map_obj.height,
            "start_keys": list(self.key_start_locations),
            "events_list": [e['name'] for e in self.events]
        }
        return metrics

    def add_match(self, metrics):
        """Calculates final totals and saves to history."""
        match_xp = metrics.get('xp_gained', 0.0)
        
        # 1. ACCUMULATE XP
        self.current_xp += match_xp
        
        # 2. CALCULATE LEVEL (2500 XP per level)
        base_level = 1 + int(self.current_xp // 2500)
        self.agent_level = max(1, base_level)
        
        # 3. UPDATE METRICS with the new totals
        metrics['total_xp'] = self.current_xp
        metrics['agent_level'] = self.agent_level
        
        # 4. SAVE TO DISK
        self.save_state()
        self.history.append(metrics)