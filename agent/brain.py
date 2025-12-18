import json
import os
import random
import numpy as np

class QLearningBrain:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        self.q_table = {} # The Memory Bank
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate # Chance to try "New Ideas" (Random moves)
        self.file_path = "data/memory/hunter_q_table.json"
        
        self.load_brain()

    def get_state_key(self, dx, dy, walls):
        """
        Simplifies the world into a string like 'NE_0100'
        (Survivor is North-East, Wall to the South)
        """
        # 1. Determine relative direction of Survivor
        if abs(dx) > abs(dy):
            direction = "E" if dx > 0 else "W"
        else:
            direction = "S" if dy > 0 else "N"
            
        # 2. Wall configuration (North, South, East, West)
        wall_code = "".join(['1' if w else '0' for w in walls])
        
        return f"{direction}_{wall_code}"

    def choose_action(self, state_key, valid_actions):
        # Exploration: Try a random new idea?
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(valid_actions)
            
        # Exploitation: Use what we know works best
        if state_key not in self.q_table:
            self.q_table[state_key] = {action: 0.0 for action in ["UP", "DOWN", "LEFT", "RIGHT"]}
            
        # Pick the action with the highest Score (Q-value)
        current_knowledge = self.q_table[state_key]
        # Filter only valid actions (don't try to walk off screen)
        valid_knowledge = {k: v for k, v in current_knowledge.items() if k in valid_actions}
        
        if not valid_knowledge: return random.choice(valid_actions)
        
        return max(valid_knowledge, key=valid_knowledge.get)

    def learn(self, state, action, reward, next_state, next_valid_actions):
        """The core learning equation (Bellman Equation)."""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in ["UP", "DOWN", "LEFT", "RIGHT"]}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in ["UP", "DOWN", "LEFT", "RIGHT"]}

        # Predict future reward
        future_rewards = [self.q_table[next_state][a] for a in next_valid_actions]
        max_future_q = max(future_rewards) if future_rewards else 0.0
        
        current_q = self.q_table[state][action]
        
        # Update Memory: Old Value + LearningRate * (Reward + Discount * Future - Old)
        new_q = current_q + self.lr * (reward + self.gamma * max_future_q - current_q)
        self.q_table[state][action] = new_q

    def save_brain(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.q_table, f)
        print(f"[Agent X] Brain Saved! Knowledge Size: {len(self.q_table)} states.")

    def load_brain(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                self.q_table = json.load(f)
            print(f"[Agent X] Brain Loaded with {len(self.q_table)} strategies.")