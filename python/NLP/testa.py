from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from datasets import Dataset
import torch
import json
import numpy as np

# Ladda tokenizer och tränad modell
model_path = "Python/AI-models/maximo_model"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

# Ladda ny JSON-fil för testning
with open("Python/data/100_60_40.json", "r") as f:
    new_data = json.load(f)

# Skapa samma kombinerade textsträng som vid träning
texts = []
for entry in new_data:
    competences = entry.get("competences", "")
    pmnum = entry.get("pmnum", "")
    cxlineroutenr = str(entry.get("cxlineroutenr", ""))
    location = entry.get("location", "")
    description = entry.get("description", "")
    combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
    texts.append(combined)

# Skapa dataset
predict_dataset = Dataset.from_dict({"text": texts})

def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

tokenized = predict_dataset.map(tokenize_function, batched=True)
tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])

# Inference
model.eval()
preds = []
with torch.no_grad():
    for batch in torch.utils.data.DataLoader(tokenized, batch_size=16):
        outputs = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
        logits = outputs.logits
        batch_preds = torch.argmax(logits, axis=1).numpy()
        preds.extend(batch_preds)

# Skapa JSON-output
results = []
for i, entry in enumerate(new_data):
    results.append({
        "input": entry,
        "predicted_valid": int(preds[i])
    })

# Spara till JSON-fil
with open("Python/data/predicted_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Resultat sparat i Python/data/predicted_results.json")