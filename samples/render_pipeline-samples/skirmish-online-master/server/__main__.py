from .server import Server
import time
import logging


root = logging.getLogger()


if __name__ == "__main__":
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    server = Server()
    server.run()
    root.info("started")

    while True:
        time.sleep(10)
