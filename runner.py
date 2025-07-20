import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from interpreter import runner

app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    code = data.get("code", "")
    result = runner(code)
    return jsonify({"output": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

