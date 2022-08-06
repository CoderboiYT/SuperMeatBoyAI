from math import dist
import pygame
import time

from tiles import Tile, Ckpt
from settings import level_bg, tile_size_x, tile_size_y, screen_width, screen_height, render_blocks
from player import PlayerCollection


class Level:
    def __init__(self, level_data, surface):

        # level setup
        self.display_surface = surface
        self.setup_level(level_data)
        self.world_shift = 0
        self.current_x = 0

        self.num_iterations = 0
        self.map = level_data

    def setup_level(self, layout):
        self.tiles = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()
        self.ckpts = pygame.sprite.GroupSingle()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size_x
                y = row_index * tile_size_y

                if cell == 'X':
                    tile = Tile((x, y), tile_size_x, tile_size_y)
                    self.tiles.add(tile)
                if cell == 'T':
                    ckpt = Ckpt((x, y), 20, 20, 'green')
                    self.ckpts.add(ckpt)
                if cell == 'P':
                    self.player_collection = PlayerCollection(
                        (x, y), self.display_surface)
                if cell == 'D':
                    hazard = Tile((x, y), 20, 20, 'blue')
                    self.hazards.add(hazard)

    def horizontal_movement_collision(self, player):
        player = player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    player.current_x = player.rect.left
                    player.direction.x = 0
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    player.current_x = player.rect.right
                    player.direction.x = 0

        if player.on_left and (player.rect.left < player.current_x or player.rect.left > player.current_x):
            player.on_left = False
        if player.on_right and (player.rect.right > player.current_x or player.rect.right < player.current_x):
            player.on_right = False

    def vertical_movement_collision(self, player):
        player = player.sprite
        player.apply_gravity()

        for sprite in self.tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def check_ckpt_dist(self, player):
        player = player.sprite

        for ckpt in self.ckpts.sprites():
            if ckpt.rect.colliderect(player.rect):
                player.is_alive = False
                player.assign_fitness(ckpt.points)
                print("WON")
            else:
                # ckpt_dist = dist(ckpt.rect.center, player.rect.center)
                # player.assign_fitness(max(player.fitness, 1/ckpt_dist))
                pass

    def is_dead(self, player):
        player = player.sprite
        if player.rect.x <= 0 or player.rect.x >= screen_width or player.rect.y <= 0 or player.rect.y >= screen_height:
            player.is_alive = False
            player.assign_fitness(0)
        for hazard in self.hazards.sprites():
            if hazard.rect.colliderect(player.rect):
                player.is_alive = False
                player.assign_fitness(0)

    def run(self):
        # background
        self.display_surface.blit(level_bg, (0, 0))

        # level tiles
        if render_blocks:
            self.tiles.draw(self.display_surface)

            self.hazards.draw(self.display_surface)

            self.ckpts.draw(self.display_surface)

        # player
        num_alive = self.player_collection.update()
        for player in self.player_collection.players:
            if player.sprite.is_alive:
                self.horizontal_movement_collision(player)
                self.vertical_movement_collision(player)
                self.check_ckpt_dist(player)
                self.is_dead(player)
            player.draw(self.display_surface)
        if num_alive == 0:
            self.player_collection.evolve_population(self.map)
            self.num_iterations += 1
