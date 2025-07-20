from flask import Flask, request, jsonify, render_template
from interpreter import runner
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    code = request.get_json().get("code", "")
    try:
        output = runner(code)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"[Error: {e}]"})
