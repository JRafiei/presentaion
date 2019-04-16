from sanic import Sanic
from sanic.response import json, html
from sanic.websocket import WebSocketProtocol

app = Sanic()

clients = set()

@app.route('/')
def handle_request(request):
    template = open('./main.html')
    response = template.read()
    template.close
    return html(response)


@app.websocket('/ws')
async def feed(request, ws):
    clients.add(ws)
    while True:
        recv_message = await ws.recv()
        id = recv_message
        print(id)
        for client in clients:
            await client.send(id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

