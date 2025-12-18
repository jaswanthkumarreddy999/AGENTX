import pygame
import math
import json
from config import *

# COLORS
COLOR_BG = (10, 10, 15)       
COLOR_PANEL = (18, 18, 25)    
COLOR_BORDER = (40, 40, 50)
COLOR_TEXT_MAIN = (255, 255, 255)
COLOR_TEXT_DIM = (120, 120, 130)

COLOR_SURVIVOR_THEME = (0, 240, 255) 
COLOR_HUNTER_THEME   = (255, 50, 50) 
COLOR_ACCENT         = (0, 255, 128) 

COLOR_REWARD_POS = (0, 255, 0)
COLOR_REWARD_NEG = (255, 50, 50)

class Dashboard:
    def __init__(self, screen_w, screen_h):
        self.width = screen_w
        self.height = screen_h
        
        self.font_header = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_big_data = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_label = pygame.font.SysFont("Arial", 14)
        self.font_insight = pygame.font.SysFont("Consolas", 13) 
        
        self.replay_frame_idx = 0
        self.replay_speed = 4 
        self.recorder = None 
        self.view_index = 0  
        self.active_metrics = {}
        self.graph_points_p = []
        self.graph_points_a = []
        self.processed_insights = [] 
        self.key_timings = {} 
        self.insight_scroll_offset = 0 
        self.line_height = 20          
        self.current_view_role = "SURVIVOR" 

    def set_data(self, recorder, metrics):
        self.recorder = recorder
        self.view_index = len(recorder.history) - 1
        
        # SMART DEFAULT: View the AI, not the Player
        game_mode_role = metrics.get('agent_role', 'HUNTER')
        
        if game_mode_role == "AI_VS_AI":
            self.current_view_role = "SURVIVOR" # Default to Survivor for AVA
        else:
            # If PVE, agent is Hunter. If EVP, agent is Survivor.
            self.current_view_role = game_mode_role
            
        self.load_snapshot(self.view_index)

    def load_snapshot(self, index):
        if not self.recorder or not self.recorder.history: return
        if index < 0: index = 0
        if index >= len(self.recorder.history): index = len(self.recorder.history) - 1
        
        self.view_index = index
        self.active_metrics = self.recorder.history[index]
        self.replay_frame_idx = 0
        self._refresh_view_data()

    def _refresh_view_data(self):
        frames = self.active_metrics.get('frames', [])
        self._process_graph_data(frames)
        self.processed_insights = self._process_match_log(self.active_metrics) 
        self._calculate_key_timings(frames)
        self.insight_scroll_offset = 0 

    def _calculate_key_timings(self, frames):
        self.key_timings = {}
        start_keys = self.active_metrics.get('start_keys', [])
        if not start_keys: return
        keys_to_track = list(start_keys)
        for frame in frames:
            t = frame['t']
            # p_pos is ALWAYS Survivor in recorder
            target_pos = frame['p_pos'] 

            for k in keys_to_track[:]: 
                kx, ky = k
                dist = math.hypot(target_pos[0] - kx, target_pos[1] - ky)
                if dist < 0.6:
                    self.key_timings[k] = t
                    keys_to_track.remove(k) 

    # --- NEW: Check if the current view is a Human or AI ---
    def _is_viewing_ai(self):
        # agent_role tells us which entity was the AI
        ai_role = self.active_metrics.get('agent_role', 'HUNTER')
        
        if ai_role == "AI_VS_AI": return True 
        if self.current_view_role == ai_role: return True 
        return False 

    def _process_match_log(self, m):
        insights = []
        is_ai = self._is_viewing_ai()
        
        role_label = "AI AGENT" if is_ai else "HUMAN PLAYER"
        insights.append(f"> [LOG VIEW: {self.current_view_role} ({role_label})]")

        if not is_ai:
            insights.append("> Neural logs unavailable for Human Player.")
            insights.append("> Showing game events only.")
            events = m.get('events_list', [])
            for e in events:
                insights.append(f">> EVENT: {e}")
            return insights

        decisions_log = m.get('decisions_log', [])
        filtered_log = []
        for d in decisions_log:
            brain = d.get('brain', '')
            if self.current_view_role == "HUNTER":
                if brain in ["Survivor", "Objective", "Evade"]: continue
            if self.current_view_role == "SURVIVOR":
                if brain in ["Hunter", "Predator", "Trap"]: continue
            filtered_log.append(d)

        SAMPLE_RATE = max(1, len(filtered_log) // 12) 
        for i, d in enumerate(filtered_log):
            if i % SAMPLE_RATE == 0:
                brain = d.get('brain', 'N/A')
                action = d.get('action', 'N/A')
                reward = d.get('reward', 0)
                prefix = "++" if reward > 0 else "--" if reward < 0 else ".."
                insights.append(f"{prefix} t={d.get('t', 0):.1f} | {brain:8} | {action:12} | {reward:+.1f}")

        return insights

    def _process_graph_data(self, frames):
        self.graph_points_p = []
        self.graph_points_a = []
        if not frames: return
        total = len(frames); sample = max(1, total // 50)
        curr_p_dist, curr_a_dist = 0, 0
        prev_p = frames[0]['p_pos']; prev_a = frames[0]['a_pos']
        for i, f in enumerate(frames):
            dist_p = math.hypot(f['p_pos'][0]-prev_p[0], f['p_pos'][1]-prev_p[1])
            dist_a = math.hypot(f['a_pos'][0]-prev_a[0], f['a_pos'][1]-prev_a[1])
            curr_p_dist += dist_p; curr_a_dist += dist_a
            prev_p = f['p_pos']; prev_a = f['a_pos']
            if i % sample == 0 or i == total - 1:
                self.graph_points_p.append(curr_p_dist)
                self.graph_points_a.append(curr_a_dist)

    def update(self):
        frames = self.active_metrics.get('frames', [])
        if frames:
            self.replay_frame_idx += self.replay_speed
            if self.replay_frame_idx >= len(frames): self.replay_frame_idx = 0

    def handle_dashboard_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if self.current_view_role == "SURVIVOR": self.current_view_role = "HUNTER"
                else: self.current_view_role = "SURVIVOR"
                self._refresh_view_data() 

        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0: self.insight_scroll_offset = max(0, self.insight_scroll_offset - 1)
            elif event.y < 0:
                max_lines = (180 - 45) // self.line_height 
                max_offset = max(0, len(self.processed_insights) - max_lines)
                self.insight_scroll_offset = min(max_offset, self.insight_scroll_offset + 1)

    def draw(self, screen):
        screen.fill(COLOR_BG)
        margin = 15
        
        is_ai = self._is_viewing_ai()
        role_type = "AI AGENT" if is_ai else "HUMAN"
        
        if self.current_view_role == "SURVIVOR":
            theme_color = COLOR_SURVIVOR_THEME
            opp_color = COLOR_HUNTER_THEME
            title_text = f"SURVIVOR ANALYSIS ({role_type})"
        else:
            theme_color = COLOR_HUNTER_THEME
            opp_color = COLOR_SURVIVOR_THEME
            title_text = f"HUNTER ANALYSIS ({role_type})"

        self._draw_header(screen, margin, title_text, theme_color)

        row1_y = 70; row1_h = 100; col_w = (self.width - (margin*4)) // 3
        
        score = self.active_metrics.get('player_score', 0)
        self._draw_stat_card(screen, pygame.Rect(margin, row1_y, col_w, row1_h), 
                             "GAME SCORE", str(score), COLOR_TEXT_MAIN)
                             
        if is_ai:
            xp = self.active_metrics.get('xp_gained', 0.0)
            self._draw_stat_card(screen, pygame.Rect(margin*2 + col_w, row1_y, col_w, row1_h), 
                                 f"NEURAL REWARD", f"{xp:+.0f}", theme_color)
        else:
            self._draw_stat_card(screen, pygame.Rect(margin*2 + col_w, row1_y, col_w, row1_h), 
                                 "PLAYER RANK", "HUMAN", COLOR_TEXT_DIM)
        
        if self.current_view_role == "SURVIVOR":
            keys = self.active_metrics.get('keys_found', 0) 
            if keys == 0:
                decisions = self.active_metrics.get('decisions_log', [])
                keys = len([d for d in decisions if d.get('action') == 'KEY_COLLECTED'])
            self._draw_stat_card(screen, pygame.Rect(margin*3 + col_w*2, row1_y, col_w, row1_h), 
                                 "KEYS SECURED", str(keys), COLOR_ACCENT)
        else:
            events = self.active_metrics.get('events_list', [])
            traps = events.count("SURVIVOR_TRAPPED") + events.count("TRAP_TRIGGERED")
            self._draw_stat_card(screen, pygame.Rect(margin*3 + col_w*2, row1_y, col_w, row1_h), 
                                 "TRAPS SPRUNG", str(traps), COLOR_ACCENT)

        row2_y = row1_y + row1_h + margin; row2_h = 180
        self._draw_insights_panel(screen, pygame.Rect(margin, row2_y, col_w*2 + margin, row2_h), theme_color)
        
        if is_ai:
            self._draw_evolution_panel(screen, pygame.Rect(margin*3 + col_w*2, row2_y, col_w, row2_h), theme_color) 
        else:
            self._draw_human_panel(screen, pygame.Rect(margin*3 + col_w*2, row2_y, col_w, row2_h))

        row3_y = row2_y + row2_h + margin; row3_h = self.height - row3_y - 40
        self._draw_graph_card(screen, pygame.Rect(margin, row3_y, col_w, row3_h), theme_color, opp_color)
        self._draw_map_replay(screen, pygame.Rect(margin*2 + col_w, row3_y, col_w*2 + margin, row3_h))
        self._draw_footer(screen)

    def _draw_header(self, screen, margin, text, color):
        # Left: Role Title
        t_surf = self.font_header.render(text, True, color)
        screen.blit(t_surf, (margin, 15))
        
        # Right: Tab Hint
        hint_surf = self.font_title.render("[TAB] SWITCH ROLE VIEW", True, COLOR_TEXT_DIM)
        screen.blit(hint_surf, (self.width - hint_surf.get_width() - margin, 15))
        
        # Right Bottom: Nav Hint
        nav_txt = "< ARROWS: HISTORY >"
        if self.recorder and len(self.recorder.history) > 1:
            nav_surf = self.font_title.render(nav_txt, True, COLOR_TEXT_DIM)
            screen.blit(nav_surf, (self.width - nav_surf.get_width() - margin, 40))

        # --- CENTER: MATCH NUMBER ---
        match_num = self.view_index + 1
        m_surf = self.font_header.render(f"MATCH #{match_num}", True, COLOR_TEXT_MAIN)
        screen.blit(m_surf, (self.width // 2 - m_surf.get_width() // 2, 15))
        # ----------------------------
    
    def _draw_stat_card(self, screen, rect, title, value, color):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, (color[0]//4, color[1]//4, color[2]//4), rect, 2, border_radius=8)
        t_surf = self.font_title.render(title, True, COLOR_TEXT_DIM)
        screen.blit(t_surf, (rect.x + 15, rect.y + 15))
        v_surf = self.font_big_data.render(value, True, color)
        screen.blit(v_surf, (rect.x + 15, rect.y + 45))

    def _draw_insights_panel(self, screen, rect, color):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        title = self.font_title.render("MATCH LOG", True, color)
        screen.blit(title, (rect.x + 15, rect.y + 15))
        content_start_y = rect.y + 45
        max_lines_fit = (rect.height - 45) // self.line_height 
        start_index = self.insight_scroll_offset
        end_index = min(start_index + max_lines_fit, len(self.processed_insights))
        y_off = content_start_y
        for i in range(start_index, end_index):
            line = self.processed_insights[i]
            c = COLOR_TEXT_MAIN
            if "++" in line: c = COLOR_REWARD_POS
            elif "--" in line: c = COLOR_REWARD_NEG
            screen.blit(self.font_insight.render(line, True, c), (rect.x+20, y_off))
            y_off += self.line_height

    def _draw_evolution_panel(self, screen, rect, color):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        new_total_xp = self.active_metrics.get('total_xp', 0)
        curr_lvl = max(1, self.active_metrics.get('agent_level', 1))
        l_surf = self.font_header.render(f"LEVEL {curr_lvl}", True, color)
        screen.blit(l_surf, (rect.centerx - l_surf.get_width()//2, rect.y + 15))
        MAX_XP = 2500 
        xp_in_lvl = max(0, new_total_xp) % MAX_XP
        pct = int((xp_in_lvl / MAX_XP) * 100)
        bar_rect = pygame.Rect(rect.x + 15, rect.bottom - 40, rect.w - 30, 12)
        pygame.draw.rect(screen, COLOR_BORDER, bar_rect, border_radius=5)
        fill_w = int(bar_rect.w * (pct/100))
        if fill_w > 0:
            pygame.draw.rect(screen, (color[0]//2, color[1]//2, color[2]//2), 
                             (bar_rect.x, bar_rect.y, fill_w, 12), border_radius=5)
        lbl = self.font_insight.render(f"XP: {int(xp_in_lvl)} / {MAX_XP}", True, COLOR_TEXT_DIM)
        screen.blit(lbl, (bar_rect.x, bar_rect.y - 15))

    def _draw_human_panel(self, screen, rect):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        msg = self.font_title.render("NO NEURAL DATA", True, COLOR_TEXT_DIM)
        screen.blit(msg, (rect.centerx - msg.get_width()//2, rect.centery))

    def _draw_graph_card(self, screen, rect, theme_col, opp_col):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, rect, 1, border_radius=8)
        screen.blit(self.font_title.render("MOVEMENT ACTIVITY", True, COLOR_TEXT_DIM), (rect.x+15, rect.y+10))
        max_v = max(max(self.graph_points_p or [1]), max(self.graph_points_a or [1]))
        plot_r = pygame.Rect(rect.x+10, rect.y+40, rect.w-20, rect.h-50)
        if len(self.graph_points_a) > 1:
            pts = []
            step = plot_r.w / (len(self.graph_points_a)-1)
            for i, val in enumerate(self.graph_points_a):
                pts.append((plot_r.x + i*step, plot_r.bottom - (val/max_v * plot_r.h)))
            pygame.draw.lines(screen, COLOR_HUNTER_THEME, False, pts, 2)
        if len(self.graph_points_p) > 1:
            pts = []
            step = plot_r.w / (len(self.graph_points_p)-1)
            for i, val in enumerate(self.graph_points_p):
                pts.append((plot_r.x + i*step, plot_r.bottom - (val/max_v * plot_r.h)))
            pygame.draw.lines(screen, COLOR_SURVIVOR_THEME, False, pts, 2)

    def _draw_map_replay(self, screen, rect):
        pygame.draw.rect(screen, COLOR_PANEL, rect, border_radius=8)
        frames = self.active_metrics.get('frames', [])
        map_grid = self.active_metrics.get('map_grid', [])
        if not frames: return
        
        # Consistent coloring: P_POS is always Survivor (Blue), A_POS is always Hunter (Red)
        col_s = COLOR_SURVIVOR_THEME
        col_h = COLOR_HUNTER_THEME
        
        frame = frames[int(self.replay_frame_idx)]
        map_w, map_h = len(map_grid[0]), len(map_grid)
        scale = min(rect.w / map_w, rect.h / map_h) * 0.9
        off_x = rect.centerx - (map_w * scale) / 2
        off_y = rect.centery - (map_h * scale) / 2
        for y, row in enumerate(map_grid):
            for x, char in enumerate(row):
                sx, sy = off_x+x*scale, off_y+y*scale
                if char == '#': pygame.draw.rect(screen, (30,30,40), (sx, sy, scale, scale))
                elif char == 'E': pygame.draw.rect(screen, (0,255,0), (sx, sy, scale, scale), 1)
        start_keys = self.active_metrics.get('start_keys', [])
        current_time = frame['t']
        for kx, ky in start_keys:
            is_collected = False
            if (kx, ky) in self.key_timings:
                if current_time >= self.key_timings[(kx, ky)]: is_collected = True
            if not is_collected:
                sx, sy = off_x + kx*scale, off_y + ky*scale
                pygame.draw.circle(screen, (255, 215, 0), (int(sx + scale/2), int(sy + scale/2)), int(scale/3))
        current_traps = frame.get('traps', [])
        for tx, ty in current_traps:
            sx, sy = off_x + tx*scale, off_y + ty*scale
            pygame.draw.line(screen, (255, 50, 50), (sx, sy), (sx + scale, sy + scale), 2)
            pygame.draw.line(screen, (255, 50, 50), (sx + scale, sy), (sx, sy + scale), 2)
            
        px, py = frame['p_pos'] # Survivor
        ax, ay = frame['a_pos'] # Hunter
        
        pygame.draw.circle(screen, col_s, (off_x+px*scale, off_y+py*scale), scale)
        pygame.draw.circle(screen, col_h, (off_x+ax*scale, off_y+ay*scale), scale)

    def _draw_footer(self, screen):
        txt = "SPACE: NEXT LEVEL | TAB: SWITCH VIEW | LEFT/RIGHT: HISTORY | ESC: QUIT"
        surf = self.font_label.render(txt, True, COLOR_TEXT_DIM)
        screen.blit(surf, (self.width//2 - surf.get_width()//2, self.height - 20))