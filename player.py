from snake import Window, Snake

import random
import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

required_score = 100
initial_games = 1000
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
            action = random.randrange(0, 3)
            observation, reward, done, _ = s.step(action)

            if len(previous_observation) > 0:
                game_memory.append([previous_observation, action])

            previous_observation = observation
            score += reward
            if done:
                break

        if score > required_score:
            accepted_scores.append(score)
            for data in game_memory:
                output = [0] * 4
                action = data[1]
                output[action] = 1
                training_data.append([data[0], output])
    print(accepted_scores)

    return training_data


def train_generation(trained_model, generation_games):
    training_data = []
    accepted_scores = []
    for game in range(generation_games):
        score = 0
        observation = []
        game_memory = []
        prev_distance = 20
        print(f'Game {game} of {generation_games}')

        for step in range(goal_steps):
            if not observation:
                action = random.randrange(1, 2)
            else:
                action = np.argmax(trained_model.predict(np.array(observation).reshape(-1, len(observation))))
            observation, reward, done, distance = s.step(action)

            if distance < prev_distance:
                game_memory.append([observation, action])

            prev_distance = distance

            score += reward
            if done:
                break

        if score > required_score:
            accepted_scores.append(score)
            for data in game_memory:
                output = [0] * 4
                action = data[1]
                output[action] = 1
                training_data.append([data[0], output])
    print(accepted_scores)

    train_model(training_data)
    return trained_model


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

    model.fit(x, y, epochs=20)
    return model


def play_game(trained_model):
    observation = []
    generation = 1
    score = 0
    reward = 0
    done = False
    while True:
        if generation > 50:
            if not observation:
                action = random.randrange(0, 3)
            else:
                action = np.argmax(trained_model.predict(np.array(observation).reshape(-1, len(observation))))

            observation, reward, done = s.step(action)
        else:
            trained_model = train_generation(trained_model, 10)
            generation += 1
            print(f'Generation {generation} running...')

        score += reward
        if done:
            print(score)
            score = 0
            s.reset()


def main():
    s.speed = 0
    s.title('Training, please wait...')
    data = prepare_model_data()
    trained_model = train_model(data)
    s.speed = 4
    s.title('The snake!')
    play_game(trained_model)


if __name__ == '__main__':
    main()
