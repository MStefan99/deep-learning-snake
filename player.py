import time
from collections import deque

from snake import Window, Snake

import random
import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

initial_games = 10000
required_score = 0
goal_steps = 1000
w = Window(20, 20, 20)
s = Snake(w)
train = True


class DQNAgent:
    def __init__(self):
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.0001
        self.epsilon_decay = 0.996
        self.learning_rate = 0.0005
        self.model = self.build_model(6, 4)

    def train(self, games):
        for game in range(games):
            if game > 900:
                w.speed = games + 20 - game
            else:
                w.speed = 0
            training_data = []
            observation = s.reset()
            prev_observation = observation
            w.generate_food()
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay
            score = 0
            steps = 0
            reward_total = 0
            done = False

            # self.model.load_weights('weights')

            while not done:
                if random.uniform(0, 1) < self.epsilon:
                    action = random.randrange(0, 4)
                else:
                    action = np.argmax(self.model.predict(np.array(observation).reshape([-1, 6])))
                observation, reward, done, info = s.step(action)

                training_data.append([prev_observation, action, reward, observation, done])
                prev_observation = observation

                w.update()
                w.delay()
                w.clear()

                if info['Eaten']:
                    score += 1
                reward_total += reward
                steps += 1
                # print(f'Observation: {observation}, Reward: {reward}')

            self.replay(training_data)
            if game % 50 == 0:
                self.model.save_weights('weights', overwrite=True)
            print(f'Game {game} finished. Score: {round(score, 2)} in {steps} steps, Avg reward: ' +
                  f'{round(reward_total / steps, 2)} eps: {round(self.epsilon, 2)}')

    def replay(self, training_data):
        for prev_state, action, reward, state, done in training_data:
            prev_state = np.reshape(prev_state, [1, 6])
            state = np.reshape(prev_state, [1, 6])

            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(state)[0]))
            target_f = self.model.predict(prev_state)
            target_f[0][action] = target
            self.model.fit(prev_state, target_f, epochs=1, verbose=0)

    def build_model(self, in_size, out_size):
        model = Sequential()
        model.add(Dense(64, input_dim=in_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(out_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        print(model.summary())

        return model

    def play(self):
        game = 0

        if not train:
            self.model.load_weights('weights')

        while True:
            state = s.reset()
            w.generate_food()
            score = 0
            done = False

            while not done:
                action = np.argmax(self.model.predict(np.array(state).reshape([-1, 6])))
                observation, reward, done, info = s.step(action)
                if info['Eaten']:
                    score += 1

                w.update()
                w.delay()
                w.clear()

            game += 1
            print(f'Game {game} finished. Score: {round(score, 2)}')


def log_process(text, done, total, size, accuracy=1, time_start=0.0, time_now=0.0, start='\r', end=''):
    completed = round(done / total * size)
    if time_start and time_now and done > 0:
        seconds = round((time_now - time_start) / done * (total - done))
        if seconds > 60:
            minutes = round(seconds / 60)
            seconds = seconds % 60
            eta = f'ETA: {minutes}m {seconds}s'
        else:
            eta = f'ETA: {seconds}s'
    else:
        eta = ''
    print(f'{start}{text}  [{done}/{total}] ' + eta + '  ▌■' +
          '▬' * completed + '►' + ' ' * (size - completed) +
          '▐' + f'  {round(100 * done / total, accuracy)}% ', end=end)


def main():
    a = DQNAgent()
    if train:
        # w.mode = ''
        a.train(1000)
    w.mode = 'Visual'
    a.play()


if __name__ == '__main__':
    main()
