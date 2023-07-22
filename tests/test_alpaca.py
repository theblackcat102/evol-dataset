import os
from datasets import load_dataset
from tqdm import tqdm
from evolinstruct import EvolInstruction

if __name__ == "__main__":
    evol = EvolInstruction(
        model_name="gpt-3.5-turbo",
        backend="openai",
        backend_settings={"api_key": os.getenv("OPENAI_KEY")},
    )
    dataset = load_dataset("tatsu-lab/alpaca")["train"]
    texts = []
    for row in tqdm(dataset):
        input_text = row["instruction"]
        if len(row["input"]):
            input_text += "## Input:\n" + row["input"]
        texts.append(input_text)
        if len(texts) > 10:
            break

    results = evol.ingest(texts, "alpaca_evol_sample", total_augment=20)
    print(results[:10])
