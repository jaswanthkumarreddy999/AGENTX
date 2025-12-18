import pygame
import math
from config import TILE_SIZE, BLUE, RED

# --- NOTE: Do NOT import Player here. This IS the Player file. ---

class Player:
    def __init__(self, game, x, y, is_human=True):
        self.game = game
        self.x, self.y = float(x), float(y)
        self.is_human = is_human
        
        # --- ROLE BASED INITIALIZATION ---
        if self.game.role == "SURVIVOR":
            self.color = BLUE
            self.speed = 4.0
            self.base_vision = 12.0
            self.scan_vision = 12.0
            
            # SPRITE ORIENTATION FIX
            # 0 degrees if sprite faces RIGHT in image
            # -90 degrees if sprite faces UP in image
            self.rotation_offset = 0 
            
        else: # HUNTER
            self.color = RED
            self.speed = 4.2 
            self.base_vision = 5.0
            self.scan_vision = 10.0
            
            # HUNTER FIX: Likely faces UP in the image file
            self.rotation_offset = -90 
            
        self.vision_radius = self.base_vision
        
        # Stats
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.is_sprinting = False
        
        # Abilities
        self.active_traps = []
        self.trap_cooldown = 0
        self.is_scanning = False
        self.scan_cooldown = 0
        self.scan_timer = 0
        
        # Movement
        self.angle = 0
        self.last_dx, self.last_dy = 0, 0
        self.is_frozen = False
        self.freeze_timer = 0

    def update(self):
        dt = self.game.dt
        
        if self.is_frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0: self.is_frozen = False
            return

        # Cooldowns
        if self.trap_cooldown > 0: self.trap_cooldown -= dt
        if self.scan_cooldown > 0: self.scan_cooldown -= dt
        
        # --- HUNTER SPECIFIC UPDATE ---
        if self.game.role == "HUNTER":
            if self.is_scanning:
                self.scan_timer -= dt
                self.vision_radius = self.scan_vision
                if self.scan_timer <= 0:
                    self.is_scanning = False
                    self.vision_radius = self.base_vision
            else:
                self.vision_radius = self.base_vision
        else:
            self.vision_radius = self.base_vision

        if self.is_human:
            self.handle_input(dt)
            
        if not self.is_sprinting and self.stamina < self.max_stamina:
            self.stamina += 15 * dt

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -1
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = 1
        
        # Sprint Logic
        self.is_sprinting = False
        current_speed = self.speed
        if keys[pygame.K_LSHIFT] and self.stamina > 0:
            self.is_sprinting = True
            current_speed *= 1.5
            self.stamina -= 30 * dt
        
        if dx != 0 or dy != 0:
            length = math.hypot(dx, dy)
            dx, dy = dx/length, dy/length
            self.last_dx, self.last_dy = dx, dy
            
            nx = self.x + dx * current_speed * dt
            if not self.check_collision(nx, self.y): self.x = nx
            ny = self.y + dy * current_speed * dt
            if not self.check_collision(self.x, ny): self.y = ny
            
            # --- ROTATION FIX APPLIED HERE ---
            # Calculates angle based on movement (Right = 0)
            base_angle = math.degrees(math.atan2(-dy, dx))
            
            # Apply specific correction for this role
            self.angle = base_angle + self.rotation_offset

        # --- ABILITY INPUTS (HUNTER ONLY) ---
        if self.game.role == "HUNTER":
            if keys[pygame.K_q] and self.trap_cooldown <= 0:
                self.place_trap()
            if keys[pygame.K_e] and self.scan_cooldown <= 0:
                self.activate_scan()

    def place_trap(self):
        if len(self.active_traps) < 2:
            tx = int(self.x + 0.5)
            ty = int(self.y + 0.5)
            
            if (tx, ty) not in self.active_traps:
                self.active_traps.append((tx, ty))
                self.trap_cooldown = 5.0
                print(f"Trap Placed at {tx}, {ty}!")

    def activate_scan(self):
        self.is_scanning = True
        self.scan_timer = 1.0
        self.scan_cooldown = 15.0 
        self.game.play_sound("scare")

    def check_collision(self, x, y):
        margin = 0.25
        for px in [x+margin, x+1-margin]:
            for py in [y+margin, y+1-margin]:
                if self.game.map.is_wall(int(px), int(py)): return True
        return False

    def save_memory(self):
        pass