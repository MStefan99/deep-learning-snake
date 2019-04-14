import random

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from snake import Window, Snake

initial_games = 50000
goal_steps = 1000
w = Window(50, 50, 12)
s = Snake(w)


def run_game(model):
    score = 0
    action = 1
    observation, reward, done = s.step(action)

    while True:
        action = np.argmax(model.predict(np.array(observation).reshape(-1, len(observation))))
        observation, reward, done = s.step(action)

        w.update()
        w.delay()
        w.clear()

        score += reward
        if done:
            s.reset()
            w.generate_food()
            print(f'Game finished. Score: {score}')
            score = 0


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(64, input_dim=in_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(out_size, activation='softmax'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def play_random_games():
    for _ in range(1000):
        s.step(random.randrange(0, 3))


def train_model(training_data):
    x = np.array(([data[0] for data in training_data]))
    y = np.array(([data[1] for data in training_data]))

    model = create_model(len(x[0]), len(y[0]))

    model.fit(x, y, epochs=2)
    return model


def prepare_model_data():
    training_data = []
    for game in range(initial_games):
        score = 0
        log_process('Running games...', game, initial_games, 100)

        for step in range(goal_steps):
            action = random.randrange(0, 4)
            observation, reward, done = s.step(action)

            if reward > 0:
                output = [0] * 4
                output[int(action)] = 1
                training_data.append([observation, output])

            score += reward
            if done:
                s.reset()
                w.generate_food()
                break

    print()
    return training_data


def log_process(text, done, total, size, accuracy=2, start='\r', end=''):
    completed = round(done / total * size)
    print(f'{start}{text}  [{done}/{total}] ▌■' +
          '▬' * completed + '►' + ' ' * (size - completed) +
          '▐' + f'  {round(100 * done / total, accuracy)}% ', end=end)


def main():
    # w.mode = 'Game'
    # w.speed = 4
    # s.step(1)

    w.mode = 'Background'
    data = prepare_model_data()
    model = train_model(data)

    w.mode = 'Visual'
    run_game(model)


if __name__ == '__main__':
    main()
