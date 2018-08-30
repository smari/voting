from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import threading
import random
import os.path
import voting
import tempfile
import simulate as sim
from hashlib import sha256
import json
import util
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv

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


@app.route('/api/votes/upload/', methods=['POST'])
def upload_votes():
    if 'file' not in request.files:
        return jsonify({'error': 'must upload a file.'})
    f = request.files['file']
    res = util.load_votes_from_stream(f.stream, f.filename)
    return jsonify(res)

@app.route('/api/votes/paste/', methods=['POST'])
def paste_votes():
    data = request.get_json(force=True)

    if "csv" not in data:
        return jsonify({'error': 'must provide csv'})

    rd = []
    for row in csv.reader(StringIO(data["csv"]), skipinitialspace=True):
        rd.append(row)

    res = {}
    if data["has_parties"]:
        res["parties"] = rd[0]
        del(rd[0])

    if data["has_constituencies"]:
        res["constituencies"] = [row[0] for row in rd]
        for row in rd: del(row[0])
        if data["has_parties"]: res["parties"] = res["parties"][1:]

    if data["has_constituency_seats"]:
        res["constituency_seats"] = [row[0] for row in rd]
        for row in rd: del(row[0])
        if data["has_parties"]: res["parties"] = res["parties"][1:]

    if data["has_constituency_adjustment_seats"]:
        res["constituency_adjustment_seats"] = [row[0] for row in rd]
        for row in rd: del(row[0])
        if data["has_parties"]: res["parties"] = res["parties"][1:]

    res["votes"] = rd

    return jsonify(res)


SIMULATIONS = {}
SIMULATION_IDX = 0

def run_simulation(sid):
    global SIMULATIONS
    SIMULATIONS[sid][1].done = False
    print("Starting thread %s" % sid)
    SIMULATIONS[sid][0].simulate()
    print("Ending thread %s" % sid)
    SIMULATIONS[sid][1].done = True


@app.route('/api/simulate/', methods=['POST'])
def start_simulation():
    global SIMULATIONS
    global SIMULATION_IDX

    SIMULATION_IDX += 1

    h = sha256()
    sidbytes = (str(SIMULATION_IDX) + ":" + str(random.randint(1, 100000000))).encode('utf-8')
    h.update(sidbytes)
    sid = h.hexdigest()
    thread = threading.Thread(target=run_simulation, args=(sid,))

    success, simulation = set_up_simulation()
    if not success:
        return jsonify({"started": False, "error": simulation})

    SIMULATIONS[sid] = [simulation, thread]

    thread.start()
    return jsonify({"started": True, "sid": sid})


@app.route('/api/simulate/check/', methods=['GET', 'POST'])
def check_simulation():
    data = request.get_json(force=True)
    if "sid" not in data:
        return jsonify({"error": "Please supply a SID."})
    if data["sid"] not in SIMULATIONS:
        return jsonify({"error": "Please supply a valid SID."})
    simulation, thread = SIMULATIONS[data["sid"]]
    #if thread.done:
    #    del(SIMULATIONS[data["sid"]])

    return jsonify({
            "done": thread.done,
            "iteration": simulation.iteration,
            "iteration_time": simulation.iteration_time.seconds + (simulation.iteration_time.microseconds/1000000.0),
            "target": simulation.sim_rules["simulation_count"],
            "results": simulation.get_results_dict()
        })

@app.route('/api/simulate/stop/', methods=['GET', 'POST'])
def stop_simulation():
    data = request.get_json(force=True)
    if "sid" not in data:
        return jsonify({"error": "Please supply a SID."})
    if data["sid"] not in SIMULATIONS:
        return jsonify({"error": "Please supply a valid SID."})
    simulation, thread = SIMULATIONS[data["sid"]]

    simulation.terminate = True
    thread.join()
    #if thread.done:
    #    del(SIMULATIONS[data["sid"]])

    return jsonify({
            "done": thread.done,
            "iteration": simulation.iteration,
            "target": simulation.sim_rules["simulation_count"],
            "results": simulation.get_results_dict()
        })


@app.route('/api/simulate/getxlsx/', methods=['GET'])
def get_xlsx():
    if "sid" not in request.args:
        return jsonify({'error': 'Please supply a SID.'})
    if request.args["sid"] not in SIMULATIONS:
        return jsonify({"error": "Please supply a valid SID."})

    tmpfilename = tempfile.mktemp(prefix='votesim-%s-' % request.args["sid"][:6])
    simulation, thread = SIMULATIONS[request.args["sid"]]
    util.simulation_to_xlsx(simulation, tmpfilename)
    print("%s" % (tmpfilename))
    return send_from_directory(directory='/tmp', filename=tmpfilename.split("/")[-1], attachment_filename="simulation.xlsx", as_attachment=True)


def set_up_simulation():
    data = request.get_json(force=True)
    rulesets = []

    for rs in data["election_rules"]:
        election_rules = voting.ElectionRules()

        print(data["election_rules"])
        print(rs)
        for k, v in rs.items():
            print("Setting election_rules[%s] = %s" % (k, v))
            election_rules[k] = v

        for x in ["constituency_names", "constituency_seats", "parties", "constituency_adjustment_seats"]:
            if x in data and data[x]:
                election_rules[x] = data[x]
            else:
                return False, "Missing data ('%s')" % x

        rulesets.append(election_rules)

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
        simulation = sim.Simulation(simulation_rules, rulesets, data["ref_votes"])
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


def get_capabilities_dict():
    return {
        "election_rules": voting.ElectionRules(),
        "simulation_rules": sim.SimulationRules(),
        "capabilities": {
            "divider_rules": voting.DIVIDER_RULE_NAMES,
            "adjustment_methods": voting.ADJUSTMENT_METHOD_NAMES,
            "generating_methods": sim.GENERATING_METHOD_NAMES
        },
    }

def get_presets_dict():
    from os import listdir
    from os.path import isfile, join
    presetsdir = "../data/presets/"
    try:
        files = [f for f in listdir(presetsdir) if isfile(join(presetsdir, f))
                 and f.endswith('.json')]
    except Exception as e:
        print("Presets directory read failure: %s" % (e))
        files = []
    pr = []
    for f in files:
        try:
            with open(presetsdir+f) as json_file:
                data = json.load(json_file)
        except  json.decoder.JSONDecodeError:
            data = {'error': 'Problem parsing json, please fix "{}"'.format(
                presetsdir+f)}
        pr.append(data)
    return pr

def run_script(rules):
    if type(rules) in ["str", "unicode"]:
        with open(rules, "r") as read_file:
            rules = json.load(read_file)

    if type(rules) != dict:
        return {"error": "Incorrect script format."}

    if rules["action"] not in ["simulation", "election"]:
        return {"error": "Script action must be election or simulation."}

    if rules["action"] == "election":
        return voting.run_script_election(rules)

    else:
        return sim.run_script_simulation(rules)


if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
