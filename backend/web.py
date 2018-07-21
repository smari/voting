from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
from voting import run_script, get_capabilities_dict
import voting
import os.path

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask('voting',
            template_folder=os.path.abspath('../vue-frontend/'),
            static_folder=os.path.abspath('../vue-frontend/static/'))

CORS(app)

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static/', path)

@app.route('/api/election/', methods=["POST"])
def handle_election():
    data = request.get_json(force=True)

    rules = voting.ElectionRules()

    for k, v in data["rules"].iteritems():
        rules[k] = v

    rules["constituency_names"] = data["constituency_names"]
    rules["parties"] = data["parties"]
    rules["constituency_seats"] = data["constituency_seats"]
    rules["constituency_adjustment_seats"] = data["constituency_adjustment_seats"]

    if not all([data[x] for x in ["constituency_names", "constituency_seats", "parties", "constituency_adjustment_seats"]]):
        return jsonify({"error": "missing data"})

    print("----- Rules -----")
    rules.pretty_print()

    election = voting.Election(rules, data["votes"])
    try:
        election.run()
    except ZeroDivisionError, e:
        return jsonify({"error": "Need to have more votes."})
    return jsonify(election.get_results_dict())


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

@app.route('/api/presets/', methods=["GET"])
def get_presets():
    return jsonify(get_presets_dict())


if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
