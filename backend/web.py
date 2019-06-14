from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import threading
import random
import os.path
import tempfile
from datetime import datetime, timedelta
from hashlib import sha256
import json
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv

import dictionaries
from electionRules import ElectionRules
import util
from excel_util import save_votes_to_xlsx
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

DOWNLOADS = {}
DOWNLOADS_IDX = 0
def get_new_download_id():
    global DOWNLOADS_IDX
    did = DOWNLOADS_IDX = DOWNLOADS_IDX + 1

    h = sha256()
    didbytes = (str(did) + ":" + str(random.randint(1, 100000000))).encode('utf-8')
    h.update(didbytes)
    return h.hexdigest()

@app.route('/api/downloads/get/', methods=['GET'])
def get_download():
    global DOWNLOADS
    if "id" not in request.args:
        return jsonify({'error': 'Please supply a download id.'})
    if request.args["id"] not in DOWNLOADS:
        return jsonify({"error": "Please supply a valid download id."})
    tmpfilename, attachment_filename = DOWNLOADS[request.args["id"]]

    return send_from_directory(
        directory=os.path.dirname(tmpfilename),
        filename=os.path.basename(tmpfilename),
        attachment_filename=attachment_filename,
        as_attachment=True
    )

def handle_election():
    data = request.get_json(force=True)
    rules = ElectionRules()

    for section in ["vote_table", "rules"]:
        if section not in data or not data[section]:
            return {"error": f"Missing data ('{section}')"}

    vote_table = data["vote_table"]

    for k, v in data["rules"].items():
        rules[k] = v

    for x in ["constituency_names", "constituency_seats", "parties", "constituency_adjustment_seats"]:
        if x in vote_table and vote_table[x]:
            rules[x] = vote_table[x]
        else:
            return {"error": "Missing data ('%s')" % x}

    if not "votes" in vote_table:
        return {"error": "Votes missing."}

    for const in vote_table["votes"]:
        for party in const:
            if type(party) != int:
                return {"error": "Votes must be numbers."}

    try:
        election = voting.Election(rules, vote_table["votes"])
        election.run()
    except ZeroDivisionError:
        return {"error": "Need to have more votes."}
    except AssertionError:
        return {"error": "The data is malformed."}

    return election

@app.route('/api/election/', methods=["POST"])
def get_election_results():
    election = handle_election()
    if type(election)==dict and "error" in election:
        return jsonify(election)

    return jsonify(election.get_results_dict())

@app.route('/api/election/getxlsx/', methods=['POST'])
def get_election_excel():
    global DOWNLOADS
    did = get_new_download_id()

    election = handle_election()
    if type(election)==dict and "error" in election:
        return jsonify(election)

    tmpfilename = tempfile.mktemp(prefix='election-')
    election.to_xlsx(tmpfilename)
    attachment_filename=f"election {datetime.now().strftime('%Y.%m.%d %H.%M.%S')}.xlsx"
    DOWNLOADS[did] = tmpfilename, attachment_filename
    return jsonify({"download_id": did})

@app.route('/api/votes/save/', methods=['POST'])
def save_votes():
    global DOWNLOADS
    did = get_new_download_id()
    DOWNLOADS[did] = prepare_to_save_vote_table()
    return jsonify({"download_id": did})

def prepare_to_save_vote_table():
    data = request.get_json(force=True)
    if "vote_table" not in data or not data["vote_table"]:
        return False, f"Missing data (vote_table)"
    vote_table = data["vote_table"]
    for info in [
        "name",
        "votes",
        "parties",
        "constituency_names",
        "constituency_seats",
        "constituency_adjustment_seats"
    ]:
        if info not in vote_table or not vote_table[info]:
            return False, f"Missing data ('{info}')"

    num_constituencies = len(vote_table["votes"])
    num_parties = len(vote_table["parties"])
    assert(num_constituencies == len(vote_table["constituency_names"]))
    assert(num_constituencies == len(vote_table["constituency_seats"]))
    assert(num_constituencies == len(vote_table["constituency_adjustment_seats"]))
    assert(all([num_parties == len(row) for row in vote_table["votes"]]))
    file_matrix = [
        [vote_table["name"], "cons", "adj"] + vote_table["parties"],
    ] + [
        [
            vote_table["constituency_names"][c],
            vote_table["constituency_seats"][c],
            vote_table["constituency_adjustment_seats"][c],
        ] + vote_table["votes"][c]
        for c in range(num_constituencies)
    ]

    tmpfilename = tempfile.mktemp(prefix='vote_table-')
    save_votes_to_xlsx(file_matrix, tmpfilename)
    filename = secure_filename(vote_table['name'])
    attachment_filename=f"{filename}.xlsx"

    return tmpfilename, attachment_filename

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

    return jsonify(util.parse_input(
        input=rd,
        name_included=data["has_name"],
        parties_included=data["has_parties"],
        const_included=data["has_constituencies"],
        const_seats_included=data["has_constituency_seats"],
        adj_seats_included=data["has_constituency_adjustment_seats"]
    ))


SIMULATIONS = {}
SIMULATION_IDX = 0

def run_simulation(sid):
    global SIMULATIONS
    SIMULATIONS[sid][1].done = False
    print("Starting thread %s" % sid)
    SIMULATIONS[sid][0].simulate()
    print("Ending thread %s" % sid)
    SIMULATIONS[sid][1].done = True


