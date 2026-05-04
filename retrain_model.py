"""
retrain_model.py — Re-saves the model using joblib so it loads cleanly
on any scikit-learn >= 1.3 without pickle protocol mismatch errors.

Run once locally:  .venv/bin/python retrain_model.py
Then commit the updated model/ files.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

COLUMNS = [
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
    'dst_host_rerror_rate','dst_host_srv_rerror_rate','label','difficulty'
]

def map_attack(label):
    if label == "normal":
        return "normal"
    elif label in ["neptune","smurf","pod","teardrop","land","back"]:
        return "DoS"
    elif label in ["satan","ipsweep","portsweep","nmap"]:
        return "Probe"
    elif label in ["guess_passwd","ftp_write","imap","phf","multihop","warezmaster"]:
        return "R2L"
    else:
        return "U2R"

print("Loading dataset...")
df = pd.read_csv("KDDTrain+.txt", names=COLUMNS)
df.drop(['difficulty'], axis=1, inplace=True)
df['label'] = df['label'].apply(map_attack)

# Encode categorical columns
cat_cols = ['protocol_type', 'service', 'flag']
encoders = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['label'])
X = df.drop(['label'], axis=1)

print("Training model (n_estimators=100 for speed)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.4f}")

os.makedirs("model", exist_ok=True)
joblib.dump(model,         "model/model.joblib")
joblib.dump(label_encoder, "model/label_encoder.joblib")
joblib.dump(encoders,      "model/encoders.joblib")
print("✅ Saved: model/model.joblib, model/label_encoder.joblib, model/encoders.joblib")
