# all imports needed by the engine itself
from direct.showbase.ShowBase import ShowBase

# import our own repositories
from src.ServerRepository import GameServerRepository
from src.AIRepository import AIRepository

# initialize the engine
base = ShowBase(windowType='none')

# instantiate the server
GameServerRepository()

# The AI Repository to manage server side (AI) clients
AIRepository()

# start the server
base.run()
