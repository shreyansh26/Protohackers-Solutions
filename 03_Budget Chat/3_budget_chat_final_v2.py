import asyncio
import logging

HOST = "0.0.0.0"
PORT = 8000

JOINED_CONNECTIONS = {}

async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    def get_username(data):
        if (not data) or (not data.isalnum()):
            return None

        username = data.strip()

        if username and username not in JOINED_CONNECTIONS:
            JOINED_CONNECTIONS[username] = (r, w)
            return username

        return None

    def broadcast(message):
        for reader, writer in JOINED_CONNECTIONS.values():
            writer.write((message).encode("utf-8"))
            
    def broadcast_except(username, message):
        for usr, (reader, writer) in JOINED_CONNECTIONS.items():
            if usr == username:
                continue
            writer.write((message).encode("utf-8"))

    w.write("Welcome to budgetchat! What shall I call you?\n".encode("utf-8"))
    data = (await r.readuntil(b'\n')).decode("utf-8")
    data = data.strip()

    username = get_username(data)

    if username is not None:
        temp_list = list(JOINED_CONNECTIONS.keys())
        temp_list.remove(username)
        connected_names = temp_list
        
        connected_names = ' '.join(connected_names)
        message = "* The room contains: " + connected_names + '\n'
        w.write(message.encode("utf-8"))
        broadcast_enter_message = f"* {username} has entered the room\n"
        broadcast_except(username, broadcast_enter_message)

        while not r.at_eof():
            data = (await r.readline()).decode("utf-8")
            if not data:
                del JOINED_CONNECTIONS[username]
                broadcast_leave_message = f"* {username} has left the room\n"
                broadcast(broadcast_leave_message)
                break
            message = f"[{username}] {data}"
            broadcast_except(username, message)
            
    await w.drain()
    w.close()


async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle, HOST, PORT)
    logging.info("Server Ready.")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())