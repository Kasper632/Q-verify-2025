from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments, DistilBertTokenizer
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import torch
import numpy as np
import json

# Ladda JSON-data
with open('python/data/trafikdata_50k_25k_25k.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Förbered historiska samband
route_to_headsign = {}
route_to_shortname = {}
route_to_service = {}
seen_tripids = set()

for row in data:
    routeid = row["RouteId"]
    headsign = row["TripHeadSign"]
    shortname = row["TripShortName"]
    serviceid = row["ServiceId"]

    route_to_headsign.setdefault(routeid, set()).add(headsign)
    route_to_shortname.setdefault(routeid, set()).add(shortname)
    route_to_service.setdefault(routeid, set()).add(serviceid)

# Skapa träningsdata
texts, labels = [], []

for row in data:
    routeid = row["RouteId"]
    headsign = row["TripHeadSign"]
    shortname = row["TripShortName"]
    serviceid = row["ServiceId"]
    tripid = row["TripId"]

    route_wrong = int(headsign not in route_to_headsign[routeid])
    shortname_wrong = int(shortname not in route_to_shortname[routeid])
    service_wrong = int(serviceid not in route_to_service[routeid])
    duplicate_tripid = int(tripid in seen_tripids)

    seen_tripids.add(tripid)

    text = f"RouteId={routeid}; ServiceId={serviceid}; TripHeadSign={headsign}; TripShortName={shortname}; TripId={tripid}"
    texts.append(text)
    labels.append([float(route_wrong), float(shortname_wrong), float(service_wrong), float(duplicate_tripid)])

# Dataset & tokenisering
dataset = Dataset.from_dict({"text": texts, "labels": labels})
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def tokenize_function(examples):
    tokens = tokenizer(examples['text'], padding="max_length", truncation=True)
    tokens['labels'] = examples['labels']
    return tokens

tokenized_dataset = dataset.map(tokenize_function, batched=True)
tokenized_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# Split
shuffled = tokenized_dataset.shuffle(seed=42)
split_idx = int(0.8 * len(shuffled))
train_dataset = shuffled.select(range(split_idx))
test_dataset = shuffled.select(range(split_idx, len(shuffled)))

# Modell
model = DistilBertForSequenceClassification.from_pretrained(
    'distilbert-base-uncased',
    num_labels=4,
    problem_type="multi_label_classification"
)

# Använd CUDA om tillgängligt
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

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
    output_dir='./results_trafikdata',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    evaluation_strategy="epoch",
    logging_dir='./logs_trafikdata',
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
trainer.save_model("trafikdata_model")

# Utvärdera
results = trainer.evaluate()
print(f"Test accuracy: {results.get('eval_accuracy', 0):.4f}")
print("Precision:", results.get("precision"))
print("Recall:", results.get("recall"))
print("F1-score:", results.get("f1"))

# Exempelprediktioner
predictions = trainer.predict(test_dataset)
preds = (torch.sigmoid(torch.tensor(predictions.predictions)) > 0.5).int().numpy()
labels = predictions.label_ids

print("\\nExempel prediktioner:")
for i in range(5):
    print(f"Text: {test_dataset[i]['text'][:100]}...")
    print(f"Predicted fields wrong: {preds[i]}, Actual wrong: {labels[i]}")
    print("---")
