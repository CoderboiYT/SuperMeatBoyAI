from sys import exit
import pygame
import math

tile_size = 15

pygame.init()

lvl = 8

bg = pygame.image.load(f"lvl{lvl}.jpg")
width = bg.get_width()
height = bg.get_height()
window = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

tile_size_x, tile_size_y = 10, 10

tiles = [[" " for _ in range(width//tile_size_x)]
         for _ in range(height//tile_size_y)]


def render_tiles():
    for row_idx, row in enumerate(tiles):
        for col_idx, cell in enumerate(row):
            x = col_idx * tile_size_x
            y = row_idx * tile_size_y

            if cell == 'X':
                pygame.draw.rect(window, (255, 255, 255), pygame.Rect(
                    x, y, tile_size_x, tile_size_y), 0)
            elif cell == 'P':
                pygame.draw.rect(window, (255, 0, 0), pygame.Rect(
                    x, y, tile_size_x, tile_size_y), 0)
            elif cell == 'T':
                pygame.draw.rect(window, (0, 255, 0), pygame.Rect(
                    x, y, tile_size_x, tile_size_y), 0)
            elif cell == 'D':
                pygame.draw.rect(window, (0, 0, 255), pygame.Rect(
                    x, y, tile_size_x, tile_size_y), 0)
            else:
                pygame.draw.rect(window, (0, 0, 0), pygame.Rect(
                    x, y, tile_size_x, tile_size_y), 1)


# Main Loop
while True:
    window.blit(bg, (0, 0))

    pos = pygame.mouse.get_pos()
    pressed1 = pygame.mouse.get_pressed()[0]

    render_tiles()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE]:
        pos = pygame.mouse.get_pos()
        pos_x = pos[0]//tile_size_x
        pos_y = pos[1]//tile_size_y

        tiles[pos_y][pos_x] = "X"
    if keys[pygame.K_PERIOD]:
        pos = pygame.mouse.get_pos()
        pos_x = pos[0]//tile_size_x
        pos_y = pos[1]//tile_size_y

        tiles[pos_y][pos_x] = "P"
    if keys[pygame.K_t]:
        pos = pygame.mouse.get_pos()
        pos_x = pos[0]//tile_size_x
        pos_y = pos[1]//tile_size_y

        tiles[pos_y][pos_x] = "T"
    if keys[pygame.K_d]:
        pos = pygame.mouse.get_pos()
        pos_x = pos[0]//tile_size_x
        pos_y = pos[1]//tile_size_y

        tiles[pos_y][pos_x] = "D"
    if keys[pygame.K_r]:
        pos = pygame.mouse.get_pos()
        pos_x = pos[0]//tile_size_x
        pos_y = pos[1]//tile_size_y

        tiles[pos_y][pos_x] = " "

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            for row in range(len(tiles)):
                tiles[row] = "".join(tiles[row])
            print(tiles)
            pygame.quit()
            exit()

    pygame.display.update()
    clock.tick(60)
