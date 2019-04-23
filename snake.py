import collections

import pygame

green = (0, 255, 0)
red = (255, 0, 0)


class Snake:
    def __init__(self, window):
        self._window = window
        pygame.init()
        pygame.display.set_caption("The Snake!")

        self._snake_length = 5
        self._direction = 1
        self._prev_direction = 1
        self._color = (0, 255, 0)

        x, y = [coord // 2 for coord in self._window.get_dimensions()]
        self._snake = collections.deque([(x - i, y) for i in range(self._snake_length)])

    def reset(self):
        self._snake_length = 5
        self._direction = 1
        self._prev_direction = 1

        x, y = [coord // 2 for coord in self._window.get_dimensions()]
        self._snake = collections.deque([(x - i, y) for i in range(self._snake_length)])

        return self._observe()

    def get_snake(self):
        return self._snake

    def step(self, action):
        eaten = False

        self._window.draw_snake(self._snake, green)
        self._window.draw_food(red)

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

        if self._head() == self._window.get_food():
            eaten = True
            self._snake_length += 1
            self._window.generate_food_for_snake(self.get_snake())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                self.reset()
                self._window.generate_food_for_snake(self.get_snake())

        observation = self._observe()
        self._prev_direction = self._direction

        info = {'Eaten': eaten}

        return observation, reward, self._lose(), info

    def _get_reward(self):
        food = self._window.get_food()

        if self._lose():
            return -10
        elif self._head() == food:
            return 0.7
        elif distance_between_tiles(self._snake[0], food) < \
                distance_between_tiles(self._snake[1], food):
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
        x, y = self._head()
        win_x, win_y = self._window.get_dimensions()

        hit_x = x < 0 or x > win_x - 1
        hit_y = y < 0 or y > win_y - 1

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
        observations.extend(self.dist_to_body())

        return observations

    def _obstacle_next(self):
        head = self._head()
        body = self._body()

        data = [0] * 8
        if (head[0], head[1] - 1) in body:
            data[0] = 1
        if (head[0] + 1, head[1]) in body:
            data[1] = 1
        if (head[0], head[1] + 1) in body:
            data[2] = 1
        if (head[0] - 1, head[1]) in body:
            data[3] = 1
        if (head[0] + 1, head[1] - 1) in body:
            data[0] = 1
        if (head[0] + 1, head[1] + 1) in body:
            data[1] = 1
        if (head[0] - 1, head[1] + 1) in body:
            data[2] = 1
        if (head[0] - 1, head[1] - 1) in body:
            data[3] = 1
        return data

    def dist_to_body(self):
        head = self._head()
        body = self._body()

        data = self._window.distance_to_wall(head)

        for body_tile in reversed(body):
            if body_tile[0] == head[0] and body_tile[1] < head[1]:
                data[0] = head[1] - body_tile[1] - 2
            elif body_tile[1] == head[1] and body_tile[0] > head[0]:
                data[1] = body_tile[0] - head[0] - 2
            elif body_tile[0] == head[0] and body_tile[1] > head[1]:
                data[2] = body_tile[1] - head[1] - 2
            elif body_tile[1] == head[1] and body_tile[0] < head[0]:
                data[3] = head[0] - body_tile[0] - 2

        return data


def distance_between_tiles(tile1, tile2):
    return ((tile1[0] - tile2[0]) ** 2 + (tile1[1] - tile2[1]) ** 2) ** (1 / 2)
