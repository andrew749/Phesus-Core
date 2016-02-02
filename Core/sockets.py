import asyncio
import websockets
import json
"""
Simple python sockets server to handle requests.
"""
async def requestHandler(websocket, path):
    while True:
        print ("Waiting for request")
        jsonData = await websocket.recv()
        print ("got request")
        data = json.loads(jsonData)
        print ("deserialized data")
        result = route(data)
        await websocket.send(result)
        print ("sent response")

def route(body):
    """
    Args:
        body : json in the form of a dictionary
    """
    type = body.type
    result = None
    if (type == "create_node"):
        pass
    elif (type == "create_user"):
        pass
    elif (type == "create_connection"):
        pass
    elif (type == "update_node"):
        pass
    elif (type == "update_connection"):
        pass
    elif (type == "delete_node"):
        pass
    elif (type == "delete_connection"):
        pass
    elif (type == "delete_graph"):
        pass
    elif (type == "create_graph"):
        pass
    else:
        raise PhesusException("Error : command not found")
    return result

"""Start running the server."""
start_server = websockets.serve(requestHandler, 'localhost', 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
