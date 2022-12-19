import socket
from typing import Optional, List

from .scheme import MetaSingleton
from ..data.config import HOST, PORT
from ..models.unit import Player, Bot, Food


class Server(metaclass=MetaSingleton):
    __connections: tuple = ()
    __running: bool = False
    __server: Optional[socket.socket] = None

    # TODO: Сделать сокет асинхронным

    def __init__(self):
        self.__players: Optional[List[Player]] = None
        self.__bots: Optional[List[Bot]] = None
        self.__foods: Optional[List[Food]] = None

    def run_server(self) -> socket.socket:
        if not self.__running:
            serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            serv.bind((HOST, PORT))
            serv.setblocking(False)
            serv.listen(5)
            self.__running = True
        return self.__server

    @staticmethod
    def find(string: str) -> list:
        """Обработка полученных данных от клиента"""

        obr = None  # Открывающаяся скобка
        for i in range(len(string)):
            if string[i] == "<":
                obr = i
            elif string[i] == ">" and obr is not None:
                cbr = i
                res = string[obr + 1:cbr]
                res = list(map(int, res.split(',')))
                return res
        return []
