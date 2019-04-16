import os
from sanic import Sanic
from sanic.response import json, html
from sanic.websocket import WebSocketProtocol

app = Sanic()

clients = set()

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
app.static('/favicon.ico', os.path.join(STATIC_FOLDER, 'favicon.ico'))


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
        sec_id = recv_message
        for client in clients:
            await client.send(sec_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

