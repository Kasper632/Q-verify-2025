from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import torch
from transformers import DistilBertTokenizer, DistilBertModel
from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score
import json
import numpy as np

# Ladda tränings- och testdata
with open('Python/data/träningsdata.json', 'r') as f:
    data = json.load(f)

texts = [entry["text"] for entry in data]
labels = [entry["label"] for entry in data]

# Skapa dataset som Hugging Face kan förstå
from datasets import Dataset
dataset = Dataset.from_dict({"text": texts, "label": labels})

# Ladda DistilBERT och tokenizer för fine-tuning
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Tokenisera dataset
def tokenize_function(examples):
    return tokenizer(examples['text'], padding="max_length", truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# Dela upp i tränings- och testset
train_dataset = tokenized_datasets.shuffle(seed=42).select([i for i in list(range(int(0.8 * len(tokenized_datasets))))])
test_dataset = tokenized_datasets.shuffle(seed=42).select([i for i in list(range(int(0.8 * len(tokenized_datasets)), len(tokenized_datasets)))])

def compute_metrics(p):
    predictions, labels = p
    preds = np.argmax(predictions, axis=1)  # Välj den högsta sannolikheten
    return {"accuracy": accuracy_score(labels, preds)}

# Konfigurera träningsargument
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
    model=model,                         # modellen
    args=training_args,                  # träningsargument
    train_dataset=train_dataset,         # träningsdataset
    eval_dataset=test_dataset,           # testdataset
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# Träna modellen
trainer.train()

# Spara den fine-tunade modellen
trainer.save_model("Python/AI-models/fine_tuned_distilbert")

# Testa på testdatan
results = trainer.evaluate()

print(f"Test accuracy: {results['eval_accuracy']}")
