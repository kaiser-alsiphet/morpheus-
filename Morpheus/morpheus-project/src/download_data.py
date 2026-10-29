"""Download HC3 (human vs ChatGPT answers) raw files and map to our schema.
Verify the dataset license on its Hugging Face page. Usage: python -m src.download_data"""
import json
import pandas as pd
from huggingface_hub import hf_hub_download
NAME = "Hello-SimpleAI/HC3"
SUBSETS = ["finance", "medicine", "open_qa", "wiki_csai"]

def main() -> None:
    rows = []
    for s in SUBSETS:
        path = hf_hub_download(NAME, f"{s}.jsonl", repo_type="dataset")
        for i, line in enumerate(open(path, encoding="utf-8")):
            ex = json.loads(line)
            for k, t in enumerate(ex.get("human_answers", [])):
                rows.append((f"{s}-{i}-h{k}", t, 0, "HC3-human", "human", s, "public dataset", f"{s}-{i}"))
            for k, t in enumerate(ex.get("chatgpt_answers", [])):
                rows.append((f"{s}-{i}-a{k}", t, 1, "HC3-chatgpt", "chatgpt", s, "public dataset", f"{s}-{i}"))
    cols = ["id", "text", "label", "source", "author_or_generator", "topic", "collection_method", "group_id"]
    pd.DataFrame(rows, columns=cols).to_csv("data/raw/dataset.csv", index=False)
    print(f"Saved {len(rows)} rows. Check license: https://huggingface.co/datasets/{NAME}")

if __name__ == "__main__":
    main()
