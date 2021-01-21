import snot_dare_manager as sdm
from flask import Flask, render_template, request, redirect, url_for
import json
import os


app = Flask(__name__)
ip_address = '127.0.0.1:' + os.environ['FLASK_RUN_PORT']
role = os.environ['LDN_ROLE']

manager = sdm.SnotDareManager(ip_address, role)


@app.route('/', methods=['GET'])
def root_get():
    return render_template('root.html', mode=manager.mode, role=manager.role, consensors=manager.consensors)


@app.route('/', methods=['POST'])
def root_post():
    consensors = request.form.getlist('consensors')
    print('CONSENSORS: ' + repr(consensors))

    if manager.setup_consensors(consensors):
        return redirect('/')
    else:
        return 'malformed consensor ip addresses', 400


@app.route('/new_snot_dare', methods=['POST'])
def new_snot_dare_post():
    snot_dare = request.form.get('snot_dare')
    if snot_dare is not None:
        manager.send_new_snot_dare(snot_dare)
    return redirect('/')


@app.route('/api/messages', methods=['POST'])
def api_messages_post():
    manager.incoming_messages.append(json.loads(request.json))

    return 'ok', 200
