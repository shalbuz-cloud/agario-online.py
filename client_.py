import asyncio

import pygame

from config import COLORS

WIDTH_WINDOW, HEIGHT_WINDOW = 1500, 1000
GRID_COLOR = (150, 150, 150)


class Grid:
    def __init__(self, screen):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.start_size = 200
        self.size = self.start_size

    async def update(self, coords):
        coords = tuple(map(int, coords.split(',')))
        self.size = self.start_size
        self.x = -self.size + -coords[0] % self.size
        self.y = -self.size + -coords[1] % self.size

    async def draw(self):
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


pygame.init()
screen = pygame.display.set_mode((WIDTH_WINDOW, HEIGHT_WINDOW))
pygame.display.set_caption('Agar.io')
grid = Grid(screen)
clock = pygame.time.Clock()


async def main_event(data):
    while True:
        screen.fill('gray25')
        await grid.draw()
        await grid.update(data)


async def handle_connection(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 10000
    )
    running = True
    while running:
        clock.tick(10)
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill('gray25')

        await grid.draw()

        try:
            print('Send: %s' % message)
            writer.write(message.encode())
            await writer.drain()
        except ConnectionError:
            break

        try:
            data = await reader.read(1024)
            data = data.decode()
            print('Received: %s' % data)
            if data:
                await grid.update(data)
        except ConnectionError:
            break

        pygame.display.update()

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


asyncio.run(handle_connection('Hello world!'))
