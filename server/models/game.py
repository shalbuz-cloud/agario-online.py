import sys
from typing import List, Union, Callable
from random import randint

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
    def create_bot(cls, quantity=None):
        max_q = getattr(Bot, '_MAX_QUANTITY')

        # bot slots left
        left_q = max_q - len(cls.__bots)
        left_q = left_q if left_q > 0 else 0
        if left_q:
            quantity = quantity if (quantity and quantity < left_q) else left_q
            cls.__bots += cls.generate_unit(Bot, quantity)

    @classmethod
    def create_food(cls):
        max_q = getattr(Food, '_MAX_QUANTITY')

        # food slots left
        left_q = max_q - len(cls.__foods)
        left_q = left_q if left_q > 0 else 0
        if left_q:
            cls.__foods += cls.generate_unit(Food, left_q)

    @staticmethod
    def generate_unit(
            category: Callable, quantity: int
    ) -> List[Union[Bot, Food]]:
        """Генерация списка ботов или еды"""
        return [
            category(
                randint(0, WIDTH_ROOM),
                randint(0, HEIGHT_ROOM),
                randint(0, len(BASE_COLORS) - 1)
            ) for _ in range(quantity)
        ]

    @classmethod
    def show_units(cls) -> tuple:
        return len(cls.__bots), len(cls.__foods)

    @classmethod
    def close(cls):
        cls.__running = False
        pygame.quit()
        sys.exit()


# Game.main_event()
game = Game()
game.create_food()
game.create_food()
game.create_food()
print(game.show_units())
