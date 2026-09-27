"""
One-off script: print real column names for the new safety datasets
so we can wire pipeline.py to the actual columns, not guesses.
"""

import pandas as pd

elevator = pd.read_csv("data/elevator_safety.csv", low_memory=False)
print("=== ELEVATOR SAFETY COLUMNS ===")
print(list(elevator.columns))
print()
print("First row sample:")
print(elevator.iloc[0])

print()
print("=" * 40)
print()

fire = pd.read_csv("data/fire_safety.csv", low_memory=False)
print("=== FIRE SAFETY COLUMNS ===")
print(list(fire.columns))
print()
print("First row sample:")
print(fire.iloc[0])