import pygame
import math
from pyaddition import *

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()  # Limit to 60 frames per second
fps = 60


def is_even(numb: int):
    return numb % 2 == 0


class Hex:
    size = 40
    vertical_spacing = math.sqrt(3) * size
    horizontal_spacing = 1.5 * size
    all_hexs = []

    def step_to_all_hex():
        for width in range(len(Hex.all_hexs)):
            for hex in Hex.all_hexs[width]:
                hex: Hex
                hex.step()

    def get_xy(w: int, h: int):
        x = w * Hex.horizontal_spacing
        if is_even(w):
            y = h * Hex.vertical_spacing
        else:
            y = (h * Hex.vertical_spacing) + (Hex.vertical_spacing / 2)
        return x, y

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.x, self.y = Hex.get_xy(self.w, self.h)

        self.size = Hex.size
        self.color = (255, 255, 255)

    def draw(self):
        points = []

        for i in range(6):
            angle = i * 60
            rad = angle * (math.pi / 180)
            point_x = self.x + self.size * math.cos(rad)
            point_y = self.y + self.size * math.sin(rad)

            points.append((point_x, point_y))
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (0, 0, 0), points, 5)

    def step(self):
        self.draw()


Hex.all_hexs = []


def create_hexs_map(width: int, height: int):
    map_width = width
    map_height = height

    for w in range(map_width):
        Hex.all_hexs.append([])
        for h in range(map_height):
            Hex.all_hexs[w].append(Hex(w, h))


create_hexs_map(30, 10)


running = True
while running:

    Hex.step_to_all_hex()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    screen.fill((0, 0, 0))
    clock.tick(fps)

pygame.quit()
