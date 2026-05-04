import pandas as pd
from ydata_profiling import ProfileReport
import sys

print("Loading dataset...")
# Load a sample to keep generation fast
try:
    df = pd.read_csv("KDDTrain+.txt", header=None).sample(n=10000, random_state=42)
except Exception as e:
    print(f"Error loading data: {e}")
    sys.exit(1)

print("Generating EDA report...")
try:
    # Use minimal=True for faster generation, especially on larger datasets
    profile = ProfileReport(df, title="Network Data EDA", minimal=True)
    profile.to_file("templates/eda_report.html")
    print("Successfully generated templates/eda_report.html")
except Exception as e:
    print(f"Error generating report: {e}")
    sys.exit(1)
