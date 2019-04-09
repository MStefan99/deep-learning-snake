from snake import Window, Snake

import random
import numpy as np
import tensorflow as tf

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


def play_random_games():
    for _ in range(1000):
        observation, reward, done, info = s.step(random.randrange(0, 3))


if __name__ == '__main__':
    w = Window(500, 500, 10, 10)
    s = Snake(w)

    s.speed = 250
    _, scores = prepare_model_data()
    print(scores)

