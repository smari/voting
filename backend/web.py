from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
from voting import run_script, get_capabilities_dict
from util import get_parties, ruv_transform
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

    data = {
        'constituency_names': [],
        'constituency_seats': [],
        'constituency_adjustment_seats': [],
        'parties': [],
        'votes': [],
        'adjustment_divider': 'dhondt',
        'adjustment_method': 'icelandic-law',
        'adjustment_threshold': 0.05,
        'primary_divider': 'dhondt',
        'show_entropy': False,
        'simulate': False,
        'debug': False,
        'output': 'simple'
    }

    payload = request.get_json(force=True)

    if not payload or payload == {}:
        return jsonify({"error": "No data sent"})

    data['adjustment_threshold'] = payload['threshold']
    data['parties'] = get_parties(payload['data'])
    for k, v in payload['data'].items():
        c = v['response']['constituency']
        data['constituency_names'].append(c['identifier'])
        data['constituency_seats'].append(c['seats'])
        data['constituency_adjustment_seats'].append(c['equalizerseats'])
        parties = {pv['letter']:pv for pv in v['response']['results']['list']}

        votes = [parties[p]['votes'] if p in parties else 0 for p in data['parties']]
        data['votes'].append(votes)

    e = run_script({'election_rules': data, 'action': 'election'})

    if type(e) == dict:        
        return jsonify(e)  
    ruv_data = e.get_results_dict()

    for i, c in enumerate(ruv_data['rules']['constituency_names']):
        for r, v in enumerate(payload['data'][c]['response']['results']['list']):
            print('Kjördæmi: {} - Flokkur: {} - Sæti: {}'.format(
                c,
                v['text'],
                v['seats']+v['equalizerseats']))
            print('Kjördæmi: {} - Flokkur: {} - Sæti: {}'.format(
                c,
                v['text'],
                ruv_data['seat_allocations'][i][r]))
            print('#####################################################################')
            #print(ruv_data['rules']['votes'][i][r])
    #payload['data'][c]['response']['results']['list'][r]['seats'] = ruv_data['seat_allocations'][i][r]
    #return jsonify(e.get_results_dict())    
    return jsonify(payload['data'])

    #return jsonify(ruv_data)
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
