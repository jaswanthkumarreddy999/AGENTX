import json
import os
import random

class StrategicBrain:
    def __init__(self):
        self.file_path = "data/strategic_brain.json"
        
        # TIER 1 STRATEGIES (Available from Start)
        self.strategies = {
            "RUSH_SPAWN":  {"successes": 0, "failures": 0, "weight": 1.0, "tier": 1},
            "CAMP_TRAPS":  {"successes": 0, "failures": 0, "weight": 1.0, "tier": 1},
            "PATROL_KEYS": {"successes": 0, "failures": 0, "weight": 1.0, "tier": 1}
        }
        
        # TIER 2+ STRATEGIES (Hidden code blocks that unlock later)
        self.locked_strategies = {
            "ZONE_DEFENSE":      {"tier": 5, "weight": 1.5},
            "PREDICTIVE_CUTOFF": {"tier": 10, "weight": 1.5},
            "BERSERK_RUSH":      {"tier": 15, "weight": 2.0}
        }
        
        self.current_strategy = None
        self.load()

    def check_unlocks(self, agent_level):
        """Checks if the Agent is smart enough to learn new tactics."""
        unlocked_any = False
        for name, data in self.locked_strategies.items():
            if name not in self.strategies and agent_level >= data['tier']:
                # UNLOCK NEW STRATEGY
                self.strategies[name] = {
                    "successes": 0, 
                    "failures": 0, 
                    "weight": data['weight'],
                    "tier": data['tier']
                }
                print(f">>> [NEURAL EVOLUTION] NEW STRATEGY DISCOVERED: {name}")
                unlocked_any = True
        
        if unlocked_any:
            self.save()

    def pick_strategy(self, agent_level, exploration_rate=0.2):
        # 1. Check for new unlocks first
        self.check_unlocks(agent_level)
        
        # 2. Epsilon-Greedy Selection
        if random.random() < exploration_rate:
            self.current_strategy = random.choice(list(self.strategies.keys()))
            return self.current_strategy, "EXPLORATION"

        # 3. Weighted Selection (Exploitation)
        total_weight = sum(s['weight'] for s in self.strategies.values())
        if total_weight <= 0: total_weight = 1
        
        r = random.uniform(0, total_weight)
        uptime = 0
        for name, stats in self.strategies.items():
            uptime += stats['weight']
            if r <= uptime:
                self.current_strategy = name
                return self.current_strategy, "EXPLOITATION"
        
        self.current_strategy = "PATROL_KEYS"
        return self.current_strategy, "FALLBACK"

    def report_match_result(self, winner, time_elapsed):
        if not self.current_strategy: return
        
        # Ensure strategy exists in dictionary before accessing
        if self.current_strategy not in self.strategies: return

        s = self.strategies[self.current_strategy]
        
        if winner == "HUNTER":
            s['successes'] += 1
            s['weight'] += 0.5 # Reward
            if time_elapsed < 20: s['weight'] += 0.5 # Efficiency Bonus
        else:
            s['failures'] += 1
            s['weight'] = max(0.1, s['weight'] - 0.2) # Punishment
            
        self.save()

    def save(self):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(self.strategies, f)
        except: pass

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    for k, v in data.items():
                        if k in self.strategies:
                            self.strategies[k].update(v)
                        elif k in self.locked_strategies:
                            self.strategies[k] = v
            except: pass