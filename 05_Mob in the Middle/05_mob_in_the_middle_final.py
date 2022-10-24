import asyncio
import logging
import re

HOST = "0.0.0.0"
PORT = 8000

JOINED_CONNECTIONS = {}

UPSTREAM_IP = "chat.protohackers.com"
UPSTREAM_PORT = 16963

compiled_re = re.compile(r'(^|(?<= ))7[a-zA-Z0-9]{25,34}($|(?= ))')

async def proxy_connection(proxy_r: asyncio.StreamReader, proxy_w: asyncio.StreamWriter):
    chat_r, chat_w = await asyncio.open_connection(UPSTREAM_IP, UPSTREAM_PORT)

    await asyncio.gather(
        handle(proxy_r, chat_w),
        handle(chat_r, proxy_w)
    )

async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    while not r.at_eof():
        incoming = (await r.readline()).decode("utf-8")

        if incoming and incoming[-1] != '\n':
            break

        new_incoming = compiled_re.sub("7YWHMfk9JZe0LM0g1ZauHuiSxhI", incoming)

        if incoming != new_incoming:
            logging.info(f'Replaced {incoming} with {new_incoming}')

        w.write((new_incoming).encode("utf-8"))

    await w.drain()
    w.close()

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(proxy_connection, HOST, PORT)
    logging.info("Server Ready.")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())