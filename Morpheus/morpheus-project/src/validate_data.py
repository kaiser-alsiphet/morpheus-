"""Validate raw schema/labels/nulls/balance. Usage: python -m src.validate_data [--input CSV]"""
import argparse, json, sys
import pandas as pd
REQ = ["id", "text", "label", "source", "author_or_generator", "topic", "collection_method"]

def validate(df: pd.DataFrame) -> dict:
    miss = [c for c in REQ if c not in df.columns]
    if miss:
        raise ValueError(f"Missing columns: {miss}")
    words = df["text"].fillna("").astype(str).str.split().str.len()
    return {"rows": len(df), "null_text": int(df["text"].isna().sum()),
            "bad_labels": int((~df["label"].isin([0, 1])).sum()),
            "duplicate_ids": int(df["id"].duplicated().sum()),
            "label_counts": df["label"].value_counts().to_dict(),
            "source_counts": df["source"].value_counts().to_dict(),
            "generator_counts": df["author_or_generator"].value_counts().to_dict(),
            "words_describe": words.describe().round(1).to_dict()}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--input", default="data/raw/dataset.csv")
    a = ap.parse_args()
    try:
        r = validate(pd.read_csv(a.input))
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"Validation failed: {e}")
    json.dump(r, open("reports/validation_report.json", "w"), indent=2, default=str)
    print(json.dumps(r, indent=2, default=str))
