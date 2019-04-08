from snake import Window, Snake

w = Window(500, 500, 50, 50)
s = Snake(w)

run = True
while run:
    s.step()

    print(s.observe())

