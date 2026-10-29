"""TF-IDF + LogisticRegression. Tuned on train only (group-aware CV); val reported once. Usage: python -m src.train_baseline"""
import json, sys
import joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from src.evaluate import metrics

if __name__ == "__main__":
    try:
        tr, va = pd.read_csv("data/processed/train.csv"), pd.read_csv("data/processed/val.csv")
    except FileNotFoundError:
        sys.exit("Run clean_data and split_data first.")
    pipe = Pipeline([("tfidf", TfidfVectorizer(lowercase=False, sublinear_tf=True)),
                     ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
    grid = {"tfidf__ngram_range": [(1, 1), (1, 2)], "clf__C": [0.3, 1, 3, 10]}
    gs = GridSearchCV(pipe, grid, cv=GroupKFold(3), scoring="f1", n_jobs=-1).fit(tr["text"], tr["label"], groups=tr["group"])
    joblib.dump(gs.best_estimator_, "models/baseline.joblib")
    res = {"best_params": {k: str(v) for k, v in gs.best_params_.items()},
           "val": metrics(va["label"], gs.best_estimator_.predict_proba(va["text"])[:, 1])}
    json.dump(res, open("reports/baseline_val.json", "w"), indent=2, default=float); print(res["best_params"], res["val"].get("f1"))
