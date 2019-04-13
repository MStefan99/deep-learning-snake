import random

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from snake import Window, Snake

initial_games = 500
goal_steps = 500
w = Window(500, 500, 25, 25)
s = Snake(w)


def prepare_model_data():
    training_data = []
    for game in range(initial_games):
        score = 0
        game_memory = []
        log_process('Running games...', game / initial_games, 100)

        for step in range(goal_steps):
            action = random.randrange(0, 4)
            observation, reward, done = s.step(action)

            if reward > 0:
                game_memory.append([observation, action])

            score += reward
            if done:
                s.reset()
                break

        for data in game_memory:
            output = [0] * 4
            action = data[1]
            output[action] = 1
            training_data.append([data[0], output])

    print()
    print(f'Recorded {len(training_data)} moves')
    return training_data


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(256, input_dim=in_size, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(256, activation='relu', kernel_initializer='random_normal'))
    model.add(Dense(out_size, activation='softmax', kernel_initializer='random_normal'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def play_random_games():
    for _ in range(1000):
        s.step(random.randrange(0, 4))


def train_model(training_data):
    x = np.array(([data[0] for data in training_data]))
    y = np.array(([data[1] for data in training_data]))

    model = create_model(len(x[0]), len(y[0]))

    model.fit(x, y, epochs=10)
    return model


def play_game(trained_model):
    score = 0
    action = random.randrange(0, 4)
    observation, reward, done = s.step(action)

    while True:
        action = np.argmax(trained_model.predict(np.array(observation).reshape(-1, len(observation))))
        observation, reward, done = s.step(action)

        w.update()
        w.delay()
        w.clear()

        score += reward
        if done:
            print(f'Game finished. Score: {round(score, 1)}')
            score = 0
            s.reset()


def log_process(text, process, size, start='\r', end=''):
    completed = round(process * size)
    print(f'{start}{text}  ▌■' +
          '▬' * completed + '►' + ' ' * (size - completed) +
          '▐' + f' {round(100 * process, 2)}%', end=end)


def main():
    # play_game(create_model(14, 4))
    w.mode = 'Background'
    data = prepare_model_data()
    trained_model = train_model(data)
    w.mode = 'Visual'
    play_game(trained_model)


if __name__ == '__main__':
    main()
