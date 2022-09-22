import asyncio
import sys

class ChatServer:
    def __init__(self, server_name, port, loop):
        self.server_name = server_name
        self.connected_connections = {}
        self.joined_connections = {}
        print("start")
        self.server = loop.run_until_complete(
                asyncio.start_server(
                    self.accept_connection, "0.0.0.0", port, loop=loop))


    def broadcast(self, message):
        for reader, writer in self.joined_connections.values():
            writer.write((message).encode("utf-8"))

    def broadcast_except(self, username, message):
        for usr, (reader, writer) in self.joined_connections.items():
            if usr == username:
                continue
            writer.write((message).encode("utf-8"))

    @asyncio.coroutine
    def prompt_username(self, reader, writer):
        while True:
            writer.write("Welcome to budgetchat! What shall I call you?\n".encode("utf-8"))
            data = (yield from reader.readuntil(b'\n')).decode("utf-8")

            data = data.strip()

            if (not data) or (not data.isalnum()):
                return None
            username = data.strip()
            print(username)
            if username and username not in self.joined_connections:
                self.joined_connections[username] = (reader, writer)
                return username

            return None

    @asyncio.coroutine
    def handle_connection(self, username, reader):
        while True:
            data = (yield from reader.readline()).decode("utf-8")
            if not data:
                del self.joined_connections[username]
                return None
            message = f"[{username}] {data}"
            self.broadcast_except(username, message)

    @asyncio.coroutine
    def accept_connection(self, reader, writer):
        print("hello")
        username = (yield from self.prompt_username(reader, writer))
        # print(username)
        if username is not None:
            temp_list = list(self.joined_connections.keys())
            temp_list.remove(username)
            connected_names = temp_list
            
            connected_names = ' '.join(connected_names)
            message = "* The room contains: " + connected_names + '\n'
            writer.write(message.encode("utf-8"))
            broadcast_enter_message = f"* {username} has entered the room\n"
            self.broadcast_except(username, broadcast_enter_message)

            yield from self.handle_connection(username, reader)
            broadcast_leave_message = f"* {username} has left the room\n"
            self.broadcast(broadcast_leave_message)
            
        yield from writer.drain()
        writer.close()

def main(argv):
    loop = asyncio.get_event_loop()
    server = ChatServer("Test Server", 8000, loop)
    try:
        loop.run_forever()
    finally:
        loop.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))