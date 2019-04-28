import argparse
import os
import json as json_module
from sanic import Sanic
from sanic.response import json, html, file, redirect
from sanic.websocket import WebSocketProtocol, ConnectionClosed
from sanic_session import Session
from sanic_jinja2 import SanicJinja2
from apps.models import db, Item

app = Sanic()
app.config.UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'uploads')

Session(app)
jinja = SanicJinja2(app)

args = None  # to be replaced by parse_args
clients = set()

STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
app.static('/favicon.ico', os.path.join(STATIC_FOLDER, 'favicon.ico'))
app.static('/static/style.css', os.path.join(STATIC_FOLDER, 'style.css'))
app.static('/static/materialize.min.css', os.path.join(STATIC_FOLDER, 'materialize.min.css'))
app.static('/static/materialize.min.js', os.path.join(STATIC_FOLDER, 'materialize.min.js'))
app.static('/static/material_icons.css', os.path.join(STATIC_FOLDER, 'material_icons.css'))
app.static('/static/flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2', os.path.join(STATIC_FOLDER, 'flUhRq6tzZclQEJ-Vdg-IuiaDsNc.woff2'))


@app.route('/')
@jinja.template('main.html')
def handle_request(request):
    items = Item.select()
    show_edit_button = True if request.args.get('edit') == 'on' else False
    return {'WS_HOST': args.host, 'WS_PORT': args.port,
            'items': items, 'show_edit_button': show_edit_button}



@app.route('/file/<filename>')
async def handle_request(request, filename):
    return await file(f'{app.config.UPLOAD_PATH}/{filename}')


@app.route("/add", methods=['GET', 'POST'])
@jinja.template('add_item.html')
async def add_item(request):
    if request.method == 'POST':
        filename = request.files["file"][0].name
        if filename:
            with open(f'{app.config.UPLOAD_PATH}/{filename}', 'wb') as f: 
                f.write(request.files["file"][0].body)

        Item.create(
            title=request.form.get('title'),
            description=request.form.get('description'),
            filename=filename
        )
        return {'message': "uploaded successfully!"}
    return {}


@app.route("/edit/<item_id>", methods=['GET', 'POST'])
@jinja.template('edit_item.html')
async def edit_item(request, item_id):
    item = Item.get(Item.id == item_id)
    if request.method == 'POST':
        item.title = request.form.get('title', item.title)
        item.description = request.form.get('description', item.description)
        item.save()
        return redirect('/?edit=on')

    return {'item': item}


@app.route("/rtc", methods=['GET', 'POST'])
@jinja.template('rtc.html')
async def rtc(request):
    return {'WS_HOST': args.host, 'WS_PORT': args.port}


users = {}

@app.websocket('/ws-rtc')
async def ws_rtc(request, ws):
    while True:
        message = await ws.recv()
        try:
            data = json_module.loads(message)
        except Exception as error:
            print('Invalid JSON', error)
            data = {}

        if data['type'] == 'login':
            print('User logged in', data['username'])
            if data['username'] in users:
                await ws.send(json_module.dumps({'type': 'login', 'success': False}))
            else:
                users[data['username']] = ws
                ws.username = data['username']
                await ws.send(json_module.dumps({'type': 'login', 'success': True}))
        elif data['type'] == 'offer':
            print('Sending offer to: ', data['otherUsername'])
            if users[data['otherUsername']] != None:
                ws.otherUsername = data['otherUsername']
                other_ws = users[data['otherUsername']]
                other_ws.send(json_module.dumps({
                    'type': 'offer',
                    'offer': data['offer'],
                    'username': ws.username
                }))
        elif data['type'] == 'answer':
            print('Sending answer to: ', data.otherUsername)
            if users[data['otherUsername']] != None:
                ws.otherUsername = data['otherUsername']
                other_ws = users[data['otherUsername']]
                other_ws.send(json_module.dumps({
                    'type': 'answer',
                    'answer': data['answer'],
                }))
        elif data['type'] == 'candidate':
            print('Sending candidate to:', data.otherUsername)
            if users[data['otherUsername']] != None:
                ws.otherUsername = data['otherUsername']
                other_ws = users[data['otherUsername']]
                other_ws.send(json_module.dumps({
                    'type': 'candidate',
                    'candidate': data.candidate
                }))



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
    db.connect()
    db.create_tables([Item])
    if not os.path.exists(app.config.UPLOAD_PATH):
        os.makedirs(app.config.UPLOAD_PATH)
    app.run(host=args.host, port=args.port)

