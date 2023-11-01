welcome_msg = "Welcome to Skirmish Online!\n\n"

help = (
    "Available commands:\n"
    "/setname <name>\n"
    "/setmodel 0-3\n"
    "/setweapon 0-3\n\n"
    "Use Q, E, R, F to cast spells.\n\n"
    "Press ENTER to type a command or chat message.\n\n"
)


welcome_msg += help

position_update_delay = 100

connection_check_timeout = 10
connection_check_interval = 2

redis_host = "redis"

use_redis_pubsub = False
