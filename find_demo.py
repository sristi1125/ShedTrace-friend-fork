"""
One-off script: find the best demo address — oldest active shed
with the most violations/complaints, so we have a dramatic example.
"""

import pandas as pd
from pipeline import (
    load_data, SHED_BIN_COL, SHED_ISSUE_COL,
    SHED_HOUSE_COL, SHED_STREET_COL,
    get_violations, get_complaints,
)
from datetime import datetime

sheds, violations, complaints = load_data()

sheds["_issue_date"] = pd.to_datetime(sheds[SHED_ISSUE_COL], errors="coerce")
sheds["_duration_days"] = (datetime.now() - sheds["_issue_date"]).dt.days

# sort oldest sheds first
candidates = sheds.sort_values("_duration_days", ascending=False).head(30)

results = []
for _, row in candidates.iterrows():
    bin_number = row[SHED_BIN_COL]
    v = get_violations(violations, bin_number)
    c = get_complaints(complaints, bin_number)
    address = f"{row[SHED_HOUSE_COL]} {row[SHED_STREET_COL]}"
    results.append({
        "address": address,
        "bin": bin_number,
        "duration_years": round(row["_duration_days"] / 365, 1),
        "violation_count": len(v),
        "complaint_count": len(c),
    })

results_df = pd.DataFrame(results)
results_df["score"] = results_df["violation_count"] + results_df["complaint_count"]
results_df = results_df.sort_values("score", ascending=False)

print(results_df.head(10).to_string(index=False))