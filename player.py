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
w = Window(15, 30, 30)
s = Snake(w)


class DQNAgent:
    def __init__(self, action_size):
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self.build_model(12, 4)

    def train(self, model):
        batch_size = 32

        while True:
            memory = []
            prev_state = []
            training_data = []
            done = False
            state = s.reset()
            w.generate_food()
            self.epsilon *= self.epsilon_decay

            while not done:
                score = 0

                if random.uniform(0, 1) < self.epsilon:
                    action = random.randrange(0, 4)
                else:
                    action = np.argmax(model.predict(np.array(state).reshape([-1, 12])))

                observation, reward, done = s.step(action)

                state = np.reshape(state, [1, 12])
                training_data.append([prev_state, action, reward, state, done])
                prev_state = state

                w.update()
                w.delay()
                w.clear()

                score += reward
                if len(memory) > batch_size:
                    self.replay(training_data)

    def replay(self, training_data):
        for prev_state, action, reward, state, done in training_data:
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
        model.compile(loss='mse', optimizer=Adam(lr=0.8))
        print(model.summary())

        return model

    def train_model(self, training_data, weights=None):
        x = np.array(([data[0] for data in training_data]))
        y = np.array(([data[1] for data in training_data]))

        model = self.build_model(len(x[0]), len(y[0]))

        if weights:
            model.load_weights(weights)
        model.fit(x, y, epochs=5)

        return model


def play_game(trained_model):
    observation = []
    score = 0
    while True:
        if not observation:
            action = 1
        else:
            action = np.argmax(trained_model.predict(np.array(observation).reshape(-1, len(observation))))
        observation, reward, done = s.step(action)

        w.update()
        w.delay()
        w.clear()

        score += reward
        if done:
            print(score)
            score = 0
            s.reset()
            w.generate_food()


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
    a = DQNAgent(4)
    model = a.build_model(12, 4)
    a.train(model)

    # prepare_model_data(create_model(12, 4))
    # trained_model = train_model(data)
    # w.mode = 'Visual'
    # play_game(trained_model)


if __name__ == '__main__':
    main()
