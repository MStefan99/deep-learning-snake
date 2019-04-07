import collections
import random

import pygame

win_width = 500
win_height = 500


class Window:
    def __init__(self, tiles_horizontal, tiles_vertical):
        self.tiles_horizontal = tiles_horizontal
        self.tiles_vertical = tiles_vertical
        self.tile_height = win_height / self.tiles_vertical
        self.tile_width = win_width / self.tiles_horizontal


class Snake:

    def __init__(self, window):
        self.window = window
        pygame.init()

        self.win = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("The Snake!")

        self.snake = collections.deque([3, 2, 1, 0])

        self.snake_length = 4
        self.direction = 1
        self.speed = 2
        self.food = None

    def reset(self):
        self.snake = collections.deque([3, 2, 1, 0])

        self.snake_length = 4
        self.direction = 1
        self.speed = 2
        self.food = None

    def run(self):

        run = True
        while run:
            pygame.time.delay(200 // self.speed)
            self.win.fill((0, 0, 0))

            if not self.food:
                self.food = self.random_tile()

            x, y = self.num_to_window_coords(self.food)
            pygame.draw.rect(self.win, (255, 0, 0),
                             (x, y, win_width / self.window.tiles_horizontal, win_height / self.window.tiles_vertical))

            for tile in self.snake:
                x, y = self.num_to_window_coords(tile)
                pygame.draw.rect(self.win, (0, 255, 0), (
                    x, y, win_width / self.window.tiles_horizontal, win_height / self.window.tiles_vertical))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] and self.direction != 1:
                    self.direction = 3
                if keys[pygame.K_RIGHT] and self.direction != 3:
                    self.direction = 1
                if keys[pygame.K_UP] and self.direction != 2:
                    self.direction = 0
                if keys[pygame.K_DOWN] and self.direction != 0:
                    self.direction = 2

            self.snake.appendleft(self.get_next())
            if len(self.snake) > self.snake_length:
                self.snake.pop()

            if self.snake[0] == self.food:
                self.food = None
                self.snake_length += 1

            if self.head() in self.body() or self.hit_wall():
                self.reset()

        pygame.quit()

    def num_to_window_coords(self, num):
        return num % self.window.tiles_vertical * self.window.tile_width, num // \
               self.window.tiles_horizontal * self.window.tile_height

    def num_to_tile_coords(self, num):
        return num % self.window.tiles_vertical * self.window.tile_width // self.window.tile_width, num // \
               self.window.tiles_horizontal * self.window.tile_height // self.window.tile_height

    def get_next(self):
        if self.direction == 0:
            return self.head() - self.window.tiles_vertical
        elif self.direction == 2:
            return self.head() + self.window.tiles_vertical
        elif self.direction == 1:
            return self.head() + 1
        else:
            return self.head() - 1

    def random_tile(self):
        field = collections.deque()
        for i in range(0, self.window.tiles_horizontal * self.window.tiles_vertical):
            if i not in self.snake:
                field.append(i)
        rand_tile = random.randrange(0, len(field))
        return field.index(rand_tile)

    def hit_wall(self):
        x0, y0 = self.num_to_tile_coords(self.head())
        hit_up = x0 < 0 or y0 < 0
        hit_down = x0 > self.window.tiles_vertical or y0 > self.window.tiles_horizontal
        hit_right = self.snake[0] % self.window.tiles_horizontal == 0 \
            and self.snake[1] % self.window.tiles_horizontal == self.window.tiles_horizontal - 1
        hit_left = self.snake[0] % self.window.tiles_horizontal == self.window.tiles_horizontal - 1 \
            and self.snake[1] % self.window.tiles_horizontal == 0

        return hit_up or hit_down or hit_right or hit_left

    def head(self):
        return self.snake[0]

    def body(self):
        snake_body = self.snake.copy()
        snake_body.popleft()
        return snake_body


w = Window(50, 50)
s = Snake(w)
s.run()
