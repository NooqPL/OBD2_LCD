from flask import Flask, jsonify, render_template
from ..data_model import data

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api")
def api():
    return jsonify(data)

def start_web():
    app.run(host="0.0.0.0", port=5000)
