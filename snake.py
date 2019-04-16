import collections
import random

import pygame

green = (0, 255, 0)
red = (255, 0, 0)


class Window:
    def __init__(self, scale, tiles_horizontal, tiles_vertical):
        self.tiles_horizontal = tiles_horizontal
        self.tiles_vertical = tiles_vertical
        self.win_width = tiles_horizontal * scale
        self.win_height = tiles_vertical * scale
        self.tile_height = self.win_height / self.tiles_vertical
        self.tile_width = self.win_width / self.tiles_horizontal
        self.tiles_diagonal = ((tiles_horizontal - 0) ** 2 + (tiles_vertical - 1) ** 2) ** (1 / 2)

        self.speed = 18
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
            pygame.time.delay(1000 // self.speed)

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

    def direction_to_food(self, tile):
        data = [0] * 2

        if self.food[0] < tile[0]:
            data[1] = -1
        elif self.food[0] > tile[0]:
            data[1] = 1
        if self.food[1] < tile[1]:
            data[0] = -1
        elif self.food[1] > tile[1]:
            data[0] = 1

        return data


class Snake:
    def __init__(self, window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("The Snake!")

        x = self._window.tiles_horizontal // 2
        y = self._window.tiles_vertical // 2
        self._snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y), (x - 4, y)])

        self._snake_length = 4
        self._direction = 1
        self._prev_direction = 1
        self._color = (0, 255, 0)

    def reset(self):
        x = self._window.tiles_horizontal // 2
        y = self._window.tiles_vertical // 2
        self._snake = collections.deque([(x, y), (x - 1, y), (x - 2, y), (x - 3, y), (x - 4, y)])

        self._snake_length = 4
        self._direction = 1
        self._prev_direction = 1

        return self._observe()

    def step(self, action):
        eaten = False
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

        self._snake.appendleft(self._get_next())
        if len(self._snake) > self._snake_length:
            self._snake.pop()

        reward = self._get_reward()

        if self._head() == self._window.food:
            eaten = True
            self._snake_length += 1
            self._window.generate_food()

        if not self._window.food:
            self._window.generate_food()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                self.reset()
                self._window.generate_food()

        observation = self._observe()
        self._prev_direction = self._direction

        info = {'Eaten': eaten}

        return observation, reward, self._lose(), info

    def _get_reward(self):
        if self._lose():
            return -1.0
        elif self._head() == self._window.food:
            return 0.7
        elif distance_between_tiles(self._snake[0], self._window.food) < \
                distance_between_tiles(self._snake[1], self._window.food):
            return 0.01
        else:
            return -0.02

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
        x, y = self._head()

        hit_x = x < 0 or x > self._window.tiles_horizontal - 1
        hit_y = y < 0 or y > self._window.tiles_vertical - 1

        return hit_x or hit_y

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

        observations = self._obstacle_next()
        observations.extend(self._window.direction_to_food(tile))

        return observations

    def _obstacle_next(self):
        head = self._head()
        body = self._body()

        data = [0] * 4
        if (head[0], head[1] - 1) in body:
            data[0] = 1
        if (head[0] + 1, head[1]) in body:
            data[1] = 1
        if (head[0], head[1] + 1) in body:
            data[2] = 1
        if (head[0] - 1, head[1]) in body:
            data[3] = 1
        return data


def distance_between_tiles(tile1, tile2):
    return ((tile1[0] - tile2[0]) ** 2 + (tile1[1] - tile2[1]) ** 2) ** (1 / 2)
