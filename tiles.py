import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size_x, size_y, color='grey'):
        super().__init__()

        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, x_shift):
        self.rect.x += x_shift


class Ckpt(pygame.sprite.Sprite):
    def __init__(self, pos, size_x, size_y, color, points=10):
        super().__init__()

        self.image = pygame.Surface((size_x, size_y))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.points = points
