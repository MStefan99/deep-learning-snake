import random

import numpy as np
from keras import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

from snake import Window, Snake

required_score = 0
initial_games = 25
goal_steps = 500
w = Window(500, 500, 50, 50)


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
            w.update()

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


def create_model(in_size, out_size):
    model = Sequential()
    model.add(Dense(32, input_dim=in_size, activation='relu', kernel_initializer='random_uniform'))
    model.add(Dense(16, activation='relu', kernel_initializer='random_uniform'))
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

    model.fit(x, y, epochs=25)
    return model


def play_game(population):
    generation = 0
    while True:
        print(f'Generation {generation} running...')
        while True:
            for snake in population:
                if snake['alive']:
                    observation = snake['observation']
                    if not observation:
                        action = random.randrange(0, 4)
                    else:
                        action = np.argmax(snake['model'].predict(np.array(observation).reshape(-1, len(observation))))
                    observation, reward, done = snake['snake'].step(action)

                    snake['score'] += reward
                    if done:
                        snake['alive'] = False
            w.update()
            w.clear()

            if all_dead(population):
                size = len(population)
                leave = 2
                population = sorted(population, key=lambda kv: kv['score'], reverse=True)[:len(population) // leave]
                print(f'Generation {generation} has finished playing. Generation highscore: {population[0]["score"]}.')

                print(f'Breeding generation {generation}...')
                while len(population) < size:
                    log_process('Breeding...', (len(population) / size - 1 / leave) * leave, 40)
                    population.append(breed(random.choice(population), random.choice(population)))

                print(f'\nMutating generation {generation}...')
                for _ in range(3):
                    model = random.randrange(len(population))
                    population[model] = mutate(population[model], 10)

                generation += 1
                print(f'Success! Preparing to run generation {generation}')
                population = reset_population(population)
                w.generate_food()
                break


def log_process(text, process, size, start='\r', end=''):
    print(text + f' {start}[' +
          '*' * round(process * size) + ' ' * round((1 - process) * size) +
          '] ' + f'{round(100 * process)}%', end=end)


def all_dead(population):
    dead = True
    for snake in population:
        if snake['alive']:
            dead = False

    return dead


def reset_population(population):
    for snake in population:
        snake['score'] = 0
        snake['alive'] = True
        snake['snake'].reset()

    return population


def create_population(count):
    population = []
    for _ in range(count):
        population.append({'model': create_model(24, 4), 'snake': Snake(w), 'score': 0, 'alive': True,
                           'observation': []})

    return population


def create_snake():
    return {'model': create_model(24, 4), 'snake': Snake(w), 'score': 0, 'alive': True, 'observation': []}


def breed(mother, father):
    child = create_snake()
    m_weights = mother['model'].get_weights()
    f_weights = father['model'].get_weights()
    weights = child['model'].get_weights()
    for layer in enumerate(weights):
        if layer[1].ndim > 1:
            for row in range(len(layer[1])):
                m_value = m_weights[layer[0]][row]
                f_value = f_weights[layer[0]][row]
                weights[layer[0]][row] = random_of_two(m_value, f_value)
            weights[layer[0]] = layer[1]
    child['model'].set_weights(weights)

    return child


def random_of_two(a, b):
    if random.getrandbits(1) == 1:
        return a
    else:
        return b


def mutate(network, speed):
    weights = network['model'].get_weights()
    for layer in enumerate(weights):
        if layer[1].ndim > 1:
            for _ in range(speed):
                element = random.randrange(len(layer[1][layer[0]]))
                layer[1][layer[0]][element] = random.uniform(-0.02, 0.02)
            weights[layer[0]] = layer[1]
    network['model'].set_weights(weights)

    return network


def main():
    population = create_population(200)
    play_game(population)


if __name__ == '__main__':
    main()
