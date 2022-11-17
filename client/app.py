import socket

import pygame

from config import COLORS

WIDTH_WINDOW, HEIGHT_WINDOW = 1500, 1000
GRID_COLOR = (150, 150, 150)


class Me:
    def __init__(self, data: str):
        data = data.split()
        self.r = int(data[0])
        self.color = data[1]

    def update(self, new_radius: int):
        self.r = new_radius

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(
                screen,
                COLORS[self.color],
                (WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2),
                self.r
            )

            write_name(WIDTH_WINDOW // 2, HEIGHT_WINDOW // 2, self.r, my_name)


class Grid:
    def __init__(self, screen):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.start_size = 200
        self.size = self.start_size

    def update(self, coord_x: int, coord_y: int, scale: int):
        self.size = self.start_size // scale
        self.x = -self.size + -coord_x % self.size
        self.y = -self.size + -coord_y % self.size

    def draw(self):
        # TODO: Перенести draw в отдельный класс
        # Вертикальные полосы
        for i in range(WIDTH_WINDOW // self.size + 2):
            # for i in range(WIDTH_WINDOW // self.size + 2):
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                # координаты верхнего конца отрезка
                [self.x + i * self.size, 0],
                # координаты нижнего конца отрезка
                [self.x + i * self.size, HEIGHT_WINDOW],
                1
            )

        # Горизонтальные полосы
        for i in range(HEIGHT_WINDOW // self.size + 2):
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                [0, self.y + i * self.size],
                [WIDTH_WINDOW, self.y + i * self.size],  # TODO: оптимизировать
                1
            )


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

        if len(j) == 5:
            write_name(x, y, r, j[4])


def write_name(coord_x: int, coord_y: int, r: int, name: str) -> None:
    font = pygame.font.Font(None, r)
    text = font.render(name, True, (0, 0, 0))
    rect = text.get_rect(center=(coord_x, coord_y))
    screen.blit(text, rect)


# Создание окна игры
pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
pygame.display.set_caption('Agar.io')

# Подключение к серверу
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

# Отправляем серверу свой ник и размеры окна
my_name = 'Sype'  # TODO: Ввод пользователем через интерфейс
sock.send(('.%s.' % ' '.join(
    [my_name, str(WIDTH_WINDOW), str(HEIGHT_WINDOW)]
)).encode())

# Получаем свой размер и цвет
me = Me(sock.recv(64).decode())
sock.send('!'.encode())  # Отправляем подтверждение на сервер
grid = Grid(screen)

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
        if v[0] ** 2 + v[1] ** 2 <= me.r ** 2:
            v = (0, 0)

    # Отправляем вектор желаемого направления движения, если он поменялся
    if v != vector:
        vector = v
        message = "<%i,%i>" % (vector[0], vector[1])
        sock.send(message.encode())

    # Получаем новое состояние игрового поля
    try:
        data = sock.recv(2 ** 20).decode()
        data = find(data).split(',')
    except ConnectionAbortedError:
        running = False
        break

    # Обработка сообщения с сервера
    if data != ['']:
        parameters = list(map(int, data[0].split()))
        me.update(int(parameters[0]))
        grid.update(*parameters[1:])
        # Рисуем новое состояние игрового поля
        screen.fill('gray25')
        grid.draw()
        draw_enemies(data[1:])
        me.draw()

    pygame.display.update()

pygame.quit()
sock.close()
