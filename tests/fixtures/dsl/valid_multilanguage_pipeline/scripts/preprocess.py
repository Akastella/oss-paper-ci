"""Preprocess step placeholder."""
import os
os.makedirs("results", exist_ok=True)
with open("results/clean_data.csv", "w") as f:
    f.write("x,y\n1,0\n2,1\n")
