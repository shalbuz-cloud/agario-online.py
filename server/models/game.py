import sys
from typing import List, Union, Callable
from random import randint
import asyncio

import pygame

from server.models.unit import Player, Food, Bot
from server.core.scheme import MetaSingleton
from server.data.config import (WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW, FPS,
                                WIDTH_ROOM, HEIGHT_ROOM)
from server.colors.palette import BASE_COLORS


class Game(metaclass=MetaSingleton):
    __players: List[Player] = []
    __foods: List[Food] = []
    __bots: List[Bot] = []

    def __init__(self, host, port):
        self.host = host
        self.port = port

    @classmethod
    async def __main_event(cls, reader, writer):
        pygame.init()
        screen = pygame.display.set_mode(
            (WIDTH_SERVER_WINDOW, HEIGHT_SERVER_WINDOW)
        )
        clock = pygame.time.Clock()
        addr = writer.get_extra_info('peername')
        print('Connected by')
        # while cls.__running:
        while True:
            clock.tick(FPS)  # Ограничение fps

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cls.close()

            # Receive
            try:
                data = await reader.read(1024)
                print(data)
            except ConnectionError:
                print('Client suddenly closed while receiving from %s' % addr)
                break

            if not data:
                break

            try:
                data = '%i, %i' % (randint(0, 100), randint(0, 100))
                print(data)
                data = data.encode()
                writer.write(data)
            except ConnectionError:
                print('Client suddenly closed, cannot send')
                break

            pygame.display.flip()

        writer.close()
        print('Disconnect by', addr)

    async def __main_loop(self):
        srv = await asyncio.start_server(
            self.__main_event, self.host, self.port
        )
        async with srv:
            await srv.serve_forever()

    def start(self):
        asyncio.run(self.__main_loop())

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
        pygame.quit()
        sys.exit()


game = Game('', 10000)
game.start()
