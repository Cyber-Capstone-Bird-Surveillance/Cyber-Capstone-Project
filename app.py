from flask import Flask
from flask import render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd

# from flask_restful import 
app = Flask(__name__)
CORS(app)

uploads = "uploads"
os.makedirs(uploads, exist_ok=True)
app.config["Upload Folder"] = uploads

@app.route('/', methods=["POST"])
def home():
    return render_template("LandingPage.html")

if __name__ == '__main__': 
    app.run(debug=True, port=5001)