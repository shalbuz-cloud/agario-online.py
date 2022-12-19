import asyncio
import random

import pygame

clock = pygame.time.Clock()

pygame.init()


async def handle_connection(reader, writer):
    addr = writer.get_extra_info('peername')
    print('Connected by', addr)
    while True:
        clock.tick(240)
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
            data = '%i, %i' % (random.randint(0, 100), random.randint(0, 100))
            print(data)
            data = data.encode()
            writer.write(data)
        except ConnectionError:
            print('Client suddenly closed, cannot send')
            break

    writer.close()
    print('Disconnect by', addr)


async def main(host, port):
    srv = await asyncio.start_server(handle_connection, host, port)
    async with srv:
        await srv.serve_forever()


HOST, PORT = "", 10000

if __name__ == '__main__':
    asyncio.run(main(HOST, PORT))
