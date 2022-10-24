import socket

import pygame

from config import COLORS

WIDTH_WINDOW, HEIGHT_WINDOW = 1000, 800


def find(s: str) -> str:
    obr = None
    for i in range(len(s)):
        if s[i] == "<":
            obr = i
        elif s[i] == ">" and obr is not None:
            cbr = i
            res = s[obr + 1:cbr]
            return res
    return ""


def draw_enemies(data):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH_WINDOW // 2 + int(j[0])
        y = HEIGHT_WINDOW // 2 + int(j[1])
        r = int(j[2])
        c = COLORS[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)


# Подключение к серверу
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

color = sock.recv(16).decode()

# Создание окна игры
pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
pygame.display.set_caption('Agar.io')

running = True
vector = (0, 0)
v = (0, 0)  # current vector
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Считываем положение мыши игрока
    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        # От координат нач/кон. вектора - координаты нач/кон. бактерии.
        v = (pos[0] - WIDTH_WINDOW // 2, pos[1] - HEIGHT_WINDOW // 2)

        # Если вектор меньше радиуса бактерии - никуда не двигаемся
        if v[0] ** 2 + v[1] ** 2 <= 50 ** 2:
            v = (0, 0)

    # Отправляем вектор желаемого направления движения, если он поменялся
    if v != vector:
        vector = v
        message = "<%i,%i>" % (vector[0], vector[1])
        sock.send(message.encode())

    # Получаем от сервера новое состояние игрового поля
    data = sock.recv(2**20).decode()
    data = find(data).split(',')

    # Рисуем новое состояние игрового поля
    screen.fill('gray25')
    pygame.draw.circle(
        screen, COLORS[color], (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2), 50
    )
    if data != ['']:
        draw_enemies(data)
    pygame.display.update()

pygame.quit()
sock.close()
