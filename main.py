import argparse
import os
from sanic import Sanic
from sanic.response import json, html
from sanic.websocket import WebSocketProtocol
from sanic_session import Session
from sanic_jinja2 import SanicJinja2

app = Sanic()
Session(app)
jinja = SanicJinja2(app)

clients = set()

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
app.static('/favicon.ico', os.path.join(STATIC_FOLDER, 'favicon.ico'))


@app.route('/')
@jinja.template('main.html')
def handle_request(request):
    return {'WS_HOST': args.host, 'WS_PORT': args.port}


@app.websocket('/ws')
async def feed(request, ws):
    clients.add(ws)
    while True:
        recv_message = await ws.recv()
        sec_id = recv_message
        for client in clients:
            await client.send(sec_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default="localhost",
                        help="server ip")
    parser.add_argument("-p", "--port", default=8000,
                        help="server port")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)

