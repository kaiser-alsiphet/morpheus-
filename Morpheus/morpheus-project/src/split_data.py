"""Group-aware stratified 70/15/15 split (7 folds: 1 test, 1 val, 5 train). Usage: python -m src.split_data"""
import json, sys
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
SEED = 42

def split(df: pd.DataFrame):
    folds = [i for _, i in StratifiedGroupKFold(7, shuffle=True, random_state=SEED).split(df, df["label"], df["group"])]
    te, va = df.iloc[folds[0]], df.iloc[folds[1]]
    tr = df.iloc[[i for f in folds[2:] for i in f]]
    for a, b in [(tr, va), (tr, te), (va, te)]:
        assert not set(a["group"]) & set(b["group"]), "group leakage"
    return tr, va, te

if __name__ == "__main__":
    try:
        tr, va, te = split(pd.read_csv("data/interim/cleaned.csv"))
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"Split failed: {e}")
    rep = {}
    for n, d in [("train", tr), ("val", va), ("test", te)]:
        d.to_csv(f"data/processed/{n}.csv", index=False)
        rep[n] = {"rows": len(d), "label_counts": d["label"].value_counts().to_dict()}
    json.dump(rep, open("reports/split_report.json", "w"), indent=2); print(rep)
