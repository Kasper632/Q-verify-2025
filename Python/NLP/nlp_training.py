from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments, DistilBertTokenizer
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
import numpy as np

# Ladda JSON-data
with open('Python/data/10k_50_50.json', 'r') as f:
    data = json.load(f)

# Konvertera varje rad till kombinerad text + label
texts = []
labels = []

for entry in data:
    competences = entry.get("competences", "")
    pmnum = entry.get("pmnum", "")
    cxlineroutenr = str(entry.get("cxlineroutenr", ""))
    location = entry.get("location", "")
    description = entry.get("description", "")
    label = int(entry.get("valid", 0))

    combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
    texts.append(combined)
    labels.append(label)

# Skapa Dataset till HF-format
dataset = Dataset.from_dict({"text": texts, "label": labels})

# Debug: kolla labeldistribution
print("Label distribution (all):", np.bincount(labels))

# Ladda modell & tokenizer
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

shuffled = tokenized_datasets.shuffle(seed=42)
split_idx = int(0.8 * len(shuffled))
train_dataset = shuffled.select(range(split_idx))
test_dataset = shuffled.select(range(split_idx, len(shuffled)))


# Debug: kolla labeldistribution i train/test
print("Train label dist:", np.bincount(train_dataset['label']))
print("Test label dist:", np.bincount(test_dataset['label']))

def compute_metrics(p):
    predictions, labels = p
    preds = np.argmax(predictions, axis=1)
    return {"accuracy": accuracy_score(labels, preds)}

# Träningsargument
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

# Spara modellen
trainer.save_model("Python/AI-models/maximo_model")

# Utvärdera
results = trainer.evaluate()
print(f"Test accuracy: {results['eval_accuracy']}")

# Extra eval: precision, recall, f1, exempel
predictions = trainer.predict(test_dataset)
preds = np.argmax(predictions.predictions, axis=1)
labels = predictions.label_ids

# Debug: kolla fördelning av modellens gissningar
print("Predictions dist:", np.bincount(preds))

print("Precision:", precision_score(labels, preds, zero_division=0))
print("Recall:", recall_score(labels, preds, zero_division=0))
print("F1-score:", f1_score(labels, preds, zero_division=0))

# Visa exempel
print("\nExempel prediktioner:")
for i in range(50):
    print(f"Text: {test_dataset[i]['text'][:100]}...")
    print(f"Predicted: {preds[i]}, Actual: {labels[i]}\n")