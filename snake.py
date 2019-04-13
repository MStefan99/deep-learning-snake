import collections
import random

import pygame

green = (0, 255, 0)
red = (255, 0, 0)


class Window:
    def __init__(self, win_width, win_height, tiles_horizontal, tiles_vertical):
        self.tiles_horizontal = tiles_horizontal
        self.tiles_vertical = tiles_vertical
        self.win_width = win_width
        self.win_height = win_height
        self.tile_height = win_height / self.tiles_vertical
        self.tile_width = win_width / self.tiles_horizontal
        self.tiles_diagonal = ((tiles_horizontal - 0) ** 2 + (tiles_vertical - 1) ** 2) ** (1 / 2)

        self.speed = 4
        self.food = self.random_tile()
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        self.mode = 'Visual'

    def generate_food(self):
        self.food = self.random_tile()

    def random_tile(self):
        i = random.randrange(self.tiles_horizontal)
        j = random.randrange(self.tiles_vertical)
        return i, j

    def update(self):
        if self.mode == 'Visual':
            pygame.display.update()

    def clear(self):
        if self.mode == 'Visual':
            self.win.fill((0, 0, 0))

    def delay(self):
        if self.mode == 'Visual' and self.speed != 0:
            pygame.time.delay(200 // self.speed)

    def draw_tile(self, tile, color):
        if self.mode == 'Visual':
            x, y = self.tile_to_window_coords(tile)
            pygame.draw.rect(self.win, color,
                             (x, y, self.win_width / self.tiles_horizontal,
                              self.win_height / self.tiles_vertical))

    @staticmethod
    def is_left_tile(tile):
        return tile[0] == 0

    def is_right_tile(self, tile):
        return tile[1] == self.tiles_horizontal - 1

    def tile_to_window_coords(self, tile):
        return tile[0] * self.tile_width, tile[1] * self.tile_height

    def dist_to_wall(self, tile):
        data = [tile[1] / self.tiles_vertical,
                1 - tile[0] / self.tiles_horizontal,
                1 - tile[1] / self.tiles_vertical,
                tile[0] / self.tiles_horizontal]

        return data

    def dist_to_body(self, tile, body):
        data = self.dist_to_wall(tile)

        for body_tile in body:
            if body_tile[0] == tile[0] and body_tile[1] < tile[1]:
                data[0] = (body_tile[1] - tile[1]) / self.tiles_vertical
            elif body_tile[1] == tile[1] and body_tile[0] > tile[0]:
                data[1] = (body_tile[0] - tile[0]) / self.tiles_horizontal
            elif body_tile[0] == tile[0] and body_tile[1] > tile[1]:
                data[2] = (tile[1] - body_tile[1]) / self.tiles_vertical
            elif body_tile[1] == tile[1] and body_tile[0] < tile[0]:
                data[3] = (tile[0] - body_tile[0]) / self.tiles_horizontal

        return data

    def dist_to_food(self, tile):
        data = [0] * 4

        if self.food[0] < tile[0]:
            data[3] = self.food[0] / (tile[0] + 2)
        else:
            data[1] = (self.tiles_horizontal - self.food[0]) / (tile[0] + 2)
        if self.food[1] < tile[1]:
            data[0] = self.food[1] / (tile[1] + 2)
        else:
            data[2] = (self.tiles_vertical - self.food[1]) / (tile[1] + 2)

        return data


class Snake:
    def __init__(self, window):
        self._window = window
        pygame.init()

        pygame.display.set_caption("The Snake!")

        x = self._window.tiles_horizontal // 2
        y = self._window.tiles_vertical // 2
        self._snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y)])

        self._snake_length = 4
        self._direction = 1
        self._color = (0, 255, 0)
        self._prev_action = 1
        self._reward = 0

    def reset(self):
        x = self._window.tiles_horizontal // 2
        y = self._window.tiles_vertical // 2
        self._snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y)])

        self._snake_length = 4
        self._direction = 1
        self._prev_action = 1
        self._reward = 0

    def step(self, action):
        self._prev_action = action

        self._window.draw_tile(self._window.food, red)

        for tile in self._snake:
            self._window.draw_tile(tile, green)

        if action == 3 and self._direction != 1:
            self._direction = 3
        if action == 1 and self._direction != 3:
            self._direction = 1
        if action == 0 and self._direction != 2:
            self._direction = 0
        if action == 2 and self._direction != 0:
            self._direction = 2

        self._reward = self._get_reward()

        self._snake.appendleft(self._get_next())
        if len(self._snake) > self._snake_length:
            self._snake.pop()

        if self._head() == self._window.food:
            self._snake_length += 1

        if not self._window.food:
            self._window.generate_food()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        observation = self._observe()
        return observation, self._reward, self._lose()

    def _get_reward(self):
        if self._lose():
            return -1.0
        elif self._head() == self._window.food:
            return 0.7
        elif distance_between_tiles(self._head(), self._window.food) < \
                distance_between_tiles(self._snake[1], self._window.food):
            return 0.1
        else:
            return -0.2

    def _get_next(self):
        x, y = self._head()
        if self._direction == 0:
            return x, y - 1
        elif self._direction == 1:
            return x + 1, y
        elif self._direction == 2:
            return x, y + 1
        elif self._direction == 3:
            return x - 1, y

    def _hit_wall(self):
        x0, y0 = self._head()

        hit_up = x0 < 0 or y0 < 0
        hit_down = x0 > self._window.tiles_horizontal or y0 > self._window.tiles_vertical

        hit_right = self._window.is_left_tile(self._snake[0]) and self._window.is_right_tile(self._snake[1])
        hit_left = self._window.is_right_tile(self._snake[0]) and self._window.is_left_tile(self._snake[1])

        return hit_up or hit_down or hit_right or hit_left

    def _lose(self):
        return self._head() in self._body() or self._hit_wall()

    def _head(self):
        return self._snake[0]

    def _body(self):
        snake_body = self._snake.copy()
        snake_body.popleft()
        return snake_body

    def _tile_in_window(self, tile):
        is_inside = 0 <= tile[0] <= self._window.tiles_horizontal and 0 <= tile[1] <= self._window.tiles_vertical
        return is_inside

    def _observe(self):
        tile = self._head()
        observations = self._window.dist_to_wall(tile)
        observations.extend(self._window.dist_to_body(tile, self._body()))
        observations.extend(self._window.dist_to_food(tile))
        observations.append(self._prev_action)
        observations.append(self._get_reward())

        return observations


def distance_between_tiles(tile1, tile2):
    return ((tile1[0] - tile2[0]) ** 2 + (tile1[1] - tile2[1]) ** 2) ** (1 / 2)
