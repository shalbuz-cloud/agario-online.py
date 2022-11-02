import socket
from random import randint, choice
from typing import List

import pygame

from config import COLORS

# TODO: Перенести константы в конфиг файл
FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 4000, 4000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300
START_PLAYER_SIZE = 50  # px
START_FOOD_SIZE = 15
MOBS_QUANTITY = 25
FOODS_QUANTITY = WIDTH_ROOM * HEIGHT_ROOM // 80_000
SPEED_RATE = 30  # Коэффициент скорости


class Player:
    def __init__(self, conn, addr, x, y, r, color):
        self.conn = conn
        self.addr = addr
        self.x: int | float = x
        self.y: int | float = y
        self.r: int | float = r
        self.color: str = color
        self.scale: int = 1

        self.width_window: int = 1000
        self.height_window: int = 800
        self.w_vision: int = 1000
        self.h_vision: int = 800

        self.errors: int = 0

        self.abs_speed: int = SPEED_RATE / (r ** 0.5)
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

        # abs_speed
        # TODO: Менять абс. скорость только при изменении размера
        self.abs_speed = SPEED_RATE / (self.r ** 0.5)

        # Уменьшаем размер с течением времени
        if self.r >= 100:
            self.r -= self.r * 0.0001

        # Изменим масштаб игрока
        # Если радиус большой, увеличиваем масштаб
        # TODO: Плавное масштабирование
        if self.r >= self.w_vision / 4 or self.r >= self.h_vision / 4:
            # Если игрок не видит всю карту
            if self.w_vision <= WIDTH_ROOM or self.h_vision <= HEIGHT_ROOM:
                self.scale *= 2
                # TODO: Вывести в отдельную функцию
                self.w_vision = self.width_window * self.scale
                self.h_vision = self.height_window * self.scale
        if self.r < self.w_vision / 8 and self.r < self.h_vision:
            if self.scale > 1:
                self.scale //= 2
                self.w_vision = self.width_window * self.scale
                self.h_vision = self.height_window * self.scale

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


class Food:
    """Корм на игровом поле"""

    def __init__(self, x, y, r, color):
        self.x = x
        self.y = y
        self.r = r
        self.color = color


def find(s: str) -> list:
    """Обработка полученных данных от клиента"""
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


def calculate_radius(radius1: int, radius2: int):
    """Вычисление нового радиуса после поглощения другого объекта"""
    return (radius1 ** 2 + radius2 ** 2) ** 0.5


players: List[Player]
foods: List[Food]

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
    ) for _ in range(MOBS_QUANTITY)
]

