import pygame
import time
import sys
from settings import *
from level import Level

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_map, screen)

start = time.time()
frame = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    level.run()

    if save_img:
        pygame.image.save(screen, f"./output/level_{lvl}/{frame}.jpg")

    frame += 1

    pygame.display.update()
    clock.tick(60)

print(time.time() - start)
