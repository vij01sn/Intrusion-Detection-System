import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless environments
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
import sys
import json

print("Loading dataset...")
try:
    df = pd.read_csv("KDDTrain+.txt", header=None).sample(n=10000, random_state=42)
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

df.columns = [str(i) for i in df.columns]

# ── Helpers ──────────────────────────────────────────────────────────────────

def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def make_card(title, content_html):
    return f"""
    <div class="card">
        <h2>{title}</h2>
        {content_html}
    </div>"""


# ── Overview ─────────────────────────────────────────────────────────────────

num_rows, num_cols = df.shape
num_numeric = df.select_dtypes(include="number").shape[1]
num_categorical = df.select_dtypes(exclude="number").shape[1]
missing_total = df.isnull().sum().sum()
duplicate_rows = df.duplicated().sum()

overview_html = f"""
<table>
  <tr><td>Rows</td><td><strong>{num_rows:,}</strong></td></tr>
  <tr><td>Columns</td><td><strong>{num_cols}</strong></td></tr>
  <tr><td>Numeric columns</td><td><strong>{num_numeric}</strong></td></tr>
  <tr><td>Categorical columns</td><td><strong>{num_categorical}</strong></td></tr>
  <tr><td>Missing values</td><td><strong>{missing_total:,}</strong></td></tr>
  <tr><td>Duplicate rows</td><td><strong>{duplicate_rows:,}</strong></td></tr>
</table>"""

# ── Descriptive Statistics ────────────────────────────────────────────────────

desc = df.describe(include="all").T.reset_index().rename(columns={"index": "Column"})
desc_html = desc.to_html(classes="data-table", border=0, index=False, na_rep="-")

# ── Missing Values Bar Chart ──────────────────────────────────────────────────

missing = df.isnull().sum()
missing = missing[missing > 0]
if not missing.empty:
    fig, ax = plt.subplots(figsize=(10, max(3, len(missing) * 0.4)))
    missing.sort_values().plot(kind="barh", ax=ax, color="#6366f1")
    ax.set_title("Missing Values per Column")
    ax.set_xlabel("Count")
    plt.tight_layout()
    missing_chart = f'<img src="data:image/png;base64,{fig_to_b64(fig)}" alt="Missing values chart"/>'
else:
    missing_chart = "<p class='ok'>✅ No missing values found.</p>"

# ── Distribution plots for numeric columns ────────────────────────────────────

numeric_cols = df.select_dtypes(include="number").columns.tolist()
dist_imgs = []
for col in numeric_cols[:15]:   # cap at 15 to keep report fast
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#6366f1", edgecolor="white", linewidth=0.4)
    ax.set_title(f"Distribution: {col}")
    ax.set_xlabel(col)
    ax.set_ylabel("Count")
    plt.tight_layout()
    dist_imgs.append(f'<div class="dist-img"><img src="data:image/png;base64,{fig_to_b64(fig)}" alt="{col} distribution"/></div>')

dist_html = '<div class="dist-grid">' + "".join(dist_imgs) + "</div>"

# ── Correlation Heatmap ───────────────────────────────────────────────────────

if len(numeric_cols) >= 2:
    corr = df[numeric_cols[:20]].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=False, cmap="coolwarm", center=0, ax=ax,
                linewidths=0.3, linecolor="#1e1e2e")
    ax.set_title("Correlation Heatmap (first 20 numeric columns)")
    plt.tight_layout()
    corr_html = f'<img src="data:image/png;base64,{fig_to_b64(fig)}" alt="Correlation heatmap"/>'
else:
    corr_html = "<p>Not enough numeric columns for a heatmap.</p>"

# ── Categorical value counts ──────────────────────────────────────────────────

cat_cols = df.select_dtypes(exclude="number").columns.tolist()
cat_imgs = []
for col in cat_cols[:10]:
    vc = df[col].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(6, max(3, len(vc) * 0.35)))
    vc.plot(kind="barh", ax=ax, color="#f43f5e")
    ax.set_title(f"Value Counts: {col}")
    ax.invert_yaxis()
    plt.tight_layout()
    cat_imgs.append(f'<div class="dist-img"><img src="data:image/png;base64,{fig_to_b64(fig)}" alt="{col} value counts"/></div>')

cat_html = '<div class="dist-grid">' + "".join(cat_imgs) + "</div>" if cat_imgs else "<p>No categorical columns found.</p>"

# ── Assemble HTML ─────────────────────────────────────────────────────────────

cards = "".join([
    make_card("📊 Dataset Overview", overview_html),
    make_card("📋 Descriptive Statistics", desc_html),
    make_card("❓ Missing Values", missing_chart),
    make_card("📈 Numeric Distributions", dist_html),
    make_card("🔥 Correlation Heatmap", corr_html),
    make_card("🏷️ Categorical Columns", cat_html),
])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Network Data – EDA Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', sans-serif;
    background: #0f0f1a;
    color: #e2e2f0;
    min-height: 100vh;
    padding: 2rem 1rem;
  }}
  header {{
    text-align: center;
    margin-bottom: 2.5rem;
  }}
  header h1 {{
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}
  header p {{ color: #888; margin-top: 0.4rem; }}
  .card {{
    background: #16162a;
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 2rem;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 4px 30px rgba(99,102,241,0.08);
  }}
  .card h2 {{
    font-size: 1.2rem;
    font-weight: 600;
    color: #a5b4fc;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid #2a2a4a;
    padding-bottom: 0.7rem;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  th, td {{
    padding: 0.55rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid #1e1e36;
  }}
  th {{ color: #a5b4fc; font-weight: 600; background: #1a1a30; }}
  tr:hover td {{ background: #1e1e36; }}
  img {{ max-width: 100%; border-radius: 10px; display: block; }}
  .dist-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    margin-top: 0.5rem;
  }}
  .dist-img img {{ width: 100%; }}
  .ok {{ color: #4ade80; font-weight: 600; }}
  .data-table {{ font-size: 0.78rem; }}
</style>
</head>
<body>
<header>
  <h1>🛡️ Network Data – EDA Report</h1>
  <p>Exploratory Data Analysis · {num_rows:,} rows sampled · {num_cols} columns</p>
</header>
{cards}
</body>
</html>"""

print("Writing report...")
try:
    with open("templates/eda_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Successfully generated templates/eda_report.html")
except Exception as e:
    print(f"Error writing report: {e}")
    sys.exit(1)
