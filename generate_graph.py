import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

print("Loading dataset...")
df = pd.read_csv("KDDTrain+.txt", header=None)

# NSL-KDD typically has 43 columns, where index 41 is the attack label
label_col_index = 41 if len(df.columns) > 41 else len(df.columns) - 1
df.rename(columns={df.columns[label_col_index]: 'label'}, inplace=True)

# Create a binary column: "normal" vs "attack"
df['traffic_type'] = df['label'].apply(lambda x: 'Normal Traffic' if x == 'normal' else 'Cyber Attack')

print("Applying styling and generating graph...")

# Set dark theme to perfectly match the dashboard
sns.set_theme(style="darkgrid", rc={
    "axes.facecolor": "none", 
    "figure.facecolor": "none", 
    "grid.color": "#1e293b", 
    "text.color": "#f8fafc", 
    "axes.labelcolor": "#f8fafc", 
    "xtick.color": "#94a3b8", 
    "ytick.color": "#94a3b8"
})

# Create a figure with 2 subplots side-by-side
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Subplot 1: Normal vs Attack
sns.countplot(x='traffic_type', data=df, palette=['#10b981', '#f43f5e'], ax=axes[0], order=['Normal Traffic', 'Cyber Attack'])
axes[0].set_title("Overall Traffic Breakdown", fontsize=20, pad=20, fontweight='bold', color='white')
axes[0].set_xlabel("Traffic Category", fontsize=16, labelpad=15)
axes[0].set_ylabel("Total Connections", fontsize=16, labelpad=15)
axes[0].tick_params(axis='x', labelsize=14)
axes[0].tick_params(axis='y', labelsize=14)

# Add data labels to Subplot 1
for p in axes[0].patches:
    axes[0].annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=14, color='white', xytext=(0, 10), textcoords='offset points')

# Subplot 2: Top 10 Attack Types (excluding Normal)
attack_df = df[df['traffic_type'] == 'Cyber Attack']
top_attacks = attack_df['label'].value_counts().head(10).index
sns.countplot(x='label', data=attack_df, order=top_attacks, palette='cool', ax=axes[1])
axes[1].set_title("Top 10 Most Frequent Attacks", fontsize=20, pad=20, fontweight='bold', color='white')
axes[1].set_xlabel("Specific Attack Signature", fontsize=16, labelpad=15)
axes[1].set_ylabel("Number of Connections", fontsize=16, labelpad=15)
axes[1].tick_params(axis='x', labelsize=14, rotation=45)
axes[1].tick_params(axis='y', labelsize=14)

# Add data labels to Subplot 2
for p in axes[1].patches:
    axes[1].annotate(f'{int(p.get_height()):,}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', fontsize=12, color='white', xytext=(0, 10), textcoords='offset points')

# Ensure everything fits perfectly
plt.tight_layout()

# Save the plot
os.makedirs("static/plots", exist_ok=True)
plt.savefig("static/plots/attack_distribution.svg", bbox_inches='tight', transparent=True)

print("Saved incredibly clear and beautiful graph to static/plots/attack_distribution.svg")
