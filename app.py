import os
from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)

try:
    model = pickle.load(open("model/model.pkl", "rb"))
    label_encoder = pickle.load(open("model/label_encoder.pkl", "rb"))
    print("✅ Model loaded successfully")
except Exception as e:
    model = None
    label_encoder = None
    print(f"❌ Model loading failed: {e}")

@app.route('/health')
def health():
    status = "ok" if model is not None else "model_load_failed"
    return {"status": status}, 200

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template("index.html", prediction_text="⚠️ Model not loaded. Check server logs.")

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
    import os
    if os.path.exists(os.path.join(app.template_folder, 'eda_report.html')):
        return render_template("eda_report.html")
    return "<h2 style='font-family:sans-serif;text-align:center;margin-top:50px'>EDA report not generated yet. Run generate_eda.py locally first.</h2>"

@app.route('/graph')
def graph():
    return render_template("graph.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
    