import sys
import typing
from typing import List, Union, Callable
from random import randint
from copy import deepcopy

import pygame

from server.models.unit import Player, Food, Bot
from server.core.scheme import MetaSingleton
from server.data.config import (WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW, FPS,
                                WIDTH_ROOM, HEIGHT_ROOM)
from server.colors.palette import BASE_COLORS


class Game(metaclass=MetaSingleton):
    __running: bool = False
    __players: List[Player] = []
    __foods: List[Food] = []
    __bots: List[Bot] = []

    @classmethod
    def main_event(cls):
        pygame.init()
        screen = pygame.display.set_mode(
            (WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW)
        )
        clock = pygame.time.Clock()

        while cls.__running:

            clock.tick(FPS)  # Ограничение fps

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cls.close()

            pygame.display.flip()

    @classmethod
    def create_bot(cls) -> List[Bot]:
        cls.generate_unit(Bot, ...)
        ...

    @staticmethod
    def generate_unit(category: Callable, quantity: int) -> List[Bot, Food]:
        """Генерация списка ботов или еды"""
        return [
            category(
                randint(0, WIDTH_ROOM),
                randint(0, HEIGHT_ROOM),
                randint(0, len(BASE_COLORS) - 1)
            ) for _ in range(quantity)
        ]

    @classmethod
    def show_units(cls):  # FIXME: !!!
        return cls.__bots, cls.__foods

    @classmethod
    def close(cls):
        cls.__running = False
        pygame.quit()
        sys.exit()


# Game.main_event()
Game.generate_unit(Bot, 20)
print(Game.show_units())
