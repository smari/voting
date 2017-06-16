from flask import Flask, render_template, send_from_directory, request, jsonify
from voting import run_script
app = Flask('voting')

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/api/', methods=["POST"])
def handle_api():
    script = request.get_json(force=True)
    if not script or script == {}:
        return jsonify({"error": "No script sent"})
    e = run_script(script)
    return jsonify(e.get_results_dict())

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
