from abc import ABC, abstractmethod
from typing import Union, Optional, List
from math import sqrt

from server.colors.color import get_rgb
from server.core.assist import wall_check
from server.data.config import WIDTH_ROOM, HEIGHT_ROOM


class BaseUnit(ABC):
    """Базовая модель корма, игроков, ботов"""

    _START_SIZE: Optional[int] = None  # px
    _MAX_QUANTITY: Optional[int] = None

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

    @classmethod
    @abstractmethod
    def create(cls) -> list: pass


class Unit(BaseUnit):
    """Базовая модель динамических объектов (игроки, боты)"""

    _START_SIZE = 50
    _SPEED_RATE = 30  # Коэффициент скорости
    _MAX_QUANTITY = 30

    def __init__(self, *args, **kwargs) -> None:
        super(Unit, self).__init__(radius=self._START_SIZE, *args, **kwargs)
        self._abs_speed = self._SPEED_RATE / sqrt(self._radius)
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
            self._abs_speed = self._SPEED_RATE / sqrt(self._radius)
        else:
            self._abs_speed = 0

        # Уменьшаем размер с течением времени
        if self._radius >= 100:
            self._radius -= self._radius * 0.0001

        ...

    def calculate_radius(self, radius: Union[int, float]) -> Union[int, float]:
        """Вычисление нового радиуса после поглощения другого объекта"""
        return sqrt(pow(self._radius, 2) + pow(radius, 2))

    @classmethod
    def create(cls) -> list:
        pass


class Food(BaseUnit):
    """Корм на игровом поле"""

    _START_SIZE = 15
    _MAX_QUANTITY = WIDTH_ROOM * HEIGHT_ROOM // 80_000

    def __init__(self, *args, **kwargs) -> None:
        super(Food, self).__init__(radius=self._START_SIZE, *args, **kwargs)

    @classmethod
    def create(cls):
        ...


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

    def set_scale(self):
        self._w_vision = self._width_window * self._scale
        self._h_vision = self._height_window * self._scale

    def update(self) -> None:
        super(Player, self).update()
        if (
                self._radius >= self._w_vision / 4
                or self._radius >= self._h_vision / 4
        ):
            # Если игрок не видит всю карту
            if self._w_vision <= WIDTH_ROOM or self._h_vision <= HEIGHT_ROOM:
                self._scale *= 2
                self.set_scale()
        if self._radius < self._w_vision / 8 and self._radius < self._h_vision:
            if self._scale > 1:
                self._scale //= 2
                self.set_scale()

    def change_speed(self, vector: List[Union[int, float]]) -> None:
        # Если курсор на бактерии
        if vector[0] == 0 and vector[1] == 0:
            self._speed_x = 0
            self._speed_y = 0
        else:
            # Вычисляем длину вектора по теореме Пифагора
            len_vector = sqrt(pow(vector[0], 2) + pow(vector[1], 2))
            # Нормализуем вектор
            vector = (vector[0] / len_vector, vector[1] / len_vector)
            vector = (vector[0] * self._abs_speed, vector[1] * self._abs_speed)
            self._speed_x, self._speed_y = vector[0], vector[1]


class Bot(Unit):

    def __init__(self, *args, **kwargs) -> None:
        super(Bot, self).__init__(*args, **kwargs)
