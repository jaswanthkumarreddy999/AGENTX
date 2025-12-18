import pygame
import os

# CONFIG
TILE_SIZE = 32
ASSET_DIR = "assets/images"
os.makedirs(ASSET_DIR, exist_ok=True)

pygame.init()
screen = pygame.display.set_mode((100, 100)) # Hidden surface

def create_wolf_sprite():
    # 1. Create a fully transparent surface
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    
    # 2. Draw Wolf Head (Pixel Art Style)
    # Fur (Gray)
    pygame.draw.polygon(surf, (120, 130, 140), [
        (4, 8), (10, 2), (22, 2), (28, 8), # Top Head
        (30, 18), (22, 30), (10, 30), (2, 18) # Jaw
    ])
    # Ears (Darker Gray)
    pygame.draw.polygon(surf, (80, 90, 100), [(4, 8), (2, 0), (10, 4)]) # Left Ear
    pygame.draw.polygon(surf, (80, 90, 100), [(28, 8), (30, 0), (22, 4)]) # Right Ear
    
    # Eyes (Glowing Red - SCARY)
    pygame.draw.rect(surf, (255, 0, 0), (8, 12, 4, 4))
    pygame.draw.rect(surf, (255, 0, 0), (20, 12, 4, 4))
    
    # Snout/Nose (Black)
    pygame.draw.rect(surf, (20, 20, 20), (12, 18, 8, 8))
    pygame.draw.rect(surf, (0, 0, 0), (14, 20, 4, 2)) # Nose tip

    # Teeth (White - Sharp)
    pygame.draw.polygon(surf, (255, 255, 255), [(13, 26), (14, 30), (15, 26)])
    pygame.draw.polygon(surf, (255, 255, 255), [(17, 26), (18, 30), (19, 26)])

    # Save
    pygame.image.save(surf, os.path.join(ASSET_DIR, "hunter.png"))
    print(">>> Created Perfect Hunter Sprite (hunter.png)")

def create_survivor_sprite():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    
    # Body (Blue Shirt)
    pygame.draw.circle(surf, (0, 100, 255), (16, 16), 14)
    # Head (Skin tone)
    pygame.draw.circle(surf, (255, 200, 180), (16, 16), 8)
    # Flashlight Beam (Semi-transparent Yellow)
    beam = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(beam, (255, 255, 0, 100), [(16, 16), (32, 0), (32, 32)])
    surf.blit(beam, (0,0))
    
    pygame.image.save(surf, os.path.join(ASSET_DIR, "survivor.png"))
    print(">>> Created Perfect Survivor Sprite (survivor.png)")

create_wolf_sprite()
create_survivor_sprite()
pygame.quit()