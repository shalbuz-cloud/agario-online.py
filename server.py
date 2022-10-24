import socket
from random import randint

import pygame

FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
START_PLAYER_SIZE = 50  # px

colors = {
    '0': (255, 255, 0),
    '1': (255, 0, 0),
    '2': (0, 255, 0),
    '3': (0, 255, 255),
    '4': (128, 0, 128),
}


class Player:
    def __init__(self, conn, addr, x, y, r, color):
        self.conn = conn
        self.addr = addr
        self.x = x
        self.y = y
        self.r = r
        self.color = color
        self.errors = 0
        self.abs_speed = 10
        self.speed_x = 5
        self.speed_y = 2

    def update(self) -> None:
        self.x += self.speed_x
        self.y += self.speed_y

    def change_speed(self, vector: list) -> None:

        # Если курсор на бактерии
        if (vector[0] == 0) and (vector[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            # Вычисляем длину вектора по теореме Пифагора
            len_vector = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            # Нормируем вектор
            vector = (vector[0] / len_vector, vector[1] / len_vector)
            vector = (vector[0] * self.abs_speed, vector[1] * self.abs_speed)
            self.speed_x, self.speed_y = vector[0], vector[1]


def find(s: str) -> list:
    obr = None  # Открывающаяся скобка
    for i in range(len(s)):
        if s[i] == "<":
            obr = i
        elif s[i] == ">" and obr is not None:
            cbr = i
            res = s[obr + 1:cbr]
            res = list(map(int, res.split(',')))
            return res
    return []  # ""


# Создание сокета
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind(('localhost', 10000))
server.setblocking(False)
server.listen(5)

# Создание графического окна
pygame.init()
screen = pygame.display.set_mode((WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW))
clock = pygame.time.Clock()

players = []
server_works = True
while server_works:
    clock.tick(FPS)  # Ограничение fps
    # Проверим, есть ли желающие войти в игру
    try:
        # FIXME: Переделать try на метод сокета, чтобы не падало при ошибке
        client, addr = server.accept()
        print('Подключился ', addr)
        client.setblocking(False)

        players.append(Player(
            client,
            addr,
            randint(0, WIDTH_ROOM),
            randint(0, HEIGHT_ROOM),
            START_PLAYER_SIZE,
            str(randint(0, len(colors) - 1))
        ))

    except BlockingIOError:
        pass
    except KeyboardInterrupt:
        server.close()
        break

    # Считываем команды игроков
    for player in players:
        try:
            data = player.conn.recv(1024).decode()
            data = find(data)
            # Обрабатываем команды
            player.change_speed(data)
        except:
            pass

        player.update()  # Обновляем координаты

    # Отправляем новое состояние игрового поля
    for player in players:
        try:
            player.conn.send('Новое состояние игры'.encode())
            player.errors = 0
        except:  # FIXME: Скорректировать исключение
            # Накапливаем ошибки при неудачных попытках подключения
            player.errors += 1

    # Чистим список от отвалившихся игроков
    for player in players:
        if player.errors >= 500:
            player.conn.close()
            players.remove(player)

    # Нарисуем состояние комнаты
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    screen.fill('BLACK')
    for player in players:
        x = round(player.x * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        y = round(player.y * HEIGHT_SERVER_WINDOW / HEIGHT_ROOM)
        r = round(player.r * WIDTH_SERVER_WINDOW / WIDTH_ROOM)
        c = colors[player.color]

        pygame.draw.circle(screen, c, (x, y), r)
    pygame.display.update()

pygame.quit()
server.close()
