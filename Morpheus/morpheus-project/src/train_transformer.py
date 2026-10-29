"""Fine-tune DistilBERT (max 256 tokens; longer text is truncated). Usage: python -m src.train_transformer [--max_train_samples N] [--epochs 4]"""
import argparse, json
import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding,
                          EarlyStoppingCallback, Trainer, TrainingArguments, set_seed)
MODEL, MAXLEN, SEED = "distilbert-base-uncased", 256, 42

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--max_train_samples", type=int); ap.add_argument("--epochs", type=int, default=4)
    a = ap.parse_args(); set_seed(SEED)
    tr, va = pd.read_csv("data/processed/train.csv"), pd.read_csv("data/processed/val.csv")
    if a.max_train_samples:
        tr = tr.sample(min(a.max_train_samples, len(tr)), random_state=SEED)
    tok = AutoTokenizer.from_pretrained(MODEL)
    enc = lambda d: Dataset.from_pandas(d[["text", "label"]].reset_index(drop=True)).map(
        lambda b: tok(b["text"], truncation=True, max_length=MAXLEN), batched=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2, id2label={0: "human", 1: "ai"})
    def cm(ev):
        p = ev.predictions.argmax(-1); return {"accuracy": accuracy_score(ev.label_ids, p), "f1": f1_score(ev.label_ids, p)}
    args = TrainingArguments("checkpoints", eval_strategy="epoch", save_strategy="epoch", num_train_epochs=a.epochs,
                             learning_rate=2e-5, per_device_train_batch_size=16, per_device_eval_batch_size=32, weight_decay=0.01,
                             load_best_model_at_end=True, metric_for_best_model="f1", save_total_limit=1, seed=SEED, report_to="none")
    t = Trainer(model=model, args=args, train_dataset=enc(tr), eval_dataset=enc(va), data_collator=DataCollatorWithPadding(tok),
                compute_metrics=cm, callbacks=[EarlyStoppingCallback(2)])
    t.train(); t.save_model("models/transformer"); tok.save_pretrained("models/transformer")
    json.dump(t.evaluate(), open("reports/transformer_val.json", "w"), indent=2, default=float)

if __name__ == "__main__":
    main()
