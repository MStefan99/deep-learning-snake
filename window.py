import collections
import random

import pygame


class Window:
    def __init__(self, tile_size, width, height, speed=20, mode='Visual'):
        self._tiles_horizontal = width
        self._tiles_vertical = height
        self._win_width = width * tile_size
        self._win_height = height * tile_size
        self._tile_height = self._win_height / self._tiles_vertical
        self._tile_width = self._win_width / self._tiles_horizontal
        self._tiles_diagonal = ((width - 0) ** 2 + (height - 1) ** 2) ** (1 / 2)

        self._speed = speed
        self._mode = mode
        self._food = self.random_tile()
        self._win = pygame.display.set_mode((self._win_width, self._win_height))

    def set_mode(self, mode):
        if mode == 'Visual':
            self._mode = 'Visual'
        elif mode == 'Train':
            self._mode = 'Train'

    def generate_food(self):
        self._food = self.random_tile()

    def random_tile(self):
        i = random.randrange(self._tiles_horizontal)
        j = random.randrange(self._tiles_vertical)
        return i, j

    def generate_food_for_snake(self, snake):
        field = collections.deque()
        for i in range(0, self._tiles_horizontal):
            for j in range(0, self._tiles_vertical):
                if (i, j) not in snake:
                    field.append((i, j))
        self._food = random.choice(field)

    def update(self):
        if self._mode == 'Visual':
            pygame.display.update()

    def clear(self):
        if self._mode == 'Visual':
            self._win.fill((0, 0, 0))

    def delay(self):
        if self._mode == 'Visual' and self._speed != 0:
            pygame.time.delay(1000 // self._speed)

    @staticmethod
    def is_left_tile(tile):
        return tile[0] == 0

    def is_right_tile(self, tile):
        return tile[1] == self._tiles_horizontal - 1

    def tile_to_window_coords(self, tile):
        return tile[0] * self._tile_width, tile[1] * self._tile_height

    def direction_to_food(self, tile):
        data = [0] * 2

        if self._food[0] < tile[0]:
            data[1] = -1
        elif self._food[0] > tile[0]:
            data[1] = 1
        if self._food[1] < tile[1]:
            data[0] = -1
        elif self._food[1] > tile[1]:
            data[0] = 1

        return data

    def get_dimensions(self):
        return self._tiles_horizontal, self._tiles_vertical

    def get_food(self):
        return self._food

    def set_speed(self, speed):
        if 0 <= speed <= 1000:
            self._speed = speed

    def draw_food(self, color):
        if self._mode == 'Visual':
            x, y = self.tile_to_window_coords(self._food)
            pygame.draw.rect(self._win, color,
                             (x, y, self._win_width / self._tiles_horizontal,
                              self._win_height / self._tiles_vertical))

    def draw_snake(self, snake, color):
        if self._mode == 'Visual':
            for tile in snake:
                x, y = self.tile_to_window_coords(tile)
                pygame.draw.rect(self._win, color,
                                 (x, y, self._win_width / self._tiles_horizontal,
                                  self._win_height / self._tiles_vertical))

    def distance_to_wall(self, tile):
        data = [tile[1] / self._tiles_vertical,
                1 - tile[0] / self._tiles_horizontal,
                1 - tile[1] / self._tiles_vertical,
                tile[0] / self._tiles_horizontal]

        return data
