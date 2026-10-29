import pandas as pd
from src.clean_data import clean, clean_text
from src.predict import predict_text

def test_clean_text_preserves_style():
    t = clean_text("Hello   <b>World</b>!  See https://x.com/?utm_source=a\n\n\n\nNew PARA.")
    assert "http" not in t and "<b>" not in t and "World" in t and "\n\n" in t and "PARA" in t

def test_cleaning_log_and_dups():
    df = pd.DataFrame({"id": [1, 2, 3, 4], "text": ["a b c d e f g", "a b c d e f g", None, "short"], "label": [0, 0, 1, 1],
                       "group_id": ["x", "y", "z", "w"]})
    out, flagged, log = clean(df, min_words=5)
    assert len(out) == 1 and log["removed_null"] == 1 and log["removed_exact_duplicates"] == 1 and log["removed_below_min_words"] == 1

def test_empty_input():
    for s in ["", "   \n", None]:
        assert predict_text(s)["error"]

def test_prediction_contract_and_short_warning():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    m = make_pipeline(TfidfVectorizer(), LogisticRegression()).fit(["good day", "bad night", "good one", "bad two"], [0, 1, 0, 1])
    r = predict_text("good day", ("baseline", m))
    assert abs(r["p_ai"] + r["p_human"] - 1) < 1e-9 and r["warnings"] and r["label"] in ("AI-generated", "Human-written")
