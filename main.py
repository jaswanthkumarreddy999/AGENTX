import pygame
import sys
import os
import math
from config import *

# --- IMPORTS ---
from engine.level_loader import LevelLoader
from engine.maze_generator import MazeGenerator
from engine.tilemap import TileMap
from engine.particles import ParticleSystem 
from engine.fog import FogSystem 
from engine.recorder import GameRecorder
from engine.dashboard import Dashboard
from engine.ui import GameOverUI 
from player.player import Player
from agent.agent_x import AgentX

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() 
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_w, self.screen_h = self.screen.get_size()
        pygame.display.set_caption("Agent-X: Learning Environment")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font_title = pygame.font.SysFont("Arial", 80, bold=True)
        self.font_option = pygame.font.SysFont("Arial", 50, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 30)
        self.font = pygame.font.SysFont("Arial", 24)
        
        # --- 1. INITIALIZE VARIABLES FIRST ---
        self.cam_speed = 10.0
        self.time_scale = 1.0 
        
        # --- 2. LOAD ASSETS ---
        self.assets = self.load_assets()
        
        # --- 3. START MUSIC SAFELY (Fixed KeyError) ---
        self.switch_music("menu_music")

        self.level_loader = LevelLoader()
        self.particles = ParticleSystem()
        self.fog = FogSystem(self.screen.get_size()) 
        self.recorder = GameRecorder()
        self.dashboard = Dashboard(self.screen_w, self.screen_h)
        self.ui = GameOverUI(self.screen_w, self.screen_h)
        
        self.current_level_num = 1
        self.running = True
        self.true_scroll_x = 0
        self.true_scroll_y = 0
        self.game_time = 0
        
        # STATE & MODE
        self.state = "MENU" 
        self.mode = "PVE" 
        self.role = "SURVIVOR" 
        self.last_winner = None
        self.last_score = 0
        self.current_match_metrics = {} 
        self.still_player_timer = 0.0 
        self.player_last_pos = (0, 0)
        self.reveal_timer = 0.0

    def load_assets(self):
        assets = {
            "survivor_img": None, "hunter_img": None, 
            "pickup_snd": None, "scare_snd": None, "win_snd": None, 
            "menu_bg": None, 
            "menu_music": None, "game_music": None # No floor_img to keep tile structure safe
        }
        
        # Images
        try:
            if os.path.exists("assets/images/menu_bg.png"):
                bg = pygame.image.load("assets/images/menu_bg.png").convert()
                assets["menu_bg"] = pygame.transform.scale(bg, (self.screen_w, self.screen_h))
        except: pass
        try:
            if os.path.exists("assets/images/survivor.png"):
                s_full = pygame.image.load("assets/images/survivor.png").convert()
                crop_size = 32 if s_full.get_width() < 64 else 64
                s_img = s_full.subsurface((0, 0, crop_size, crop_size))
                s_img.set_colorkey(s_img.get_at((0,0))) 
                assets["survivor_img"] = pygame.transform.scale(s_img, (TILE_SIZE, TILE_SIZE))
            if os.path.exists("assets/images/hunter.png"):
                h_full = pygame.image.load("assets/images/hunter.png").convert()
                crop_size = 32 if h_full.get_width() < 64 else 64
                h_img = h_full.subsurface((0, 0, crop_size, crop_size))
                h_img.set_colorkey(h_img.get_at((0,0)))
                assets["hunter_img"] = pygame.transform.scale(h_img, (TILE_SIZE, TILE_SIZE))
        except: pass

        # Audio
        try:
            assets["pickup_snd"] = pygame.mixer.Sound("assets/audio/pickup.wav")
            assets["scare_snd"] = pygame.mixer.Sound("assets/audio/jumpscare.wav")
            assets["win_snd"] = pygame.mixer.Sound("assets/audio/win.wav")
        except: pass
        
        # Music Paths
        if os.path.exists("assets/audio/menu_theme.mp3"):
            assets["menu_music"] = "assets/audio/menu_theme.mp3"
        if os.path.exists("assets/audio/ambience.mp3"):
            assets["game_music"] = "assets/audio/ambience.mp3"

        return assets

    def switch_music(self, track_key):
        if self.time_scale > 2.0: 
            pygame.mixer.music.stop()
            return
        path = self.assets.get(track_key)
        if path:
            pygame.mixer.music.fadeout(500)
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
            except: pass

    def play_sound(self, name):
        if self.time_scale > 2.0: return 
        if self.assets.get(f"{name}_snd"): self.assets[f"{name}_snd"].play()

    def draw_text_shadow(self, surf, text, font, color, x, y, align="center"):
        shadow = font.render(text, True, BLACK)
        main_txt = font.render(text, True, color)
        if align == "center":
            rect = main_txt.get_rect(center=(x, y))
            s_rect = shadow.get_rect(center=(x+3, y+3))
        else:
            rect = main_txt.get_rect(topleft=(x, y))
            s_rect = shadow.get_rect(topleft=(x+3, y+3))
        surf.blit(shadow, s_rect); surf.blit(main_txt, rect)

    def update_menu(self):
        if self.assets.get("menu_bg"):
            self.screen.blit(self.assets["menu_bg"], (0, 0))
            overlay = pygame.Surface((self.screen_w, self.screen_h))
            overlay.fill(BLACK); overlay.set_alpha(100)
            self.screen.blit(overlay, (0,0))
        else: self.screen.fill((20, 20, 30))

        cx, cy = self.screen_w // 2, self.screen_h // 2
        self.draw_text_shadow(self.screen, "AGENT-X", self.font_title, (0, 255, 255), cx, cy - 180)
        self.draw_text_shadow(self.screen, "TRAINING SIMULATION", self.font_small, (200, 200, 200), cx, cy - 110)
        
        self.draw_text_shadow(self.screen, "1. SURVIVOR MODE", self.font_option, BLUE, cx, cy - 30)
        self.draw_text_shadow(self.screen, "(You vs AI Hunter)", self.font_small, (100, 100, 255), cx, cy + 10)
        
        self.draw_text_shadow(self.screen, "2. HUNTER MODE", self.font_option, RED, cx, cy + 80)
        self.draw_text_shadow(self.screen, "(You vs AI Survivor)", self.font_small, (255, 100, 100), cx, cy + 120)
        
        self.draw_text_shadow(self.screen, "3. SPECTATOR (AI vs AI)", self.font_option, (0, 255, 0), cx, cy + 190)
        self.draw_text_shadow(self.screen, "(Training Mode - No Fog)", self.font_small, (100, 255, 100), cx, cy + 230)
        
        pygame.display.flip()

    def new_game(self):
        if hasattr(self, 'agent') and isinstance(self.agent, AgentX): 
            self.agent.memory.save(self.current_level_num)
            self.agent.brain.save_brain()
        if hasattr(self, 'ent_hunter') and isinstance(self.ent_hunter, AgentX): self.ent_hunter.brain.save_brain()
        if hasattr(self, 'ent_survivor') and isinstance(self.ent_survivor, AgentX): self.ent_survivor.brain.save_brain()

        self.recorder.reset() 
        self.game_time = 0
        self.keys_collected = 0
        self.keys_required = 3 + (self.current_level_num // 2)
        self.time_scale = 1.0 
        self.switch_music("game_music")
        
        maze_size = 10 + (self.current_level_num - 1)
        generator = MazeGenerator(width=maze_size, height=maze_size)
        generator.generate(level=self.current_level_num)
        temp_path = os.path.join("data", "levels", "temp_level.txt")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        generator.save_to_file(temp_path)
        self.map = self.level_loader.load_from_file(temp_path) 
        
        p_start = (1, 1); a_start = (1, 1)
        for y in range(self.map.height):
            for x in range(self.map.width):
                cell = self.map.grid[y][x]
                if cell == 'P': p_start = (x, y)
                elif cell == 'A': a_start = (x, y)
                elif cell == 'k': self.recorder.log_key_location(x, y)

        if self.mode == "PVE": 
            self.ent_survivor = Player(self, p_start[0], p_start[1], is_human=True)
            self.ent_hunter = AgentX(self, a_start[0], a_start[1], role="HUNTER")
            self.role = "SURVIVOR"
        elif self.mode == "EVP": 
            self.ent_survivor = AgentX(self, a_start[0], a_start[1], role="SURVIVOR")
            self.ent_hunter = Player(self, p_start[0], p_start[1], is_human=True)
            self.role = "HUNTER"
        else: 
            self.ent_survivor = AgentX(self, p_start[0], p_start[1], role="SURVIVOR")
            self.ent_hunter = AgentX(self, a_start[0], a_start[1], role="HUNTER")
            self.role = "SPECTATOR"
            
        if isinstance(self.ent_survivor, AgentX): self.ent_survivor.memory.initialize_map_data(self.map.grid)
        if isinstance(self.ent_hunter, AgentX): self.ent_hunter.memory.initialize_map_data(self.map.grid)
        
        if isinstance(self.ent_survivor, AgentX): self.ent_survivor.game.player = self.ent_hunter 
        if isinstance(self.ent_hunter, AgentX): self.ent_hunter.game.player = self.ent_survivor

        self.true_scroll_x = (p_start[0] * TILE_SIZE) - (self.screen_w // 2)
        self.true_scroll_y = (p_start[1] * TILE_SIZE) - (self.screen_h // 2)
        
        if self.mode == "AVA": ai_role_log = "AI_VS_AI"
        elif self.mode == "PVE": ai_role_log = "HUNTER"
        elif self.mode == "EVP": ai_role_log = "SURVIVOR"
        
        self.current_match_metrics = {
            'decisions_log': [], 'xp_gained': 0.0, 'agent_level': 1,
            'agent_role': ai_role_log,
            'map_width': self.map.width, 'map_height': self.map.height, 'map_grid': self.map.grid,
            'start_keys': self.recorder.key_start_locations[:], 'player_score': 0, 'winner': None
        }
        
        self.still_player_timer = 0.0
        self.player_last_pos = (self.ent_survivor.x, self.ent_survivor.y)
        self.state = "PLAYING"
        self.reveal_timer = 0.0

    def run(self):
        while self.running:
            # --- TIME SCALING LOGIC ---
            raw_dt = self.clock.tick(FPS) / 1000.0
            self.dt = raw_dt * self.time_scale
            # --------------------------
            
            self.events()
            if self.state == "MENU": self.update_menu()
            elif self.state == "PLAYING": self.update_game(); self.draw_game()
            elif self.state == "GAMEOVER": self.ui.draw(self.screen, self.last_winner, self.last_score); pygame.display.flip()
            elif self.state == "DASHBOARD": self.dashboard.update(); self.dashboard.draw(self.screen); pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "MENU": self.quit()
                    else: 
                        if hasattr(self, 'ent_hunter') and isinstance(self.ent_hunter, AgentX): self.ent_hunter.brain.save_brain()
                        if hasattr(self, 'ent_survivor') and isinstance(self.ent_survivor, AgentX): self.ent_survivor.brain.save_brain()
                        self.state = "MENU"
                        self.switch_music("menu_music")

                if self.state == "MENU":
                    if event.key == pygame.K_1: self.mode = "PVE"; self.new_game()
                    elif event.key == pygame.K_2: self.mode = "EVP"; self.new_game()
                    elif event.key == pygame.K_3: self.mode = "AVA"; self.new_game()
                elif self.state == "GAMEOVER" and event.key == pygame.K_SPACE:
                    self.state = "DASHBOARD"
                    if self.recorder.history: self.dashboard.load_snapshot(len(self.recorder.history) - 1)
                elif self.state == "DASHBOARD":
                    if event.key == pygame.K_SPACE: self.current_level_num += 1; self.new_game()
                    elif event.key == pygame.K_LEFT: self.dashboard.load_snapshot(self.dashboard.view_index - 1)
                    elif event.key == pygame.K_RIGHT: self.dashboard.load_snapshot(self.dashboard.view_index + 1)
                
                # --- SPEED CONTROLS (ONLY IN MODE 3) ---
                if self.state == "PLAYING" and self.mode == "AVA":
                    if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS: # [+] Speed Up
                        self.time_scale = min(10.0, self.time_scale + 1.0)
                    elif event.key == pygame.K_MINUS: # [-] Slow Down
                        self.time_scale = max(1.0, self.time_scale - 1.0)
            
            if self.state == "DASHBOARD": self.dashboard.handle_dashboard_event(event)

    def update_game(self):
        self.game_time += self.dt
        self.recorder.record_frame(self.game_time, self.ent_survivor, self.ent_hunter)
        if self.reveal_timer > 0: self.reveal_timer -= self.dt
        pct = 0.0
        if self.keys_required > 0: pct = self.keys_collected / self.keys_required
        
        if isinstance(self.ent_survivor, Player): self.ent_survivor.update()
        else: 
            self.ent_survivor.game.player = self.ent_hunter 
            self.ent_survivor.update(self.current_match_metrics['decisions_log'])
            
        if isinstance(self.ent_hunter, Player): self.ent_hunter.update()
        else:
            self.ent_hunter.game.player = self.ent_survivor
            self.ent_hunter.update(self.current_match_metrics['decisions_log'])
            self.ent_hunter.update_dynamic_speed(pct, 4.0) 

        self.particles.update() 
        
        if self.mode != "AVA":
            viewer = self.ent_survivor if self.mode == "PVE" else self.ent_hunter
            vx, vy = viewer.x, viewer.y
            for y in range(max(0, int(vy)-10), min(self.map.height, int(vy)+10)):
                for x in range(max(0, int(vx)-10), min(self.map.width, int(vx)+10)):
                    if math.hypot(x-vx, y-vy) < 8: self.map.visited[y][x] = True

        if hasattr(self.ent_hunter, 'active_traps'):
            sx, sy = int(self.ent_survivor.x + 0.5), int(self.ent_survivor.y + 0.5)
            for i, trap in enumerate(self.ent_hunter.active_traps):
                tx, ty = trap
                if sx == tx and sy == ty:
                    self.play_sound("scare")
                    self.recorder.log_event(self.game_time, "SURVIVOR_TRAPPED")
                    self.ent_hunter.active_traps.pop(i)
                    if isinstance(self.ent_hunter, AgentX):
                        self.ent_hunter.xp_gained_this_match += 30.0
                        self.current_match_metrics['decisions_log'].append({'t': self.game_time,'brain': 'Hunter','action': 'TRAP_SUCCESS','reward': 30.0})
                    if isinstance(self.ent_survivor, AgentX):
                        self.ent_survivor.xp_gained_this_match -= 50.0
                        self.ent_survivor.is_frozen = True; self.ent_survivor.freeze_timer = 2.0
                    elif isinstance(self.ent_survivor, Player):
                        self.ent_survivor.is_frozen = True; self.ent_survivor.freeze_timer = 2.0
                    self.reveal_timer = 2.0
                    self.particles.emit(tx*TILE_SIZE+16, ty*TILE_SIZE+16, (255, 100, 0), count=50)
                    print(">>> [GAME] SURVIVOR TRAPPED!")
                    break

        sx, sy = int(self.ent_survivor.x + 0.5), int(self.ent_survivor.y + 0.5)
        if self.map.grid[sy][sx] == 'k':
            self.keys_collected += 1; self.map.grid[sy][sx] = '.'
            self.recorder.log_event(self.game_time, "KEY_FOUND")
            self.play_sound("pickup")
            self.particles.emit(sx*TILE_SIZE+16, sy*TILE_SIZE+16, (255, 215, 0), count=20)
            if isinstance(self.ent_survivor, AgentX):
                self.ent_survivor.xp_gained_this_match += 50.0
                self.current_match_metrics['decisions_log'].append({'t': self.game_time,'brain': 'Survivor','action': 'KEY_COLLECTED','reward': 50.0})
                if (sx, sy) in self.ent_survivor.known_keys: self.ent_survivor.known_keys.remove((sx, sy))

        if self.map.grid[sy][sx] == 'E' and self.keys_collected >= self.keys_required:
            self.play_sound("win"); self.level_complete(winner="SURVIVOR")

        dist = math.hypot(self.ent_survivor.x - self.ent_hunter.x, self.ent_survivor.y - self.ent_hunter.y)
        if dist < 0.9:
            self.play_sound("scare")
            if isinstance(self.ent_survivor, AgentX):
                self.ent_survivor.xp_gained_this_match -= 100.0
                self.current_match_metrics['decisions_log'].append({'t': self.game_time,'brain': 'Survivor','action': 'CAUGHT','reward': -100.0})
            if isinstance(self.ent_hunter, AgentX):
                self.ent_hunter.xp_gained_this_match += 100.0
                self.current_match_metrics['decisions_log'].append({'t': self.game_time,'brain': 'Hunter','action': 'CATCH','reward': 100.0})
            self.level_complete(winner="HUNTER")

    def level_complete(self, winner):
        print(f"Match Complete. Winner: {winner}")
        metrics = self.recorder.get_metrics(self.map, winner=winner)
        if isinstance(self.ent_hunter, AgentX): self.ent_hunter.brain.save_brain()
        if isinstance(self.ent_survivor, AgentX): self.ent_survivor.brain.save_brain()
        
        if self.mode == "AVA": self.current_match_metrics['xp_gained'] = self.ent_survivor.xp_gained_this_match
        elif isinstance(self.ent_hunter, AgentX): self.current_match_metrics['xp_gained'] = self.ent_hunter.xp_gained_this_match
        else: self.current_match_metrics['xp_gained'] = self.ent_survivor.xp_gained_this_match

        self.current_match_metrics['winner'] = winner
        self.current_match_metrics['player_score'] = metrics.get('player_score', 0)
        metrics.update(self.current_match_metrics)
        self.recorder.add_match(metrics)
        self.last_winner = winner; self.last_score = metrics.get('player_score', 0)
        self.dashboard.set_data(self.recorder, metrics) 
        self.state = "GAMEOVER"

    def draw_game(self):
        self.screen.fill(BLACK)
        cam_x, cam_y = 0, 0
        if self.mode == "AVA":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: self.true_scroll_x -= self.cam_speed
            if keys[pygame.K_RIGHT]: self.true_scroll_x += self.cam_speed
            if keys[pygame.K_UP]: self.true_scroll_y -= self.cam_speed
            if keys[pygame.K_DOWN]: self.true_scroll_y += self.cam_speed
            cam_x, cam_y = int(self.true_scroll_x), int(self.true_scroll_y)
        else:
            target = self.ent_survivor if self.mode == "PVE" else self.ent_hunter
            cx = int((target.x * TILE_SIZE) - (self.screen_w // 2))
            cy = int((target.y * TILE_SIZE) - (self.screen_h // 2))
            self.true_scroll_x += (cx - self.true_scroll_x) * 0.1
            self.true_scroll_y += (cy - self.true_scroll_y) * 0.1
            cam_x, cam_y = int(self.true_scroll_x), int(self.true_scroll_y)

        if self.mode == "AVA":
            for y in range(self.map.height):
                for x in range(self.map.width): self.map.visited[y][x] = True
        
        # --- FIXED: DON'T PASS floor_img TO TILEMAP TO KEEP STRUCTURE SAME ---
        self.map.draw(self.screen, cam_x, cam_y)

        can_see_traps = False
        if self.mode == "EVP" or self.mode == "AVA" or self.state == "GAMEOVER": can_see_traps = True
        
        if can_see_traps and hasattr(self.ent_hunter, 'active_traps'):
            for tx, ty in self.ent_hunter.active_traps:
                screen_x = int(tx * TILE_SIZE) - cam_x
                screen_y = int(ty * TILE_SIZE) - cam_y
                rect = pygame.Rect(screen_x+4, screen_y+4, TILE_SIZE-8, TILE_SIZE-8)
                pygame.draw.line(self.screen, (255, 100, 0), (rect.left, rect.top), (rect.right, rect.bottom), 3)
                pygame.draw.line(self.screen, (255, 100, 0), (rect.right, rect.top), (rect.left, rect.bottom), 3)

        self.draw_entity_rotatable(self.ent_survivor, cam_x, cam_y)
        self.draw_entity_rotatable(self.ent_hunter, cam_x, cam_y)
        self.particles.draw(self.screen, cam_x, cam_y)

        if self.mode != "AVA":
            target = self.ent_survivor if self.mode == "PVE" else self.ent_hunter
            p_screen_x = int(target.x * TILE_SIZE) - cam_x + (TILE_SIZE // 2)
            p_screen_y = int(target.y * TILE_SIZE) - cam_y + (TILE_SIZE // 2)
            radius = getattr(target, 'vision_radius', 10)
            if hasattr(target, 'current_vision_radius'): radius = target.current_vision_radius
            self.fog.render(self.screen, (p_screen_x, p_screen_y), radius_tiles=radius)

        if self.reveal_timer > 0:
            ax, ay = self.ent_survivor.x, self.ent_survivor.y 
            sx = int(ax * TILE_SIZE) - cam_x + (TILE_SIZE // 2)
            sy = int(ay * TILE_SIZE) - cam_y + (TILE_SIZE // 2)
            alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.01)) * 255)
            s = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 0, alpha), (32, 32), 20, 2)
            self.screen.blit(s, (sx - 32, sy - 32))

        info = f"Keys: {self.keys_collected}/{self.keys_required} | Mode: {self.mode}"
        surf_info = self.font.render(info, True, WHITE)
        pygame.draw.rect(self.screen, (0,0,0), (10, 10, surf_info.get_width()+20, 40))
        pygame.draw.rect(self.screen, WHITE, (10, 10, surf_info.get_width()+20, 40), 2)
        self.screen.blit(surf_info, (20, 20))
        
        if self.mode == "PVE":
            bar_x, bar_y, bar_w, bar_h = 20, self.screen_h - 60, 200, 25
            pygame.draw.rect(self.screen, (50,50,50), (bar_x, bar_y, bar_w, bar_h))
            fill = self.ent_survivor.stamina / self.ent_survivor.max_stamina
            color = (0, 255, 255)
            if fill < 0.3: color = (255, 0, 0)
            pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(bar_w * fill), bar_h))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            lbl = self.font.render("SPRINT [SHIFT]", True, WHITE); self.screen.blit(lbl, (bar_x, bar_y - 25))
            
        elif self.mode == "EVP":
            bar_x, bar_y, bar_w, bar_h = 20, self.screen_h - 60, 200, 25
            trap_pct = 1.0; scan_pct = 1.0
            if self.ent_hunter.trap_cooldown > 0: trap_pct = 1.0 - (self.ent_hunter.trap_cooldown / 5.0)
            if self.ent_hunter.scan_cooldown > 0: scan_pct = 1.0 - (self.ent_hunter.scan_cooldown / 15.0)
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, (255, 140, 0), (bar_x, bar_y, int(bar_w * trap_pct), bar_h))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            t_lbl = self.font.render(f"TRAP [Q] ({len(self.ent_hunter.active_traps)}/2)", True, WHITE)
            self.screen.blit(t_lbl, (bar_x, bar_y - 25))
            scan_x = bar_x + bar_w + 30
            pygame.draw.rect(self.screen, (40, 40, 40), (scan_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, (0, 255, 0) if not self.ent_hunter.is_scanning else (255,0,0), (scan_x, bar_y, int(bar_w * scan_pct), bar_h))
            pygame.draw.rect(self.screen, WHITE, (scan_x, bar_y, bar_w, bar_h), 2)
            s_msg = "SCANNING!" if self.ent_hunter.is_scanning else "SCAN [E]"
            s_lbl = self.font.render(s_msg, True, WHITE)
            self.screen.blit(s_lbl, (scan_x, bar_y - 25))
            
        elif self.mode == "AVA":
            cam_txt = self.font_small.render("ARROWS: MOVE CAMERA | +/-: SPEED", True, (200, 200, 200))
            self.screen.blit(cam_txt, (self.screen_w//2 - cam_txt.get_width()//2, self.screen_h - 40))
            
            speed_str = f"SPEED: {self.time_scale:.1f}x"
            s_surf = self.font_small.render(speed_str, True, (0, 255, 0)) 
            
            box_w, box_h = 160, 40
            box_x = self.screen_w - box_w - 10
            box_y = 70
            
            pygame.draw.rect(self.screen, (0,0,0), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(self.screen, (0, 255, 0), (box_x, box_y, box_w, box_h), 2)
            
            text_rect = s_surf.get_rect(center=(box_x + box_w//2, box_y + box_h//2))
            self.screen.blit(s_surf, text_rect)

        pygame.display.flip()

    def draw_entity_rotatable(self, entity, cam_x, cam_y):
        screen_x = int(entity.x * TILE_SIZE) - cam_x + (TILE_SIZE // 2)
        screen_y = int(entity.y * TILE_SIZE) - cam_y + (TILE_SIZE // 2)
        radius = 12; color = entity.color
        img = None
        if self.assets.get("survivor_img") and entity == self.ent_survivor: img = self.assets["survivor_img"]
        elif self.assets.get("hunter_img") and entity == self.ent_hunter: img = self.assets["hunter_img"]
        
        if img:
            angle = getattr(entity, 'angle', 0)
            if entity == self.ent_hunter and isinstance(entity, AgentX): angle = 0 
            rot_img = pygame.transform.rotate(img, angle)
            new_rect = rot_img.get_rect(center=(screen_x, screen_y))
            self.screen.blit(rot_img, new_rect)
        else:
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), 10)

    def quit(self):
        if hasattr(self, 'agent'): self.agent.memory.save(self.current_level_num)
        if hasattr(self, 'ent_hunter') and isinstance(self.ent_hunter, AgentX): self.ent_hunter.brain.save_brain()
        if hasattr(self, 'ent_survivor') and isinstance(self.ent_survivor, AgentX): self.ent_survivor.brain.save_brain()
        if hasattr(self, 'player') and hasattr(self.player, 'save_memory'): self.player.save_memory()
        pygame.quit(); sys.exit()

if __name__ == "__main__":
    if not os.path.exists("data/levels"): os.makedirs("data/levels")
    game = Game()
    game.run()