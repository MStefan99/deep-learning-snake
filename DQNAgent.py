import os
import random
from time import time

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from log import log_process

filename = 'weights/weights_5000'
skip_training = False
debug = False


class DQNAgent:
    def __init__(self, window, snake):
        self._gamma = 0.95
        self._epsilon_start = 1.0
        self._epsilon = self._epsilon_start
        self._epsilon_min = 0.1
        self._learning_rate = 0.0005

        self._window = window
        self._snake = snake
        self._model = self.build_model(6, 4)

    def train(self, games):
        if not skip_training:
            start = time()

            for game in range(games):
                score = 0
                steps = 0
                reward_total = 0
                done = False
                training_data = []
                observation = self._snake.reset()
                prev_observation = observation
                self._window.generate_food_for_snake(self._snake.get_snake())

                if self._epsilon > self._epsilon_min:
                    self._epsilon = self._epsilon_start * (1 - game / games)

                while not done:
                    if random.uniform(0, 1) < self._epsilon:
                        action = random.randrange(0, 4)
                    else:
                        action = np.argmax(self._model.predict(np.array(observation).reshape([-1, 6])))
                    observation, reward, done, info = self._snake.step(action)

                    training_data.append([prev_observation, action, reward, observation, done])
                    prev_observation = observation

                    if info['Eaten']:
                        score += 1
                    reward_total += reward
                    steps += 1

                if not debug:
                    log_process('Training, please wait...', game, games, 50,
                                time_start=start, time_now=time(), time_correction=2,
                                info=f'Avg reward: {round(reward_total / game, 2) if game > 0 else 0}, '
                                f'Score: {score}, Epsilon: {round(self._epsilon, 2)}.')

                self.replay(training_data)

                if game % 50 == 49:
                    self._model.save_weights(filename, overwrite=True)

                if debug:
                    print(f'Game {game} finished. Score: {round(score, 2)} in {steps} steps, ' +
                          f'eps: {round(self._epsilon, 2)}')

    def replay(self, training_data):
        for prev_state, action, reward, state, done in training_data:
            prev_state = np.reshape(prev_state, [1, 6])
            state = np.reshape(prev_state, [1, 6])

            target = reward
            if not done:
                target = (reward + self._gamma *
                          np.amax(self._model.predict(state)[0]))
            target_f = self._model.predict(prev_state)
            target_f[0][action] = target
            self._model.fit(prev_state, target_f, epochs=1, verbose=0)

    def build_model(self, in_size, out_size):
        model = Sequential()
        model.add(Dense(64, input_dim=in_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(out_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self._learning_rate))

        return model

    def play(self):
        game = 0

        if skip_training and os.path.isfile(filename):
            self._model.load_weights(filename)

        while True:
            observation = self._snake.reset()
            self._window.generate_food_for_snake(self._snake.get_snake())
            score = 0
            done = False

            while not done:
                action = np.argmax(self._model.predict(np.array(observation).reshape([-1, 6])))
                observation, reward, done, info = self._snake.step(action)

                if info['Eaten']:
                    score += 1

                self._window.update()
                self._window.delay()
                self._window.clear()

            game += 1
            print(f'Game {game} finished. Score: {round(score, 2)}')
