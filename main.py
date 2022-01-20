import argparse
import os
from sanic import Sanic
from sanic.response import file, redirect
from sanic_session import Session, InMemorySessionInterface
from sanic_jinja2 import SanicJinja2
from apps.models import db, Item, Presentation

app = Sanic("presentation")
app.config.UPLOAD_PATH = os.path.join(os.path.dirname(__file__), 'uploads')

session = Session(app, interface=InMemorySessionInterface())
jinja = SanicJinja2(app, session=session, pkg_name='pkg')

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
    items = Item.select().order_by(Item.order)
    show_edit_button = True if request.args.get('edit') == 'on' else False
    return {'WS_HOST': args.host, 'WS_PORT': args.port,
            'items': items, 'show_edit_button': show_edit_button}


@app.route('/present/<presentation_id>')
@jinja.template('presentation.html')
def present(request, presentation_id):
    items = Item.select().where(Item.presentation == presentation_id).order_by(Item.order)
    show_edit_button = True if request.args.get('edit') == 'on' else False
    return {'WS_HOST': args.host, 'WS_PORT': args.port,
            'items': items, 'show_edit_button': show_edit_button}


@app.route('/file/<filename>')
async def handle_request(request, filename):
    return await file(f'{app.config.UPLOAD_PATH}/{filename}')


@app.route("/present/<presentation_id>/add", methods=['GET', 'POST'])
@jinja.template('add_item.html')
async def add_item(request, presentation_id):
    if request.method == 'POST':
        filename = request.files["file"][0].name
        if filename:
            with open(f'{app.config.UPLOAD_PATH}/{filename}', 'wb') as f: 
                f.write(request.files["file"][0].body)

        Item.create(
            title=request.form.get('title'),
            description=request.form.get('description'),
            filename=filename,
            presentation=presentation_id
        )
        return {'message': "uploaded successfully!"}
    return {}


@app.route("/edit/<item_id>", methods=['GET', 'POST'])
@jinja.template('edit_item.html')
async def edit_item(request, item_id):
    item = Item.get(Item.id == item_id)
    if request.method == 'POST':
        item.title = request.form.get('title', item.title)
        item.order = request.form.get('order', item.order)
        item.description = request.form.get('description', item.description)
        item.save()
        return redirect('/?edit=on')

    return {'item': item}


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
    db.create_tables([Item, Presentation])
    if not os.path.exists(app.config.UPLOAD_PATH):
        os.makedirs(app.config.UPLOAD_PATH)
    app.run(host=args.host, port=args.port)

