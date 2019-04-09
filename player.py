from snake import Window, Snake

import random
import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

required_score = 1000
initial_games = 1000
goal_steps = 500
w = Window(500, 500, 50, 50)
s = Snake(w)


def prepare_model_data(number):
    training_data = []
    accepted_scores = []
    for game in range(number):
        score = 0
        game_memory = []
        observation = []
        print(f'Game {game} of {initial_games}')

        for step in range(goal_steps):
            action = get_action(observation)
            observation, reward, done, _ = s.step(action)

            if len(observation) > 0:
                game_memory.append([observation, action])

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


def get_action(observations):
    if not observations:
        return random.randrange(0, 4)
    elif observations[16] != 0:
        return 0
    elif observations[17] != 0:
        return 1
    elif observations[18] != 0:
        return 2
    elif observations[19] != 0:
        return 3
    else:
        return random.randrange(0, 4)


def train_generation(trained_model, generation_games):
    training_data = []
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

        for data in game_memory:
            output = [0] * 4
            action = data[1]
            output[action] = 1
            training_data.append([data[0], output])
    print(training_data)

    train_model(training_data)
    return trained_model


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(128, input_dim=in_size, activation='relu'))
    model.add(Dense(32, activation='relu'))
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
    while True:
        data = prepare_model_data(initial_games)
        if data:
            break
    trained_model = train_model(data)
    s.speed = 8
    s.title('The snake!')
    play_game(trained_model)


if __name__ == '__main__':
    main()
