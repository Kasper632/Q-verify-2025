from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
from datasets import Dataset
import torch
import json
from tqdm import tqdm

# Modell och tokenizer
model_path = "Python/AI-models/maximo_fields"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

# Ladda testdata
with open("Python/data/100_60_40.json", "r") as f:
    new_data = json.load(f)

texts = []
for entry in new_data:
    competences = entry.get("competences", "")
    pmnum = entry.get("pmnum", "")
    cxlineroutenr = str(entry.get("cxlineroutenr", ""))
    location = entry.get("location", "")
    description = entry.get("description", "")
    combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
    texts.append(combined)

predict_dataset = Dataset.from_dict({"text": texts})

def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

tokenized = predict_dataset.map(tokenize_function, batched=True)
tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])

# Prediction
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

all_preds = []
with torch.no_grad():
    for batch in tqdm(torch.utils.data.DataLoader(tokenized, batch_size=32)):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        probs = torch.sigmoid(outputs.logits)
        preds = (probs > 0.5).int().cpu().numpy()
        all_preds.extend(preds)

# Packa resultat
column_names = ["competences", "pmnum", "cxlineroutenr", "location"]
results = []
for i, entry in enumerate(new_data):
    pred_fields = all_preds[i].tolist()
    valid = int(sum(pred_fields) == 0)
    anomalies = [col for j, col in enumerate(column_names) if pred_fields[j] == 1]

    results.append({
        "input": entry,
        "predicted_fields": pred_fields,
        "predicted_valid": valid,
        "anomaly_fields": anomalies
    })

# Spara
with open("Python/data/predicted_multilabel.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Klar. Sparat till Python/data/predicted_multilabel.json")