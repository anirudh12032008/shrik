from flask import Flask, request, jsonify
from interpreter import runner
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    code = data.get("code", "")
    result = runner(code)
    return jsonify({"output": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
