import asyncio
import websockets
"""
Simple python sockets server to handle requests.
"""
async def hello(websocket, path):
    while True:
        print("running")
        name = await websocket.recv()
        print("< {}".format(name))

        greeting = "Hello {}!".format(name)
        await websocket.send(greeting)
        print("> {}".format(greeting))

start_server = websockets.serve(hello, 'localhost', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
