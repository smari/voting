from flask import Flask, render_template, send_from_directory, request, jsonify
from voting import run_script, get_capabilities_dict
import os.path

app = Flask('voting',
            template_folder=os.path.abspath('../frontend/'),
            static_folder=os.path.abspath('../frontend/static/'))

@app.route('/')
def serve_index():
    return render_template('index.html')

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
