from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import threading
import random
import os.path
from voting import run_script, get_capabilities_dict, get_presets_dict
import voting
import simulate as sim

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

    for k, v in data["rules"].items():
        rules[k] = v

    for x in ["constituency_names", "constituency_seats", "parties", "constituency_adjustment_seats"]:
        if x in data and data[x]:
            rules[x] = data[x]
        else:
            return jsonify({"error": "Missing data ('%s')" % x})

    if not "votes" in data:
        return jsonify({"error": "Votes missing."})

    for const in data["votes"]:
        for party in const:
            if type(party) != int:
                return jsonify({"error": "Votes must be numbers."})

    try:
        election = voting.Election(rules, data["votes"])
        election.run()
    except ZeroDivisionError:
        return jsonify({"error": "Need to have more votes."})
    except AssertionError:
        return jsonify({"error": "The data is malformed."})
    return jsonify(election.get_results_dict())


SIMULATIONS = {}
SIMULATION_IDX = 0

def run_simulation(sid):
    SIMULATIONS[sid][1].done = False
    print("Starting thread %x" % sid)
    SIMULATIONS[sid][0].simulate()
    print("Ending thread %x" % sid)
    SIMULATIONS[sid][1].done = True


@app.route('/api/simulate/', methods=['POST'])
def start_simulation():
    SIMULATION_IDX += 1
    h = sha256()
    h.update(SIMULATION_IDX + ":" + random.randint(1, 100000000))
    sid = h.hexdigest()
    thread = threading.Thread(target=run_simulation, args=(sid))

    success, simulation = set_up_simulation()
    if not success:
        return jsonify({"started": False, "error": simulation})

    SIMULATIONS[sid] = [simulation, thread]

    thread.start()
    return jsonify({"started": True, "sid": sid})


@app.route('/api/simulate/check/', methods=['GET'])
def check_simulation():
    data = request.get_json(force=True)
    if "sid" not in data:
        return jsonify({"error": "Please supply a SID."})
    if data["sid"] not in SIMULATIONS:
        return jsonify({"error": "Please supply a valid SID."})
    simulation, thread = SIMULATIONS[data["sid"]]
    if thread.done:
        del(SIMULATIONS[data["sid"]])

    return jsonify({
            "done": thread.done,
            "iter": simulation.iterations,
            "target": sim.rules["simulation_count"],
            "results": sim.get_results_dict()
        })


def set_up_simulation():
    data = request.get_json(force=True)
    election_rules = voting.ElectionRules()

    for k, v in data["election_rules"].items():
        election_rules[k] = v

    for x in ["constituency_names", "constituency_seats", "parties", "constituency_adjustment_seats"]:
        if x in data and data[x]:
            election_rules[x] = data[x]
        else:
            return False, "Missing data ('%s')" % x

    if not "ref_votes" in data:
        return False, "Votes missing."

    for const in data["ref_votes"]:
        for party in const:
            if type(party) != int:
                return False, "Votes must be numbers."

    simulation_rules = sim.SimulationRules()

    for k, v in data["simulation_rules"].items():
        simulation_rules[k] = v

    try:
        election = voting.Election(election_rules, data["ref_votes"])
        simulation = sim.Simulation(simulation_rules, election)
    except ZeroDivisionError:
        return False, "Need to have more votes."

    return True, simulation


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
