import code
import os
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
    inputs = request.get_json().get("inputs", [])
    try:
        output = runner(code, inputs)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"[Error: {e}]"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
