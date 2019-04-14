import random

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from snake import Window, Snake

initial_games = 10000
goal_steps = 500
w = Window(50, 50, 12)
s = Snake(w)


def run_game(model):
    training_data = []
    score = 0
    action = random.randrange(0, 4)
    observation, reward, done = s.step(action)

    while True:
        action = np.argmax(model.predict(np.array(observation).reshape(-1, len(observation))))
        observation, reward, done = s.step(action)

        w.update()
        w.delay()
        w.clear()

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


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(16, input_dim=in_size, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(out_size, activation='softmax'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def play_random_games():
    for _ in range(1000):
        s.step(random.randrange(0, 4))


def train_model(training_data, old_model=create_model(14, 4)):
    if len(training_data) > 0:
        x = np.array(([data[0] for data in training_data]))
        y = np.array(([data[1] for data in training_data]))

        model = create_model(len(x[0]), len(y[0]))

        model.fit(x, y, epochs=2)
        return model
    else:
        return old_model


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
                w.generate_food()
                break

        for data in game_memory:
            output = [0] * 4
            action = data[1]
            output[action] = 1
            training_data.append([data[0], output])

    print()
    return training_data


def log_process(text, process, size, accuracy=2, start='\r', end=''):
    completed = round(process * size)
    print(f'{start}{text}  ▌■' +
          '▬' * completed + '►' + ' ' * (size - completed) +
          '▐' + f'  {round(100 * process, accuracy)}%', end=end)


def main():
    w.mode = 'Background'
    data = prepare_model_data()
    model = train_model(data)

    w.mode = 'Visual'
    while True:
        data = run_game(model)
        model = train_model(data, model)


if __name__ == '__main__':
    main()
