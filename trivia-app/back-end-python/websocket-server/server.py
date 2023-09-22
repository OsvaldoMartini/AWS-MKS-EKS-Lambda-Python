# import app
from websocket_server import WebsocketServer
import json
# import sys
# sys.path.insert(1, '/back-end-python/gameactions')
# Called for every client connecting (after handshake)


def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    NEW_GAME_EVENT = {
        "requestContext": {
            "connectionId": client['id']
        }
    }
    # app.trivia_newgame(NEW_GAME_EVENT, None)
    server.send_message_to_all(json.dumps({"message": "All Connected"}))


# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200]+'..'
    print("Receive from Client(%d) said: %s" % (client['id'], message))
    msg = json.loads(message)
    if "slider2" in msg:
        print("Key exist in JSON data")
        # server.send_message(message)
        for clientConnected in server.clients:
            if clientConnected['id'] != client.get('id'):
                server.send_message(clientConnected, message)
                # str(client.address[0]) + ' - ' + str(client.data))
    else:
        for clientConnected in server.clients:
            if clientConnected['id'] != client.get('id'):
                server.send_message(clientConnected, message)


PORT = 9001
server = WebsocketServer(port=PORT)
print("Websocket: ws://localhost:%s" % (PORT))
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
