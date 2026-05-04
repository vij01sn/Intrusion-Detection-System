import os
from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

model = pickle.load(open("model/model.pkl","rb"))
label_encoder = pickle.load(open("model/label_encoder.pkl","rb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():

    duration = float(request.form['duration'])
    src_bytes = float(request.form['src_bytes'])
    dst_bytes = float(request.form['dst_bytes'])

    # The model expects 41 features. We have 3, so we pad with 38 zeros.
    features = np.array([[duration, src_bytes, dst_bytes] + [0] * 38])

    pred = model.predict(features)
    attack_type = label_encoder.inverse_transform(pred)[0]

    if attack_type.lower() == 'normal':
        result = "✅ Normal Traffic"
    else:
        result = f"⚠️ Attack Detected: {attack_type.upper()}"

    return render_template("index.html", prediction_text=result)

@app.route('/eda')
def eda():
    return render_template("eda_report.html")

@app.route('/graph')
def graph():
    return render_template("graph.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
    