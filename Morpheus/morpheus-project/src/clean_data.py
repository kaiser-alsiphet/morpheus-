"""Conservative cleaning with a per-operation log. Near-duplicates are flagged and clustered (not deleted);
the splitter keeps each cluster in one split. Usage: python -m src.clean_data [--input CSV] [--min_words 20]"""
import argparse, json, re, sys, unicodedata
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
URL = re.compile(r"https?://\S+|www\.\S+")  # also removes tracking params inside URLs
TAG = re.compile(r"</?(?:p|div|span|br|a|b|i|em|strong|ul|ol|li|h[1-6]|table|tr|td|img)\b[^>]*>", re.I)
PII = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s().-]{8,}\d")

def clean_text(t: str) -> str:
    """Normalize Unicode/whitespace, strip markup+URLs. Keeps case, punctuation, paragraph breaks."""
    t = unicodedata.normalize("NFKC", str(t)).replace("\r", "")
    t = URL.sub("", TAG.sub(" ", t))
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def _key(t: str) -> str:
    return re.sub(r"\W+", " ", t.lower()).strip()

def near_dup_pairs(texts: list[str], thr: float):
    if len(texts) < 2:
        return
    X = TfidfVectorizer().fit_transform(texts)
    for s in range(0, X.shape[0], 1000):
        S = (X[s:s + 1000] @ X.T).tocoo()
        for i, j, v in zip(S.row + s, S.col, S.data):
            if i < j and v >= thr:
                yield int(i), int(j)

def components(n: int, pairs) -> list[int]:
    p = list(range(n))
    def f(x):
        while p[x] != x:
            p[x] = p[p[x]]; x = p[x]
        return x
    for a, b in pairs:
        p[f(a)] = f(b)
    return [f(i) for i in range(n)]

def clean(df: pd.DataFrame, min_words: int = 20, thr: float = 0.9):
    log = {"input_rows": len(df)}
    df = df.copy()
    n = len(df); df = df[df["text"].notna()]; log["removed_null"] = n - len(df)
    df["text"] = df["text"].map(clean_text)
    n = len(df); df = df[df["text"] != ""]; log["removed_empty"] = n - len(df)
    n = len(df); df = df[df["text"].str.split().str.len() >= min_words]
    log["removed_below_min_words"] = n - len(df); log["min_words"] = min_words
    n = len(df); df = df[~df["text"].map(_key).duplicated()]; log["removed_exact_duplicates"] = n - len(df)
    pii = df["text"].str.contains(PII)
    flagged = df[pii].assign(flag_reason="possible_personal_info")
    df = df[~pii].reset_index(drop=True); log["flagged_and_excluded_pii"] = int(pii.sum())
    pairs = list(near_dup_pairs(df["text"].map(_key).tolist(), thr))
    log["near_duplicate_pairs"] = len(pairs)
    if "group_id" in df:  # rows sharing an original group (e.g. same question) stay together
        for _, idx in df.groupby("group_id").indices.items():
            pairs += [(int(idx[0]), int(k)) for k in idx[1:]]
    df["group"] = components(len(df), pairs)
    df["near_dup_flag"] = df.groupby("group")["text"].transform("size") > 1
    log.update(near_dup_threshold=thr, output_rows=len(df))
    return df, flagged, log

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/raw/dataset.csv"); ap.add_argument("--min_words", type=int, default=20)
    ap.add_argument("--threshold", type=float, default=0.9)
    a = ap.parse_args()
    try:
        d, fl, lg = clean(pd.read_csv(a.input), a.min_words, a.threshold)
    except FileNotFoundError:
        sys.exit(f"Not found: {a.input}. Run: python -m src.download_data")
    d.to_csv("data/interim/cleaned.csv", index=False); fl.to_csv("data/interim/flagged.csv", index=False)
    json.dump(lg, open("reports/cleaning_log.json", "w"), indent=2); print(json.dumps(lg, indent=2))
