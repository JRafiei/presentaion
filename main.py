import argparse
import os
from sanic import Sanic
from sanic.response import json, html
from sanic.websocket import WebSocketProtocol, ConnectionClosed
from sanic_session import Session
from sanic_jinja2 import SanicJinja2
from apps.models import db

app = Sanic()
app.config.UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'uploads')

Session(app)
jinja = SanicJinja2(app)

clients = set()

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
app.static('/favicon.ico', os.path.join(STATIC_FOLDER, 'favicon.ico'))


@app.route('/')
@jinja.template('main.html')
def handle_request(request):
    return {'WS_HOST': args.host, 'WS_PORT': args.port}


@app.route("/add", methods=['GET', 'POST'])
@jinja.template('add_item.html')
async def add_item(request):
    if request.method == 'POST':
        filename = request.files["file"][0].name
        f = open(f'{app.config.UPLOAD_PATH}/{filename}', 'wb')
        f.write(request.files["file"][0].body)
        f.close()

    return {}


@app.websocket('/ws')
async def feed(request, ws):
    clients.add(ws)
    while True:
        try:
            recv_message = await ws.recv()
            sec_id = recv_message
            for client in clients:
                await client.send(sec_id)
        except ConnectionClosed:
            clients.remove(ws)
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", default="localhost",
                        help="server ip")
    parser.add_argument("-p", "--port", default=8000,
                        help="server port")
    args = parser.parse_args()
    # db.connect()
    # db.create_tables([User, Tweet])
    if not os.path.exists(app.config.UPLOAD_PATH):
        os.makedirs(app.config.UPLOAD_PATH)
    app.run(host=args.host, port=args.port)

