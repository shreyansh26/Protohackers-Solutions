import asyncio
from struct import *
import logging

HOST = "0.0.0.0"
PORT = 8000

def get_mean(STORE, t_min, t_max):
    summ = 0
    cnt = 0

    for i in STORE:
        if i[0] <= t_max and i[0] >= t_min:
            summ += i[1]
            cnt += 1

    if cnt == 0:
        return 0

    return summ // cnt

async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    STORE = []
    while not r.at_eof():
        try:
            instr, val1, val2 = unpack('!cii', await r.readexactly(9))
            # logging.debug(f"Request: {instr}, {val1}, {val2}")     # Commented out because they slow the program

            if instr == b'I':
                STORE.append((val1, val2))
            elif instr == b'Q':
                mean_val = get_mean(STORE, val1, val2)
                w.write(pack('!i', mean_val))
                # logging.debug(f"Mean: {mean_val}")     # Commented out because they slow the program

        except (ValueError, asyncio.IncompleteReadError):
            w.write(pack('!i', -100))

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