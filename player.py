from DQNAgent import DQNAgent
from snake import Snake
from window import Window

window = Window(12, 50, 50)  # Arguments define the tile size in the window, its width and height
snake = Snake(window)

# If skip_training value is true, a pre-made file with matching number of games will be automatically loaded,
# if present. Otherwise the default file with 5000 games will be loaded.
# You can see available values in the 'weights' folder.

skip_training = True
games_number = 1000
filename = f'weights/weights_{games_number}'


# If the snake gets to run in a loop, just click anywhere in the game window with a mouse.


def main():
    a = DQNAgent(window, snake, filename, skip_training=skip_training)

    a.train(games_number)
    a.play()


if __name__ == '__main__':
    main()
