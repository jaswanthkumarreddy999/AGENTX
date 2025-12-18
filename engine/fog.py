import pygame
from config import TILE_SIZE

class FogSystem:
    def __init__(self, screen_size):
        self.width, self.height = screen_size
        
        # The main surface that covers the screen
        self.fog_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Cache the current mask to avoid regenerating it every frame
        self.current_radius_px = 0
        self.light_mask = None

    def _create_light_gradient(self, radius):
        """Generates a radial gradient to subtract alpha."""
        # Limit radius to prevent crashing on huge numbers
        radius = min(radius, 1000) 
        
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0)) 
        
        center = (radius, radius)
        
        # Draw concentric circles for the gradient
        # Step size of 2 for performance
        for r in range(radius, 0, -2):
            # Alpha calculation: Center=High (Transparent), Edge=Low (Opaque)
            alpha = int(255 * (1 - (r / radius) ** 1.5)) 
            pygame.draw.circle(surf, (0, 0, 0, alpha), center, r)
            
        return surf

    def render(self, screen, viewer_screen_pos, radius_tiles):
        """
        Draws the darkness overlay with a dynamic hole size.
        """
        # 1. Calculate Pixel Radius
        target_radius_px = int(radius_tiles * TILE_SIZE)
        
        # 2. Check if we need to generate a new mask (if radius changed)
        if self.light_mask is None or self.current_radius_px != target_radius_px:
            self.current_radius_px = target_radius_px
            self.light_mask = self._create_light_gradient(target_radius_px)

        # 3. Fill the screen with Darkness
        self.fog_surf.fill((0, 0, 0, 250)) 
        
        # 4. Subtract the Flashlight Mask
        if self.light_mask:
            light_rect = self.light_mask.get_rect(center=viewer_screen_pos)
            self.fog_surf.blit(self.light_mask, light_rect, special_flags=pygame.BLEND_RGBA_SUB)
        
        # 5. Draw to screen
        screen.blit(self.fog_surf, (0, 0))