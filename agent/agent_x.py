import pygame
import math
import random
from config import TILE_SIZE, RED, BLUE 

from engine.pathfinding import a_star_search
from agent.q_brain import QLearningBrain
from agent.memory_manager import MemoryManager

class AgentX:
    def __init__(self, game, x, y, role="HUNTER", is_human=False):
        self.game = game
        self.x, self.y = float(x), float(y)
        self.role = role  # "HUNTER" or "SURVIVOR"
        self.is_human = is_human
        
        # --- DYNAMIC ATTRIBUTES ---
        if self.role == "HUNTER":
            self.color = RED
            self.speed = 3.8
            self.actions = ["PATROL", "CHASE", "INVESTIGATE"]
            self.state = "PATROL"
        else: # SURVIVOR
            self.color = BLUE
            self.speed = 4.0 
            self.actions = ["SCAVENGE", "EVADE", "EXPLORE"]
            self.state = "EXPLORE"

        self.base_vision = 5.0      
        self.scan_vision = 10.0     
        self.current_vision_radius = self.base_vision 
        
        self.brain = QLearningBrain(self.role.lower(), self.actions)
        self.memory = MemoryManager(game.map.width, game.map.height)
        self.path = []
        
        self.level = 1
        self.xp_gained_this_match = 0.0
        self.exploration_rewarded = False 
        
        self.last_pos = (self.x, self.y)
        self.stuck_timer = 0
        self.still_penalty_timer = 0 
        self.decision_timer = 0
        self.last_state_key = None
        self.last_action = None
        self.last_seen_pos = None 
        
        self.known_keys = []
        self.known_exits = []
        
        self.active_traps = []
        self.trap_cooldown = 0
        self.is_scanning = False 
        self.scan_cooldown = 0
        self.scan_duration = 0
        self.boost_cooldown = 0 
        self.is_boosting = False
        self.boost_duration = 0
        
        self.is_frozen = False
        self.freeze_timer = 0.0

    def update(self, decisions_log_ref=None): 
        dt = self.game.dt
        
        if self.is_frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0: self.is_frozen = False
            else: return 
        
        # Passive XP
        self.xp_gained_this_match += 0.05 * dt 

        # Cooldowns
        if self.trap_cooldown > 0: self.trap_cooldown -= dt
        if self.scan_cooldown > 0: self.scan_cooldown -= dt
        if self.boost_cooldown > 0: self.boost_cooldown -= dt
        
        # Vision
        target_radius = self.base_vision
        if self.is_scanning:
            self.scan_duration -= dt
            if self.scan_duration <= 0: self.is_scanning = False 
            else: target_radius = self.scan_vision
        
        diff = target_radius - self.current_vision_radius
        if abs(diff) > 0.1: self.current_vision_radius += diff * 10.0 * dt
        else: self.current_vision_radius = target_radius

        # Physics (Boost)
        if self.is_boosting:
            self.boost_duration -= dt
            self.speed = 6.5
            if self.boost_duration <= 0:
                self.is_boosting = False
                self.speed = 4.0
        
        # 1. UPDATE VISION & MEMORY
        self._update_vision_memory()
        
        # 2. MEMORY HEATMAP
        self.memory.visit(int(self.x + 0.5), int(self.y + 0.5))
        if self.memory.get_exploration_percentage() >= 0.50 and not self.exploration_rewarded:
            reward = 15.0
            self.xp_gained_this_match += reward
            self.exploration_rewarded = True 
            self._log(decisions_log_ref, "System", "EXPLORATION_BONUS", reward)

        # 3. STUCK CHECKS
        dist_moved = math.hypot(self.x - self.last_pos[0], self.y - self.last_pos[1])
        if dist_moved < 0.05:
            self.stuck_timer += dt
            if dist_moved < 0.01: self.still_penalty_timer += dt
            else: self.still_penalty_timer = 0
            
            if self.stuck_timer > 0.5:
                self.force_unstuck(decisions_log_ref)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.still_penalty_timer = 0
            self.last_pos = (self.x, self.y)

        # 4. BRAIN EXECUTION
        if self.is_human: self.handle_human_input(decisions_log_ref)
        elif self.role == "HUNTER": self.run_hunter_logic(dt, decisions_log_ref)
        else: self.run_survivor_logic(dt, decisions_log_ref)

    def _update_vision_memory(self):
        view_r = int(self.current_vision_radius) + 1
        cx, cy = int(self.x), int(self.y)
        for y in range(max(0, cy - view_r), min(self.game.map.height, cy + view_r + 1)):
            for x in range(max(0, cx - view_r), min(self.game.map.width, cx + view_r + 1)):
                if math.hypot(x - self.x, y - self.y) <= self.current_vision_radius:
                    tile = self.game.map.grid[y][x]
                    pos = (x, y)
                    if tile == 'k':
                        if pos not in self.known_keys: self.known_keys.append(pos)
                    elif tile == 'E':
                        if pos not in self.known_exits: self.known_exits.append(pos)
                    elif tile == '.':
                        if pos in self.known_keys: self.known_keys.remove(pos)

    # =========================================================
    # --- SURVIVOR BRAIN (FIXED) ---
    # =========================================================
    def run_survivor_logic(self, dt, log):
        hunter = self.game.player
        
        # 1. SMART DANGER DETECTION
        # Don't use simple math.hypot alone. Walls exist!
        euclidean_dist = math.hypot(hunter.x - self.x, hunter.y - self.y)
        true_danger_dist = 999.0 # Assume far until proven close
        
        # Optimization: Only calculate A* if visually close (within 12 tiles)
        if euclidean_dist < 12.0:
            path_to_hunter = a_star_search(self.game.map, (int(self.x), int(self.y)), (int(hunter.x), int(hunter.y)))
            if path_to_hunter:
                true_danger_dist = len(path_to_hunter)
            else:
                # No path = blocked by walls = SAFE
                true_danger_dist = 999.0
        
        # 2. PRESSURE REWARDS (Based on TRUE distance)
        # We only feel pressure if the Hunter can ACTUALLY walk to us quickly
        if true_danger_dist < 10.0:
            self.xp_gained_this_match -= 0.5 * dt # Stress penalty
            
            # Did we run away?
            old_dist = math.hypot(hunter.x - self.last_pos[0], hunter.y - self.last_pos[1])
            if euclidean_dist > old_dist: 
                self.xp_gained_this_match += 2.0 * dt # Reward for running
        
        # Anti-Camping (Only if danger is real)
        if self.still_penalty_timer >= 1.0:
            if true_danger_dist < 15.0: self.xp_gained_this_match -= 2.0 * dt
            self.still_penalty_timer = 0

        # 3. DECISION CYCLE
        self.decision_timer -= dt
        if self.decision_timer <= 0:
            self.decision_timer = 0.25
            reward = 0.1
            
            # --- STATE TRANSITIONS ---
            # EVADE only if REAL danger is < 8 tiles away
            if true_danger_dist < 8.0:
                self.state = "EVADE"
                if self.boost_cooldown <= 0 and true_danger_dist < 4.0:
                    self.activate_boost(log)
            else:
                # If safe, focus on OBJECTIVES
                if self.game.keys_collected < self.game.keys_required:
                    if self.known_keys: self.state = "SCAVENGE"
                    else: self.state = "EXPLORE"
                else:
                    if self.known_exits: self.state = "SCAVENGE"
                    else: self.state = "EXPLORE"

            current_state_key = (int(true_danger_dist), self.state)
            if self.last_state_key:
                self.brain.learn(self.last_state_key, self.last_action, reward, current_state_key)
            self.last_state_key = current_state_key
            self.last_action = self.state

        if self.state == "EVADE": self.behavior_survivor_evade(hunter)
        elif self.state == "SCAVENGE": self.behavior_survivor_scavenge()
        elif self.state == "EXPLORE": self.behavior_explore_map()
        else: self.behavior_patrol()

    def behavior_survivor_scavenge(self):
        target_list = []
        if self.game.keys_collected < self.game.keys_required: target_list = self.known_keys
        else: target_list = self.known_exits
            
        if not target_list: 
            self.state = "EXPLORE"
            self.behavior_explore_map()
            return

        closest = min(target_list, key=lambda t: math.hypot(t[0]-self.x, t[1]-self.y))
        if not self.path or (len(self.path) > 0 and math.hypot(closest[0]-self.path[-1][0], closest[1]-self.path[-1][1]) > 1):
            self.path = a_star_search(self.game.map, (int(self.x), int(self.y)), closest)
        self.follow_path()

    def behavior_explore_map(self):
        if not self.path:
            # Try to find a random spot we haven't visited much (simple random for now)
            for _ in range(5):
                tx = random.randint(1, self.game.map.width - 2)
                ty = random.randint(1, self.game.map.height - 2)
                if not self.game.map.is_wall(tx, ty):
                    self.path = a_star_search(self.game.map, (int(self.x), int(self.y)), (tx, ty))
                    if self.path: break
        self.follow_path()

    # =========================================================
    # --- HUNTER BRAIN ---
    # =========================================================
    def run_hunter_logic(self, dt, log):
        if self.still_penalty_timer >= 2.0:
            self.xp_gained_this_match -= 2.0
            self.still_penalty_timer = 0
            self._log(log, "System", "CAMPING_PENALTY", -2.0)

        dist = math.hypot(self.game.player.x - self.x, self.game.player.y - self.y)
        can_see = (dist < self.current_vision_radius)
        
        if can_see:
            self.last_seen_pos = (self.game.player.x, self.game.player.y)
            self.state = "CHASE"

        self.decision_timer -= dt
        if self.decision_timer <= 0:
            self.decision_timer = 0.25
            
            if self.trap_cooldown <= 0 and len(self.active_traps) < 2:
                if self.state in ["PATROL", "INVESTIGATE"] and self.memory.is_hotspot(int(self.x), int(self.y)):
                    self.place_trap_internal(log)
                elif self.state == "CHASE" and 2.0 < dist < 5.0:
                    self.place_trap_internal(log)

            if self.state == "CHASE" and not can_see: self.state = "INVESTIGATE"
            elif self.state == "INVESTIGATE" and not self.path: self.state = self.brain.choose_action((int(dist), self.state))
            elif self.state == "PATROL" and random.random() < 0.1: self.state = self.brain.choose_action((int(dist), self.state))

        if self.state == "CHASE": self.behavior_chase()
        elif self.state == "INVESTIGATE": self.behavior_investigate()
        else: self.behavior_patrol()

    # =========================================================
    # --- UTILS ---
    # =========================================================
    def activate_boost(self, log_ref):
        self.is_boosting = True; self.boost_duration = 1.5; self.boost_cooldown = 15.0
        self.game.play_sound("pickup") 
        reward = -2.0 
        self.xp_gained_this_match += reward
        self._log(log_ref, "Ability", "BOOST_USED", reward)

    # ... inside AgentX class ...

    def behavior_survivor_evade(self, hunter):
        # --- FIX 3: SMART EVADE (Don't run into walls) ---
        
        # 1. Get current positions
        my_x, my_y = int(self.x), int(self.y)
        h_x, h_y = int(hunter.x), int(hunter.y)
        
        best_move = None
        max_dist = -1
        
        # 2. Check all 8 neighbors (including diagonals)
        neighbors = [
            (0, 1), (0, -1), (1, 0), (-1, 0), 
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        
        # Shuffle to prevent getting stuck in patterns
        random.shuffle(neighbors)
        
        for dx, dy in neighbors:
            nx, ny = my_x + dx, my_y + dy
            
            # Is this tile safe to walk on?
            if not self.game.map.is_wall(nx, ny):
                # Calculate distance from Hunter if I move there
                dist = math.hypot(nx - h_x, ny - h_y)
                
                # We want to MAXIMIZE distance
                if dist > max_dist:
                    max_dist = dist
                    best_move = (dx, dy)
        
        # 3. Execute Move
        if best_move:
            # Normalize vector to keep speed constant
            mx, my = best_move
            length = math.hypot(mx, my)
            if length > 0:
                self.move(mx/length, my/length)
        else:
            # If cornered (no valid moves), try to push past anyway (Panic)
            dx = self.x - hunter.x
            dy = self.y - hunter.y
            dist = math.hypot(dx, dy)
            if dist > 0: self.move(dx/dist, dy/dist)

    def place_trap_internal(self, log, brain="AI_Trap"):
        self.active_traps.append((int(self.x), int(self.y)))
        self.trap_cooldown = 15.0
        self.xp_gained_this_match += 5.0
        self._log(log, brain, "TRAP_PLACED", 5.0)

    def behavior_chase(self):
        target = (int(self.game.player.x), int(self.game.player.y))
        if not self.path or math.hypot(target[0]-self.path[-1][0], target[1]-self.path[-1][1]) > 1:
            self.path = a_star_search(self.game.map, (int(self.x), int(self.y)), target)
        self.follow_path()

    def behavior_investigate(self):
        if self.last_seen_pos:
            target = (int(self.last_seen_pos[0]), int(self.last_seen_pos[1]))
            if not self.path: self.path = a_star_search(self.game.map, (int(self.x), int(self.y)), target)
            self.follow_path()
            if not self.path: self.state = "PATROL"
        else: self.state = "PATROL"

    def behavior_patrol(self):
        if not self.path:
            tx = random.randint(1, self.game.map.width - 2)
            ty = random.randint(1, self.game.map.height - 2)
            if not self.game.map.is_wall(tx, ty):
                self.path = a_star_search(self.game.map, (int(self.x), int(self.y)), (tx, ty))
        self.follow_path()

    def follow_path(self):
        if self.path:
            tx, ty = self.path[0]
            dx = tx - self.x; dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 0.15: 
                self.path.pop(0)
                self.x, self.y = float(tx), float(ty)
                return
            if dist > 0: self.move(dx/dist, dy/dist)
        else: self.move(0, 0)

    def move(self, dir_x, dir_y):
        move_amount = self.speed * self.game.dt
        nx = self.x + dir_x * move_amount
        if not self.check_collision(nx, self.y): self.x = nx
        ny = self.y + dir_y * move_amount
        if not self.check_collision(self.x, ny): self.y = ny

    def check_collision(self, x, y):
        margin = 0.25
        points = [(x+margin, y+margin), (x+1-margin, y+margin), (x+margin, y+1-margin), (x+1-margin, y+1-margin)]
        for px, py in points:
            if self.game.map.is_wall(int(px), int(py)): return True
        return False

    def force_unstuck(self, log):
        self.xp_gained_this_match -= 5.0 
        self._log(log, "Physics", "WALL_HIT", -5.0)
        cx, cy = int(self.x + 0.5), int(self.y + 0.5)
        neighbors = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = cx + dx, cy + dy
            if not self.game.map.is_wall(nx, ny): neighbors.append((nx, ny))
        if neighbors:
            self.path = [random.choice(neighbors)]
            self.x, self.y = float(cx), float(cy)

    def update_dynamic_speed(self, pct, p_speed):
        self.speed = p_speed * (0.95 + (pct * 0.2))

    def _log(self, ref, brain, action, reward):
        if ref is not None:
            ref.append({'t': self.game.game_time, 'brain': brain, 'action': action, 'reward': reward})

    def _scan_for_keys(self): 
        return [] 
    
    def _scan_for_exits(self): 
        return []

    def handle_human_input(self, decisions_log_ref):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
        if dx!=0 or dy!=0:
            mag = (dx**2 + dy**2)**0.5
            dx /= mag; dy /= mag
            self.move(dx, dy)
        if keys[pygame.K_q]: 
            if self.trap_cooldown <= 0:
                self.place_trap_internal(decisions_log_ref, brain='Human')
        if keys[pygame.K_e]: self.activate_scan()

    def activate_scan(self):
        if self.scan_cooldown <= 0:
            self.is_scanning = True
            self.scan_duration = 1.0  
            self.scan_cooldown = 60.0 
            self.game.play_sound("scare")