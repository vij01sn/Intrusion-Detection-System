import os
import logging
from flask import Flask, render_template, request
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Absolute path to the directory containing app.py — works regardless of CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# ── Model loading (joblib preferred, pickle fallback) ─────────────────────────
model = None
label_encoder = None

def _load_models():
    global model, label_encoder
    try:
        import joblib
        jl_model = os.path.join(BASE_DIR, "model", "model.joblib")
        jl_enc   = os.path.join(BASE_DIR, "model", "label_encoder.joblib")
        logger.info(f"Looking for model at: {jl_model}")
        if os.path.exists(jl_model):
            model         = joblib.load(jl_model)
            label_encoder = joblib.load(jl_enc)
            logger.info("✅ Model loaded via joblib")
            return
        else:
            logger.warning(f"joblib model not found at {jl_model}")
    except Exception as e:
        logger.warning(f"joblib load failed: {e}")

    # Fallback: legacy pickle files
    try:
        import pickle
        pkl_model = os.path.join(BASE_DIR, "model", "model.pkl")
        pkl_enc   = os.path.join(BASE_DIR, "model", "label_encoder.pkl")
        logger.info(f"Trying pickle fallback at: {pkl_model}")
        with open(pkl_model, "rb") as f:
            model = pickle.load(f)
        with open(pkl_enc, "rb") as f:
            label_encoder = pickle.load(f)
        logger.info("✅ Model loaded via pickle (legacy)")
    except Exception as e:
        logger.error(f"❌ All model loading attempts failed: {e}")

_load_models()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/health')
def health():
    status = "ok" if model is not None else "model_load_failed"
    code   = 200 if model is not None else 503
    return {"status": status}, code


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template("index.html",
                               prediction_text="⚠️ Model not loaded. Check server logs.")
    try:
        duration  = float(request.form['duration'])
        src_bytes = float(request.form['src_bytes'])
        dst_bytes = float(request.form['dst_bytes'])

        # Model trained on 41 features; pad the remaining 38 with zeros
        features = np.array([[duration, src_bytes, dst_bytes] + [0] * 38])

        pred        = model.predict(features)
        attack_type = label_encoder.inverse_transform(pred)[0]

        if attack_type.lower() == 'normal':
            result = "✅ Normal Traffic"
        else:
            result = f"⚠️ Attack Detected: {attack_type.upper()}"

        return render_template("index.html", prediction_text=result)

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return render_template("index.html",
                               prediction_text=f"❌ Prediction error: {e}")


@app.route('/eda')
def eda():
    if os.path.exists(os.path.join(app.template_folder, 'eda_report.html')):
        return render_template("eda_report.html")
    return ("<h2 style='font-family:sans-serif;text-align:center;margin-top:50px'>"
            "EDA report not generated yet. Run generate_eda.py locally first.</h2>")


@app.route('/graph')
def graph():
    return render_template("graph.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)