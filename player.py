from snake import Window, Snake

import random
import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

required_score = -1000
initial_games = 2000
goal_steps = 500
w = Window(500, 500, 50, 50)
s = Snake(w)


def prepare_model_data():
    training_data = []
    accepted_scores = []
    for game in range(initial_games):
        score = 0
        game_memory = []
        previous_observation = []
        print(f'Game {game} of {initial_games}')

        for step in range(goal_steps):
            action = random.randrange(0, 4)
            observation, reward, done = s.step(action)
            # w.update()
            # w.clear()

            if len(previous_observation) > 0:
                game_memory.append([previous_observation, action])

            previous_observation = observation
            score += reward
            if done:
                s.reset()
                break

        if score > required_score:
            accepted_scores.append(score)
            for data in game_memory:
                output = [0] * 4
                action = data[1]
                output[action] = 1
                training_data.append([data[0], output])
        print(score)
    print(accepted_scores)

    return training_data


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(64, input_dim=in_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(out_size, activation='softmax'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def play_random_games():
    for _ in range(1000):
        s.step(random.randrange(0, 4))


def train_model(training_data):
    x = np.array(([data[0] for data in training_data]))
    y = np.array(([data[1] for data in training_data]))

    model = create_model(len(x[0]), len(y[0]))

    model.fit(x, y, epochs=50)
    return model


def play_game(trained_model):
    observation = []
    score = 0
    while True:
        if not observation:
            action = random.randrange(0, 3)
        else:
            action = np.argmax(trained_model.predict(np.array(observation).reshape(-1, len(observation))))

        observation, reward, done = s.step(action)

        score += reward
        if done:
            print(score)
            score = 0
            s.reset()


def main():
    w.mode = 'Background'
    data = prepare_model_data()
    trained_model = train_model(data)
    w.mode = 'Visual'
    play_game(trained_model)


if __name__ == '__main__':
    main()