# Создание стартового набора корма
foods = [
    Food(
        randint(0, WIDTH_ROOM),
        randint(0, HEIGHT_ROOM),
        START_FOOD_SIZE,
        str(randint(0, len(COLORS) - 1))
    ) for _ in range(FOODS_QUANTITY)
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

            # Появляемся на месте корма, чтобы не появиться
            # внутри другого игрока.
            spawn = choice(foods)
            new_player = Player(
                client,
                addr,
                spawn.x,
                spawn.y,
                START_PLAYER_SIZE,
                str(randint(0, len(COLORS) - 1))
            )

            # Удаляем использованный корм, чтобы не увеличить начальный объем
            foods.remove(spawn)

            message = " ".join([str(new_player.r), new_player.color])
            new_player.conn.send(message.encode())
            players.append(new_player)

        except BlockingIOError:
            pass
        except KeyboardInterrupt:
            server.close()
            break

        # Дополняем список ботов
        for i in range(MOBS_QUANTITY - len(players)):
            if len(foods) > 0:
                spawn = choice(foods)  # TODO: Вынести в отдельный метод

                # TODO: Вынести создание ботов в метод класса
                # TODO: Подсчет общего кол-во игроков в классе
                players.append(
                    Player(
                        None,
                        None,
                        spawn.x,
                        spawn.y,
                        randint(10, 100),
                        str(randint(0, len(COLORS) - 1))
                    )
                )
                foods.remove(spawn)

        # Дополняем список корма
        for i in range(FOODS_QUANTITY - len(foods)):
            foods.append(
                Food(
                    randint(0, WIDTH_ROOM),
                    randint(0, HEIGHT_ROOM),
                    START_FOOD_SIZE,
                    str(randint(0, len(COLORS) - 1))
                )
            )

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
        # Какой корм видит i игрок
        for f in range(len(foods)):
            dist_x = foods[f].x - players[i].x
            dist_y = foods[f].y - players[i].y

            # i игрок видит k корм
            if (  # TODO: Перенести логику в отдельную функцию
                    abs(dist_x) <= players[i].w_vision // 2 + foods[f].r
                    and
                    abs(dist_y) <= players[i].h_vision // 2 * foods[f].r
            ):
                # i может съесть k корм
                if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r:
                    # Изменим радиус i игрока
                    players[i].r = calculate_radius(players[i].r, foods[f].r)
                    foods[f].r = 0  # FIXME: Удалять объект

                # TODO: Оптимизировать проверку соединения
                if players[i].conn is not None and foods[f].r is not None:
                    # Подготовим данные  # TODO: вывести в отд. функцию
                    x_ = str(round(dist_x / players[i].scale))
                    y_ = str(round(dist_y / players[i].scale))
                    r_ = str(round(foods[f].r / players[i].scale))
                    c_ = foods[f].color

                    visible_balls[i].append(' '.join([x_, y_, r_, c_]))

        for j in range(i + 1, len(players)):
            # Рассматриваем пару i и j игрока
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y

            # i видит j
            if (  # TODO: Перенести логику в отдельную функцию
                    abs(dist_x) <= players[i].w_vision // 2 + players[j].r
                    and
                    abs(dist_y) <= players[i].h_vision // 2 + players[j].r
            ):
                # i может съесть j  # TODO: Убрать дублирование
                # Если центр бактерии j внутри i
                if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r \
                        and players[i].r > 1.1 * players[j].r:
                    # Изменим радиус i игрока
                    players[i].r = calculate_radius(players[i].r, players[j].r)
                    # Обнулим данные игрока, чтобы не отключать сразу
                    players[j].r = 0
                    players[j].speed_x = 0
                    players[j].speed_y = 0

                if players[i].conn is not None:  # Если не бот
                    # Подготовим данные к добавлению в список видимых игроков
                    x_ = str(round(dist_x / players[i].scale))
                    y_ = str(round(dist_y / players[i].scale))
                    r_ = str(round(players[j].r / players[i].scale))
                    c_ = players[j].color

                    visible_balls[i].append(' '.join([x_, y_, r_, c_]))

            # j видит i
            if (
                    abs(dist_x) <= players[j].w_vision // 2 + players[i].r
                    and
                    abs(dist_y) <= players[j].h_vision // 2 + players[i].r
            ):
                # j может съесть i  # TODO: Убрать дублирование
                # Если центр бактерии j внутри i
                if (dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[j].r \
                        and players[j].r > 1.1 * players[i].r:
                    # Изменим радиус j игрока
                    players[j].r = calculate_radius(players[j].r, players[i].r)
                    # Обнулим данные игрока, чтобы не отключать сразу
                    players[i].r = 0
                    players[i].speed_x = 0
                    players[i].speed_y = 0

                if players[j].conn is not None:  # Если не бот
                    # Подготовим данные к добавлению в список видимых игроков
                    x_ = str(round(-dist_x / players[j].scale))
                    y_ = str(round(-dist_y / players[j].scale))
                    r_ = str(round(players[i].r / players[j].scale))
                    c_ = players[i].color

                    visible_balls[j].append(' '.join([x_, y_, r_, c_]))

    # Формируем ответ каждому игроку
    responses = ['' for i in range(len(players))]
    for i in range(len(players)):
        r_ = str(round(players[i].r / players[i].scale))
        visible_balls[i] = [r_] + visible_balls[i]  # FIXME
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
        # TODO: Вынести статус игрока в отдельный параметр
        if player.errors >= 500 or (player.r == 0):
            if player.conn is not None:
                player.conn.close()
            players.remove(player)

    # Чистим список съеденных объектов
    for f in foods:
        if f.r == 0:
            foods.remove(f)

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
