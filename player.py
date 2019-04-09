from snake import Window, Snake

import random
import numpy as np
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


required_score = 100
initial_games = 500
goal_steps = 500


def prepare_model_data():
    training_data = []
    accepted_scores = []
    for game in range(initial_games):
        score = 0
        game_memory = []
        previous_observation = []

        for step in range(goal_steps):
            action = random.randrange(0, 3)
            observation, reward, done = s.step(action)

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

    return training_data, accepted_scores


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(64, input_dim=in_size, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(out_size, activation='softmax'))
    model.compile(loss='mse', optimizer=Adam())

    return model


def play_random_games():
    for _ in range(1000):
        observation, reward, done, info = s.step(random.randrange(0, 3))


if __name__ == '__main__':
    w = Window(500, 500, 10, 10)
    s = Snake(w)

    s.speed = 250
    data, scores = prepare_model_data()
    m = create_model(len(data), 4)

    print(scores)

