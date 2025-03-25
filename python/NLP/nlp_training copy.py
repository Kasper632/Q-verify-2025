# Träna DistilBERT för att klassificera vilken kolumn som orsakar mismatch (liknande binärmodellstruktur)
from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments, DistilBertTokenizer
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import torch
import numpy as np
import json
import re

# Ladda JSON-data
with open('Python/data/10k_50_50.json', 'r') as f:
    data = json.load(f)

# Förbered träningsdata
texts = []
labels = []

for entry in data:
    competences = entry.get("competences", "")
    pmnum = entry.get("pmnum", "")
    cxlineroutenr = str(entry.get("cxlineroutenr", ""))
    location = entry.get("location", "")
    description = entry.get("description", "")

    # Semantisk regelbaserad label-generator (multi-label per fält)
    match = re.search(r"maskin\s*(\d)", description.lower())
    maskin = int(match.group(1)) if match else None

    comp_wrong = int((maskin in [1,2,3,4] and competences != "BANA") or
                     (maskin == 5 and competences != "EL") or
                     (maskin == 6 and competences != "SIGNAL"))

    # Ny pmnum-regel: matcha första bokstaven med ord i description
    pm_first = pmnum[:1].upper()
    desc_first_word = description.strip().split(" ")[0] if description.strip() else ""
    desc_first_letter = re.sub(r"[^A-Z]", "", desc_first_word.upper())[:1]
    pmnum_wrong = int(pm_first != desc_first_letter)

    route_wrong = int(cxlineroutenr not in description)
    loc_wrong = int(location.lower() not in description.lower())

    combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
    texts.append(combined)
    labels.append([float(comp_wrong), float(pmnum_wrong), float(route_wrong), float(loc_wrong)])

# Skapa dataset
dataset = Dataset.from_dict({"text": texts, "labels": labels})

# Tokenisera
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
def tokenize_function(examples):
    tokens = tokenizer(examples['text'], padding="max_length", truncation=True)
    tokens['labels'] = examples['labels']
    return tokens

tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# Dela upp train/test
shuffled = tokenized_datasets.shuffle(seed=42)
split_idx = int(0.8 * len(shuffled))
train_dataset = shuffled.select(range(split_idx))
test_dataset = shuffled.select(range(split_idx, len(shuffled)))

# Modell (4 labels = 4 fält)
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=4, problem_type="multi_label_classification")

# Metrik
def compute_metrics(p):
    predictions, labels = p
    probs = torch.sigmoid(torch.tensor(predictions))
    preds = (probs > 0.5).int().numpy()
    precision = precision_score(labels, preds, average="macro", zero_division=0)
    recall = recall_score(labels, preds, average="macro", zero_division=0)
    f1 = f1_score(labels, preds, average="macro", zero_division=0)
    accuracy = accuracy_score(labels, preds)
    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1}

# Träningsargument
training_args = TrainingArguments(
    output_dir='./results_multilabel_fields',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    logging_dir='./logs_multilabel_fields',
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# Träna & spara
trainer.train()
trainer.save_model("Python/AI-models/maximo_fields")

# Utvärdera
results = trainer.evaluate()
print(f"Test accuracy: {results['eval_accuracy']:.4f}" if 'eval_accuracy' in results else "")
print("Precision:", results.get("precision"))
print("Recall:", results.get("recall"))
print("F1-score:", results.get("f1"))

# Exempelprediktioner
predictions = trainer.predict(test_dataset)
preds = (torch.sigmoid(torch.tensor(predictions.predictions)) > 0.5).int().numpy()
labels = predictions.label_ids

print("\nExempel prediktioner:")
for i in range(5):
    print(f"Text: {test_dataset[i]['text'][:100]}...")
    print(f"Predicted fields wrong: {preds[i]}, Actual wrong: {labels[i]}")
    print("---")
