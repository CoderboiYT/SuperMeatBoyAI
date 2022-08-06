import numpy as np
import random
import pygame
import time
import collections

from support import import_folder
from settings import MUTATION_BAD_TO_KEEP, MUTATION_CUT_OFF, MUTATION_MODIFY_CHANCE_LIMIT, generation_size, max_alive_time, N_INPUT, N_HIDDEN, N_OUTPUT, screen_width, screen_height, train, get_nn_inputs, scale_factor, jump_speed
from nnet import NNet


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.is_alive = True
        Player.start_pos = pos

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 0.6
        self.jump_speed = jump_speed
        self.air_speed = 0.2
        self.wall_jump_left = False
        self.wall_jump_right = False
        self.block_wall_jump = 0
        self.current_x = 0

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.completed = False

        # neural net
        self.nnet = NNet(N_INPUT, N_HIDDEN, N_OUTPUT)
        self.fitness = 0
        self.start_time = time.time()

    def reset(self):
        self.frame_index = 0
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft=Player.start_pos)
        self.is_alive = True

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 8
        self.gravity = 0.6
        self.jump_speed = jump_speed
        self.air_speed = 0.2
        self.wall_jump_left = False
        self.wall_jump_right = False
        self.block_wall_jump = 0
        self.current_x = 0

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.completed = False

        # neural net
        self.fitness = 0
        self.start_time = time.time()

    def import_character_assets(self):
        character_path = './graphics/character/'
        self.animations = {'idle': [], 'run': [],
                           'jump': [], 'fall': [], 'wall': []}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path, scale_factor)

    def animate(self):
        animation = self.animations[self.status]

        # loop over frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image

        # self.image = pygame.Surface((20, 20))
        # self.image.fill('red')

        # set the rect
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright=self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        elif self.on_ceiling and self.on_right:
            self.rect = self.image.get_rect(topright=self.rect.topright)
        elif self.on_ceiling and self.on_left:
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
        elif self.on_ceiling:
            self.rect = self.image.get_rect(midtop=self.rect.midtop)

    def click_right(self):
        if self.on_ground:
            self.direction.x = 1
        else:
            self.direction.x = min(
                1, self.direction.x + self.air_speed)
        self.facing_right = True

    def click_left(self):
        if self.on_ground:
            self.direction.x = -1
        else:
            self.direction.x = max(
                -1, self.direction.x - self.air_speed)
        self.facing_right = False

    def click_jump(self):
        self.jump()

    def get_input(self):
        keys = pygame.key.get_pressed()

        self.wall_jump_right = False
        self.wall_jump_left = False

        if self.block_wall_jump > 0:
            self.block_wall_jump -= 1

        if keys[pygame.K_RIGHT]:
            self.click_right()
        elif keys[pygame.K_LEFT]:
            self.click_left()
        else:
            if self.on_ground:
                self.direction.x = 0

        if keys[pygame.K_SPACE] and (self.on_ground or self.on_left or self.on_right):
            self.click_jump()

    def get_nn_input(self, frame):
        inputs = self.nnet.get_final_value(
            [self.rect.x / screen_width, self.rect.y / screen_height, frame])

        self.wall_jump_right = False
        self.wall_jump_left = False

        if self.block_wall_jump > 0:
            self.block_wall_jump -= 1

        if inputs[0] > 0.55:
            self.click_right()
        elif inputs[0] < 0.45:
            self.click_left()
        else:
            if self.on_ground:
                self.direction.x = 0

        if inputs[1] > 0.5 and (self.on_ground or self.on_left or self.on_right):
            self.click_jump()

        self.assign_fitness(self.fitness - self.fitness * 0.0001)

    def assign_fitness(self, points):
        self.fitness = points

    def get_status(self):
        if not self.on_ground and (self.on_left or self.on_right):
            self.status = "wall"
        elif self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def apply_gravity(self):
        if self.on_left or self.on_right:
            self.direction.y += self.gravity
        else:
            self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

        if not self.on_ground:
            if self.on_left and self.block_wall_jump == 0:
                self.wall_jump_right = True
                self.direction.x = 1.25
            elif self.on_right and self.block_wall_jump == 0:
                self.wall_jump_left = True
                self.direction.x = -1.25
        else:
            self.block_wall_jump = 10

    def update(self, frame):
        # self.get_input()
        if get_nn_inputs:
            if self.is_alive:
                self.get_nn_input(frame)
        else:
            self.get_input()
        self.get_status()
        self.animate()

    def create_offspring(p1, p2):
        new_player = pygame.sprite.GroupSingle()
        new_player_sprite = Player(Player.start_pos)
        new_player_sprite.nnet.create_mixed_weights(
            p1.sprite.nnet, p2.sprite.nnet)
        new_player.add(new_player_sprite)
        return new_player