def cleanup_expired_simulations():
    global SIMULATIONS
    global SIMULATION_IDX
    try:
        for sid, sim in list(SIMULATIONS.items()):
            if sim[2] < datetime.now():
                del(SIMULATIONS[sid])
    except RuntimeError:
        pass

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
        print(simulation)
        return jsonify({"started": False, "error": simulation})

    # Simulation cache expires in 3 hours = 3*3600 = 10800 seconds
    expires = datetime.now() + timedelta(seconds=10800)
    SIMULATIONS[sid] = [simulation, thread, expires]

    # Whenever we start a new simulation, we'll clean up any expired
    #   simulations first:
    cleanup_expired_simulations()

    thread.start()
    return jsonify({"started": True, "sid": sid})


@app.route('/api/simulate/check/', methods=['GET', 'POST'])
def check_simulation():
    data = request.get_json(force=True)
    if "sid" not in data:
        return jsonify({"error": "Please supply a SID."})
    if data["sid"] not in SIMULATIONS:
        return jsonify({"error": "Please supply a valid SID."})
    simulation, thread, expiry = SIMULATIONS[data["sid"]]
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
    simulation, thread, expiry = SIMULATIONS[data["sid"]]

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
    simulation, thread, expiry = SIMULATIONS[request.args["sid"]]
    simulation.to_xlsx(tmpfilename)
    print("%s" % (tmpfilename))
    return send_from_directory(
        directory=os.path.dirname(tmpfilename),
        filename=os.path.basename(tmpfilename),
        attachment_filename=
            f"simulation {datetime.now().strftime('%Y.%m.%d %H.%M.%S')}.xlsx",
        as_attachment=True
    )


def set_up_simulation():
    data = request.get_json(force=True)
    rulesets = []

    for section in ["vote_table", "election_rules", "simulation_rules"]:
        if section not in data or not data[section]:
            return False, f"Missing data ('{section}')"

    vote_table = data["vote_table"]

    for info in [
        "name",
        "votes",
        "parties",
        "constituency_names",
        "constituency_seats",
        "constituency_adjustment_seats"
    ]:
        if info not in vote_table or not vote_table[info]:
            return False, f"Missing data ('{info}')"

    for rs in data["election_rules"]:
        election_rules = ElectionRules()

        print(data["election_rules"])
        print(rs)
        for k, v in rs.items():
            print("Setting election_rules[%s] = %s" % (k, v))
            election_rules[k] = v

        for info in ["parties", "constituency_names"]:
            election_rules[info] = vote_table[info]

        for info in ["constituency_seats", "constituency_adjustment_seats"]:
            if info in rs and rs[info]:
                election_rules[info] = rs[info]
            else:
                election_rules[info] = vote_table[info]

            for c in range(len(election_rules[info])):
                if not election_rules[info][c]:
                    election_rules[info][c]=0
                if type(election_rules[info][c]) != int:
                    return False, "Seat specifications must be numbers."

        rulesets.append(election_rules)

    table_name = vote_table["name"]
    votes = vote_table["votes"]

    for c in range(len(votes)):
        for p in range(len(votes[c])):
            if not votes[c][p]:
                votes[c][p] = 0
            if type(votes[c][p]) != int:
                return False, "Votes must be numbers."

    stability_parameter = 100
    if "stbl_param" in data:
        stability_parameter = data["stbl_param"]
        if stability_parameter <= 1:
            return False, "Stability parameter must be greater than 1."

    simulation_rules = sim.SimulationRules()
    for k, v in data["simulation_rules"].items():
        simulation_rules[k] = v

    try:
        simulation = sim.Simulation(
            simulation_rules, rulesets, votes, table_name,
            stability_parameter)
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
def get_presets_list():
    return jsonify(get_presets_dict())

@app.route('/api/presets/load/', methods=['POST'])
def get_preset():
    qv = request.get_json(force=True)
    if 'eid' not in qv:
        return jsonify({'error': 'Must supply eid'})
    prs = get_presets_dict()
    # TODO: This is silly but it paves the way to a real database
    for p in prs:
        if p['id'] == qv['eid']:
            res = util.load_votes_from_stream(open('../data/elections/%s' % p['filename'], "r"), p['filename'])
            return jsonify(res)


def get_capabilities_dict():
    return {
        "election_rules": ElectionRules(),
        "simulation_rules": sim.SimulationRules(),
        "capabilities": {
            "divider_rules": dictionaries.DIVIDER_RULE_NAMES,
            "adjustment_methods": dictionaries.ADJUSTMENT_METHOD_NAMES,
            "generating_methods": dictionaries.GENERATING_METHOD_NAMES
        },
    }

def get_presets_dict():
    from os import listdir
    from os.path import isfile, join

    try:
        with open('../data/presets.json', encoding='utf-8') as js:
            data = json.load(js)
    except IOError:
        data = {'error': 'Could not load presets: database lost.'}
    #except json.decoder.JSONDecodeError:
    #    data = {'error': 'Could not load presets due to parse error.'}

    return data
    # presetsdir = "../data/presets/"
    # try:
    #     files = [f for f in listdir(presetsdir) if isfile(join(presetsdir, f))
    #              and f.endswith('.json')]
    # except Exception as e:
    #     print("Presets directory read failure: %s" % (e))
    #     files = []
    # pr = []
    # for f in files:
    #     try:
    #         with open(presetsdir+f) as json_file:
    #             data = json.load(json_file)
    #     except  json.decoder.JSONDecodeError:
    #         data = {'error': 'Problem parsing json, please fix "{}"'.format(
    #             presetsdir+f)}
    #     pr.append(data)
    # return pr

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
