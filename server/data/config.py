from environs import Env

env = Env()
env.read_env()

HOST = env.str('HOST')
PORT = env.int('PORT')
FPS = env.int('FPS')
WIDTH_ROOM = env.int('WIDTH_ROOM')
HEIGHT_ROOM = env.int('HEIGHT_ROOM')
WIDTH_SERVER_WINDOW = env.int('WIDTH_SERVER_WINDOW')
HEIGHT_SERVER_WINDOW = env.int('HEIGHT_SERVER_WINDOW')
