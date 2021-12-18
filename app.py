from flask import Flask, render_template, request, send_file, make_response
from db import db_add_item, db_get_items, db_get_unique_types_styles,\
    db_edit_item, db_add_use, db_find_item, db_get_item_uses

app = Flask(__name__)


@app.route('/js/<script>')
def send_js(script):
    if '..' in script or '//' in script:
        return None
    return send_file(f'./js/{script}')


@app.route('/favicon.ico')
def send_favicon():
    return send_file('./favicon.ico')


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/add')
def add_form():
    types, styles = db_get_unique_types_styles()
    return render_template('add.html', types=types, styles=styles)


action_dict = {
    'edit': db_edit_item,
    'add': db_add_item,
    'use': db_add_use
}


@app.route('/rest_api', methods=['POST'])
def rest_api():
    if not request.args['action']:
        return json_response(None, 'No action provided')
    if request.args['action'] not in action_dict.keys():
        return json_response(None, 'Unknown action')

    print(request.args['action'])
    print(request.form)
    res, error = action_dict[request.args['action']](request.form)
    return json_response(res, error)


@app.route('/items')
def show_items():
    items = db_get_items()
    return render_template('items.html', items=items)


@app.route('/view')
def show_item():
    if 'id' not in request.args or not request.args['id']:
        return json_response(None, 'Missing item Id')
    id_to_find = request.args['id']
    item_row = db_find_item(id_to_find)
    item_uses = db_get_item_uses(id_to_find)
    print(item_row)
    return render_template('view_item.html', item=item_row, uses=item_uses)


def json_response(payload=None, error=None):
    response = {'ok': not error}
    if error:
        response['error'] = error
    response['payload'] = payload
    return make_response(response)


if __name__ == '__main__':
    app.run()
