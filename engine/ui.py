import pygame
from config import *

class GameOverUI:
    def __init__(self, screen_w, screen_h):
        self.width = screen_w
        self.height = screen_h
        self.font_big = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 32)
        
        # Colors
        self.col_win = (0, 255, 100)
        self.col_lose = (255, 50, 50)
        self.col_bg = (0, 0, 0, 200) # Semi-transparent black

    def draw(self, screen, winner, score):
        # 1. Semi-transparent background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill(self.col_bg)
        screen.blit(overlay, (0,0))
        
        # 2. Text Logic
        if winner == "SURVIVOR":
            title_txt = "MISSION ACCOMPLISHED"
            color = self.col_win
            sub_txt = f"Agent Evaded! Score: {score}"
        else:
            title_txt = "TERMINATED"
            color = self.col_lose
            sub_txt = f"Agent X Caught You. Score: {score}"
            
        # 3. Render Title
        title_surf = self.font_big.render(title_txt, True, color)
        # Glow effect (simple shadow)
        title_shadow = self.font_big.render(title_txt, True, (color[0]//3, color[1]//3, color[2]//3))
        
        cx, cy = self.width // 2, self.height // 2
        
        screen.blit(title_shadow, (cx - title_surf.get_width()//2 + 4, cy - 100 + 4))
        screen.blit(title_surf, (cx - title_surf.get_width()//2, cy - 100))
        
        # 4. Render Subtitle
        sub_surf = self.font_small.render(sub_txt, True, WHITE)
        screen.blit(sub_surf, (cx - sub_surf.get_width()//2, cy))
        
        # 5. Instructions
        hint = self.font_small.render("Press SPACE for Analytics | ESC to Quit", True, GREY)
        screen.blit(hint, (cx - hint.get_width()//2, cy + 80))