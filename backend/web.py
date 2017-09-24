from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
from voting import run_script, get_capabilities_dict
from util import get_parties
import os.path

app = Flask('voting',
            template_folder=os.path.abspath('../frontend/'),
            static_folder=os.path.abspath('../frontend/static/'))

CORS(app)

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/api/ruv/calculate', methods=["POST"])
def calculate():
    if request.method == 'POST':
        data = {
            'constituency_names': [],
            'constituency_seats': [],
            'constituency_adjustment_seats': [],
            'parties': [],
            'votes': [],
            'adjustment_divider': 'dhondt',
            'adjustment_method': 'icelandic-law',
            'adjustment_threshold': 0.05,
        }

        payload = request.get_json(force=True)
        data['parties'] = get_parties(payload['data'])
        for k, v in payload['data'].items():
            c = v['response']['constituency']
            data['constituency_names'].append(c['identifier'])
            data['constituency_seats'].append(c['seats'])
            data['constituency_adjustment_seats'].append(c['equalizerseats'])
            pv = {pv['letter']:pv for pv in v['response']['results']['list']}

            votes = [pv[p]['votes'] if p in pv else 0 for p in data['parties']]
            data['votes'].append(votes)
            


    """
    script = request.get_json(force=True)
    if not script or script == {}:
        return jsonify({"error": "No script sent"})
    e = run_script(script)
    if type(e) == dict:
        return jsonify(e)
    """
    return jsonify(data)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('', path)

@app.route('/api/script/', methods=["POST"])
def handle_api():
    script = request.get_json(force=True)
    if not script or script == {}:
        return jsonify({"error": "No script sent"})
    e = run_script(script)
    if type(e) == dict:
        return jsonify(e)
    return jsonify(e.get_results_dict())


@app.route('/api/capabilities/', methods=["GET"])
def handle_capabilities():
    return jsonify(get_capabilities_dict())

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
