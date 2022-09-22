import asyncio
import json
import logging
import sympy

HOST = "0.0.0.0"
PORT = 8000

async def handle(r: asyncio.StreamReader, w: asyncio.StreamWriter):
    def dump(dat):
        w.write(json.dumps(dat).encode("utf8"))
        w.write(b"\n")

    while not r.at_eof():
        try:
            o = json.loads((await r.readuntil(b"\n")).decode("utf8"))
            logging.debug(f"Request: {o}")
            method = o["method"]
            number = o["number"]
            if method != "isPrime":
                raise ValueError()
            if type(number) == int:
                dump({"method": method, "prime": sympy.isprime(number)})
            elif type(number) == float:
                dump({"method": method, "prime": False})
            else:
                raise ValueError()
        except asyncio.LimitOverrunError:
            dump({"error": "limit_overrun"})
            break
        except asyncio.IncompleteReadError:
            dump({"error": "invalid_terminator"})
            break
        except (ValueError, KeyError):
            dump({"error": "invalid_json"})
            break
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