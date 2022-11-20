from typing import Union, Optional
from socket import socket
from math import sqrt

from server.colors.color import get_rgb
from server.core.assist import wall_check

FPS = 100
WIDTH_ROOM, HEIGHT_ROOM = 4_000, 4_000
WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW = 300, 300


class BaseUnit:
    """Базовая модель корма, игроков, ботов"""

    __START_SIZE: Optional[int] = None  # px
    __MAX_QUANTITY: Optional[int] = None

    def __init__(
            self,
            coord_x: Union[int, float],
            coord_y: Union[int, float],
            color: int,
            radius: Union[int, float],
            name: Optional[str] = None
    ) -> None:
        self._name: str = name
        self._coord_x: Optional[int, float] = coord_x
        self._coord_y: Optional[int, float] = coord_y
        self._color: tuple = get_rgb(color)
        self._radius: Optional[int, float] = radius


class Unit(BaseUnit):
    """Базовая модель динамических объектов (игроки, боты)"""

    __START_SIZE = 50
    __SPEED_RATE = 30  # Коэффициент скорости

    def __init__(self, *args, **kwargs) -> None:
        super(Unit, self).__init__(*args, **kwargs)
        self._abs_speed = self.__SPEED_RATE / sqrt(self._radius)
        self._speed_x = 5
        self._speed_y = 2
        self._is_dead = False

    def is_dead(self):
        return self._is_dead

    def update(self) -> None:
        # x coordinate
        wall_check(self._coord_x, WIDTH_ROOM, self._speed_x, self._radius)
        # y coordinate
        wall_check(self._coord_y, HEIGHT_ROOM, self._speed_y, self._radius)

        # abs_speed
        if self._radius != 0:  # TODO: is_dead()
            self._abs_speed = self.__SPEED_RATE / sqrt(self._radius)
        else:
            self._abs_speed = 0

        # Уменьшаем размер с течением времени
        if self._radius >= 100:
            self._radius -= self._radius * 0.0001

        ...

    def change_speed(self) -> None:
        pass

    def calculate_radius(self, radius: Union[int, float]) -> Union[int, float]:
        pass


class Food(BaseUnit):
    """Корм на игровом поле"""

    __START_SIZE = 15
    __MAX_QUANTITY = WIDTH_ROOM * HEIGHT_ROOM // 80_000

    def __init__(self, *args, **kwargs) -> None:
        super(Food, self).__init__(*args, **kwargs)


class Player(Unit):
    """ Player model.
    Args:
        name (str): Имя игрока.
        coord_x (int, float): Координата по оси x.
        coord_y (int, float): Координата по оси y.
        color (int): Цвет игрока.
        radius (tuple): Радиус игрока.
    """

    def __init__(self, *args, **kwargs) -> None:
        super(Player, self).__init__(*args, **kwargs)
        # self.__connection: socket = connection
        # self.__address: str = address
        self._width_window: int = 1000
        self._height_window: int = 800
        self._w_vision: int = self._width_window
        self._h_vision: int = self._height_window
        self._errors: int = 0
        self._ready: bool = False
        self._scale: int = 1  # Соотношение масштаба

    def set_options(self, data: str) -> None:
        data = data[1:-1].split()
        self._name = data[0]
        self._width_window = self._w_vision = int(data[1])
        self._height_window = self._h_vision = int(data[2])


class Bot(Unit):

    def __init__(self, *args, **kwargs) -> None:
        super(Bot, self).__init__(*args, **kwargs)


p = Player(10, 20, 13, 50, 'Alex')
print(p.__dict__)