class PlayerCollection:
    def __init__(self, pos, surface):
        self.surface = surface
        self.pos = pos
        self.frame = 0
        self.create_new_generation()

    def create_new_generation(self):
        self.players = []
        for _ in range(generation_size):
            curr_player = pygame.sprite.GroupSingle()
            player_sprite = Player(self.pos)
            curr_player.add(player_sprite)
            self.players.append(curr_player)
        self.create_time = time.time()

    def update(self):
        num_alive = 0
        for player in self.players:
            if player.sprite.is_alive:
                player.sprite.update(self.frame)
            if player.sprite.is_alive and self.create_time + max_alive_time > time.time():
                num_alive += 1

        self.frame += 1
        return num_alive

    def bfs(self, grid, start):
        queue = collections.deque([[start]])
        seen = set([start])
        while queue:
            path = queue.popleft()
            x, y = path[-1]
            if grid[y][x] == "T":
                return len(path)
            for x2, y2 in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                if 0 <= x2 < screen_width//10 and 0 <= y2 < screen_height//10 and grid[y2][x2] != "D" and grid[y2][x2] != "X" and (x2, y2) not in seen:
                    queue.append(path + [(x2, y2)])
                    seen.add((x2, y2))

    def evolve_population(self, level_map):

        total_fitness = 0
        for player in self.players:
            if player.sprite.is_alive:
                dist = self.bfs(
                    level_map, (int(player.sprite.rect.x/10), int(player.sprite.rect.y/10)))
                player.sprite.fitness = max(player.sprite.fitness, 1/dist)
            total_fitness += player.sprite.fitness

        self.players.sort(key=lambda x: x.sprite.fitness, reverse=True)

        if train:
            self.players[0].sprite.nnet.save_weights()

        print("Avg. fitness:", total_fitness/generation_size)

        cut_off = int(len(self.players) * MUTATION_CUT_OFF)
        good_players = self.players[0:cut_off]
        bad_players = self.players[cut_off:]
        num_bad_to_take = int(len(self.players) * MUTATION_BAD_TO_KEEP)

        for player in bad_players:
            player.sprite.nnet.modify_weights()

        new_players = []

        idx_bad_to_take = np.random.choice(
            np.arange(len(bad_players)), num_bad_to_take, replace=False)

        for index in idx_bad_to_take:
            new_players.append(bad_players[index])

        new_players.extend(good_players)

        while len(new_players) < len(self.players):
            idx_to_breed = np.random.choice(
                np.arange(len(good_players)), 2, replace=False)
            if idx_to_breed[0] != idx_to_breed[1]:
                new_player = Player.create_offspring(
                    good_players[idx_to_breed[0]], good_players[idx_to_breed[1]])
                if random.random() < MUTATION_MODIFY_CHANCE_LIMIT:
                    new_player.sprite.nnet.modify_weights()
                new_players.append(new_player)

        for player in new_players:
            player.sprite.reset()

        self.players = new_players

        self.create_time = time.time()
        self.frame = 0
