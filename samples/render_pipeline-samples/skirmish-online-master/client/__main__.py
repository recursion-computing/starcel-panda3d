from .client import Client
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        server_address = "127.0.0.1"
    else:
        server_address = sys.argv[1]
    Client(server_address).run()
