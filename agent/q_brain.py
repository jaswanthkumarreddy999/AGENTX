import pickle
import os
import random
import numpy as np

class QLearningBrain:
    def __init__(self, agent_name, actions, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.agent_name = agent_name
        self.actions = actions 
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon 
        
        self.q_table = {}
        self.load_brain()

    def get_state_key(self, dist, keys_left, can_see_player):
        dist_cat = "FAR"
        if dist < 5: dist_cat = "NEAR"
        elif dist < 10: dist_cat = "MEDIUM"
        
        vis_cat = "VISIBLE" if can_see_player else "HIDDEN"
        
        return f"{dist_cat}_{keys_left}_{vis_cat}"

    def choose_action(self, state_key):
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(len(self.actions))

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions) 
        else:
            action_idx = np.argmax(self.q_table[state_key])
            # Safety check to prevent crashing if table is corrupted
            if action_idx >= len(self.actions):
                return random.choice(self.actions)
            return self.actions[action_idx]

    def learn(self, state, action, reward, next_state):
        if state not in self.q_table: self.q_table[state] = np.zeros(len(self.actions))
        if next_state not in self.q_table: self.q_table[next_state] = np.zeros(len(self.actions))
        
        try:
            action_idx = self.actions.index(action)
        except ValueError:
            return 
        
        old_value = self.q_table[state][action_idx]
        next_max = np.max(self.q_table[next_state])
        
        new_value = (1 - self.lr) * old_value + self.lr * (reward + self.gamma * next_max)
        self.q_table[state][action_idx] = new_value

    def save_brain(self):
        try:
            os.makedirs("data/brains", exist_ok=True)
            path = f"data/brains/{self.agent_name}_qtable.pkl"
            with open(path, "wb") as f:
                pickle.dump(self.q_table, f)
            print(f">>> [BRAIN] Saved strategy to {path}")
        except Exception as e:
            print(f"[BRAIN] Save Error: {e}")

    def load_brain(self):
        path = f"data/brains/{self.agent_name}_qtable.pkl"
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    loaded_table = pickle.load(f)
                
                # --- CRITICAL FIX: Validate Brain Shape ---
                # Check if the loaded brain matches the current action list size
                if len(loaded_table) > 0:
                    first_key = next(iter(loaded_table))
                    if len(loaded_table[first_key]) != len(self.actions):
                        print(f">>> [BRAIN] Version Mismatch! (Old: {len(loaded_table[first_key])}, New: {len(self.actions)})")
                        print(">>> [BRAIN] Resetting memory for compatibility.")
                        self.q_table = {} # Reset
                        return

                self.q_table = loaded_table
                print(f">>> [BRAIN] Loaded strategy from {path}")
            except Exception as e:
                print(f">>> [BRAIN] Corrupt file ({e}), starting fresh.")
                self.q_table = {}