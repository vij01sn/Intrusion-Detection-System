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
        import pandas as pd
        duration  = float(request.form['duration'])
        src_bytes = float(request.form['src_bytes'])
        dst_bytes = float(request.form['dst_bytes'])

        # KDD dataset columns (41 features, 'difficulty' dropped)
        FEATURE_COLS = [
            'duration','protocol_type','service','flag','src_bytes','dst_bytes',
            'land','wrong_fragment','urgent','hot','num_failed_logins','logged_in',
            'num_compromised','root_shell','su_attempted','num_root','num_file_creations',
            'num_shells','num_access_files','num_outbound_cmds','is_host_login',
            'is_guest_login','count','srv_count','serror_rate','srv_serror_rate',
            'rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate',
            'srv_diff_host_rate','dst_host_count','dst_host_srv_count',
            'dst_host_same_srv_rate','dst_host_diff_srv_rate',
            'dst_host_same_src_port_rate','dst_host_srv_diff_host_rate',
            'dst_host_serror_rate','dst_host_srv_serror_rate',
            'dst_host_rerror_rate','dst_host_srv_rerror_rate'
        ]
        values = [duration, src_bytes, dst_bytes] + [0] * 38
        features = pd.DataFrame([values], columns=FEATURE_COLS)

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