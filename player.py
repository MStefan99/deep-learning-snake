from DQNAgent import DQNAgent
from snake import Snake
from window import Window

window = Window(12, 50, 50)
snake = Snake(window)
games = 500


def main():
    a = DQNAgent(window, snake)

    a.train(games)
    a.play()


if __name__ == '__main__':
    main()
