import pygame
import random

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Random burst velocity
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.timer = random.randint(20, 45) # How long it lasts

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.timer -= 1

    def draw(self, surface, cam_x, cam_y):
        if self.timer > 0:
            # Draw a small square
            pygame.draw.rect(surface, self.color, (self.x - cam_x, self.y - cam_y, 4, 4))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self):
        # Move particles and remove dead ones
        self.particles = [p for p in self.particles if p.timer > 0]
        for p in self.particles:
            p.update()

    def draw(self, surface, cam_x, cam_y):
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)