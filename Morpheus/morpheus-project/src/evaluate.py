"""Evaluate on test + slices. No scores are invented: slices with <30 rows are 'insufficient data'.
Usage: python -m src.evaluate"""
import json
import numpy as np, pandas as pd
from sklearn.metrics import (accuracy_score, brier_score_loss, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
MIN_N = 30

def metrics(y, p, thr: float = 0.5) -> dict:
    y, p = np.asarray(y), np.asarray(p); yh = (p >= thr).astype(int)
    if len(y) < MIN_N:
        return {"n": len(y), "status": "insufficient data"}
    both = len(set(y)) == 2
    return {"n": len(y), "accuracy": accuracy_score(y, yh), "precision": precision_score(y, yh, zero_division=0),
            "recall": recall_score(y, yh, zero_division=0), "f1": f1_score(y, yh, zero_division=0),
            "roc_auc": roc_auc_score(y, p) if both else None, "brier": brier_score_loss(y, p),
            "confusion_matrix": confusion_matrix(y, yh, labels=[0, 1]).tolist(),
            "per_class": classification_report(y, yh, labels=[0, 1], output_dict=True, zero_division=0)}

def slices(te: pd.DataFrame) -> dict:
    w = te["text"].str.split().str.len(); s = {"all": w >= 0, "short_<50w": w < 50, "long_>=300w": w >= 300}
    for c in ["topic", "author_or_generator"]:
        for v in te[c].unique():
            s[f"{c}={v}"] = te[c] == v
    return s

if __name__ == "__main__":
    from src.predict import available_models, predict_proba
    te = pd.read_csv("data/processed/test.csv"); out = {}
    for kind, m in available_models().items():
        p = predict_proba(te["text"].tolist(), m)
        out[kind] = {k: metrics(te.loc[mask, "label"], p[np.asarray(mask)]) for k, mask in slices(te).items()}
    json.dump(out, open("reports/metrics.json", "w"), indent=2, default=float)
    for k, v in out.items():
        print(k, {a: v["all"].get(a) for a in ["n", "accuracy", "f1", "roc_auc"]})
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, seaborn as sns
        fig, ax = plt.subplots(1, len(out), figsize=(5 * len(out), 4), squeeze=False)
        for a, (k, v) in zip(ax[0], out.items()):
            if "confusion_matrix" in v["all"]:
                sns.heatmap(v["all"]["confusion_matrix"], annot=True, fmt="d", ax=a, xticklabels=["human", "AI"], yticklabels=["human", "AI"]); a.set_title(k)
        fig.savefig("reports/confusion_matrices.png", dpi=120, bbox_inches="tight")
    except Exception as e:
        print("plot skipped:", e)
