import socket
from random import randint

import pygame

from config import COLORS

FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
START_PLAYER_SIZE = 50  # px
MOBS_QUANTITY = 25


class Player:
    def __init__(self, conn, addr, x, y, r, color):
        self.conn = conn
        self.addr = addr
        self.x: int | float = x
        self.y: int | float = y
        self.r: int | float = r
        self.color: str = color

        self.w_vision: int = 1000
        self.h_vision: int = 800

        self.errors: int = 0

        self.abs_speed: int = 1
        self.speed_x: int = 5
        self.speed_y: int = 2

    def update(self) -> None:  # TODO: Убрать дублирование кода
        # x coordinate
        if self.x - self.r <= 0:  # Достиг левой стены
            if self.speed_x >= 0:  # Разрешаем идти только вправо
                self.x += self.speed_x
        elif self.x + self.r >= WIDTH_ROOM:  # Достиг правой стены
            if self.speed_x <= 0:  # Разрешаем идти только влево
                self.x += self.speed_x
        else:  # Не достиг стен
            self.x += self.speed_x

        # y coordinate
        if self.y - self.r <= 0:  # Достиг верхней стены
            if self.speed_y >= 0:  # Разрешаем идти только вниз
                self.y += self.speed_y
        elif self.y + self.r >= HEIGHT_ROOM:  # Достиг нижней стены
            if self.speed_y <= 0:  # Разрешаем идти только вверх
                self.y += self.speed_y
        else:  # Не достиг стен
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


# Создание сокета  # TODO: Сделать сокет асинхронным
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
server.bind(('localhost', 10000))
server.setblocking(False)
server.listen(5)

# Создание графического окна
pygame.init()
screen = pygame.display.set_mode((WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW))
clock = pygame.time.Clock()

# Создание стартового набора мобов
players = [
    Player(
        None,
        None,
        randint(0, WIDTH_ROOM),
        randint(0, HEIGHT_ROOM),
        randint(10, 100),
        str(randint(0, len(COLORS) - 1))
    ) for i in range(MOBS_QUANTITY)
]

tick = -1  # Игровой цикл (ограничение)
server_works = True
while server_works:
    tick += 1
    clock.tick(FPS)  # Ограничение fps
    if tick == 200:  # Раз в 2 сек
        tick = 0
        # Проверим, есть ли желающие войти в игру
        try:
            # FIXME: Переделать try на метод сокета, чтобы не падало при ошибке
            client, addr = server.accept()
            print('Подключился ', addr)
            client.setblocking(False)
            new_player = Player(
                client,
                addr,
                randint(0, WIDTH_ROOM),
                randint(0, HEIGHT_ROOM),
                START_PLAYER_SIZE,
                str(randint(0, len(COLORS) - 1))
            )
            new_player.conn.send(new_player.color.encode())
            players.append(new_player)

        except BlockingIOError:
            pass
        except KeyboardInterrupt:
            server.close()
            break

    # Считываем команды игроков
    for player in players:
        if player.conn is not None:  # Если не бот
            try:
                data = player.conn.recv(1024).decode()
                data = find(data)
                # Обрабатываем команды
                player.change_speed(data)
            except:
                pass
        else:
            if tick == 100:  # TODO: Оптимизировать
                data = [randint(-100, 100), randint(-100, 100)]
                player.change_speed(data)

        player.update()  # Обновляем координаты

    # Определим, что видит каждый игрок
    visible_balls = [[] for i in range(len(players))]
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            # Рассматриваем пару i и j игрока
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y

            # i видит j
            if players[i].conn is not None and (  # Если не бот
                    abs(dist_x) <= players[i].w_vision // 2 + players[j].r
                    and
                    abs(dist_y) <= players[i].h_vision // 2 + players[j].r
            ):
                # Подготовим данные к добавлению в список видимых игроков
                x_ = str(round(dist_x))
                y_ = str(round(dist_y))
                r_ = str(round(players[j].r))
                c_ = players[j].color

                visible_balls[i].append(' '.join([x_, y_, r_, c_]))

            # j видит i
            if players[j].conn is not None and (  # Если не бот
                    abs(dist_x) <= players[j].w_vision // 2 + players[i].r
                    and
                    abs(dist_y) <= players[j].h_vision // 2 + players[i].r
            ):
                # Подготовим данные к добавлению в список видимых игроков
                x_ = str(round(-dist_x))
                y_ = str(round(-dist_y))
                r_ = str(round(players[i].r))
                c_ = players[i].color

                visible_balls[j].append(' '.join([x_, y_, r_, c_]))

    # Формируем ответ каждому игроку
    responses = ['' for i in range(len(players))]
    for i in range(len(players)):
        responses[i] = "<%s>" % ",".join(visible_balls[i])

    # Отправляем новое состояние игрового поля
    for i in range(len(players)):
        if players[i].conn is not None:  # Если не бот
            try:
                players[i].conn.send(responses[i].encode())
                players[i].errors = 0
            except:  # FIXME: Скорректировать исключение
                # Накапливаем ошибки при неудачных попытках подключения
                players[i].errors += 1

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
        c = COLORS[player.color]

        pygame.draw.circle(screen, c, (x, y), r)
    pygame.display.update()

pygame.quit()
server.close()
