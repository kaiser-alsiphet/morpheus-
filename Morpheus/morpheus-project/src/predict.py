"""Shared inference. Outputs are likelihood ESTIMATES, never proof of authorship."""
from pathlib import Path
import numpy as np
SHORT_WORDS, MAXLEN = 30, 256
DISCLAIMER = ("Probabilities are statistical estimates, not proof of authorship. This tool cannot prove "
              "AI use and must not be used as a plagiarism or cheating detector.")

def available_models() -> dict:
    m = {}
    if Path("models/baseline.joblib").exists():
        import joblib
        m["baseline"] = ("baseline", joblib.load("models/baseline.joblib"))
    if Path("models/transformer/config.json").exists():
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        m["transformer"] = ("transformer", (AutoTokenizer.from_pretrained("models/transformer"),
                            AutoModelForSequenceClassification.from_pretrained("models/transformer").eval()))
    return m

def predict_proba(texts: list[str], model) -> np.ndarray:
    kind, obj = model
    if kind == "baseline":
        return obj.predict_proba(texts)[:, 1]
    import torch
    tok, net = obj; out = []
    with torch.no_grad():
        for i in range(0, len(texts), 16):
            b = tok(texts[i:i + 16], truncation=True, max_length=MAXLEN, padding=True, return_tensors="pt")
            out += torch.softmax(net(**b).logits, -1)[:, 1].tolist()
    return np.array(out)

def predict_text(text, model=None) -> dict:
    if not isinstance(text, str) or not text.strip():
        return {"error": "Please enter some text to analyze."}
    if model is None:
        ms = available_models()
        if not ms:
            return {"error": "No trained model found. Run the training scripts first."}
        model = ms.get("transformer") or ms["baseline"]
    p = float(predict_proba([text], model)[0]); words = len(text.split()); warn = []
    if words < SHORT_WORDS:
        warn.append(f"Very short input ({words} words): results are unreliable.")
    if words > 200:
        warn.append(f"Only roughly the first {MAXLEN} tokens are analyzed.")
    unc = 0.4 <= p <= 0.6
    return {"error": None, "p_ai": p, "p_human": 1 - p, "label": "AI-generated" if p >= .5 else "Human-written",
            "uncertain": unc, "words": words, "chars": len(text), "warnings": warn, "model": model[0],
            "message": "Uncertain: the model is close to a coin flip." if unc else "Estimate only; it can be wrong."}
