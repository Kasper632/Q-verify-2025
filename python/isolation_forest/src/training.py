import json
import pandas as pd
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset, DataLoader
import torch
import os

print(torch.cuda.is_available())  # Bör vara True om CUDA är tillgängligt
print(torch.cuda.device_count())  # Antal GPU:er
print(torch.cuda.get_device_name(0))
# Sätt enhet till GPU om tillgänglig, annars CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Ladda data
with open("wwwroot/uploads/allData.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

df['text'] = df['Name'] + ' ' + df['Email'] + ' ' + df['Street']
df = df[['text', 'valid']]
df.columns = ['text', 'label']

# Ladda modell och tokenizer
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased").to(device)
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

class CustomDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, item):
        text = self.texts[item]
        label = self.labels[item]
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

# Skapa dataset och dataloader
train_dataset = CustomDataset(
    texts=df['text'].tolist(),  
    labels=df['label'].tolist(), 
    tokenizer=tokenizer,
    max_len=128
)

# Skapa en egen collate_fn för att undvika pinning av CUDA-tensorer
def collate_fn(batch):
    input_ids = torch.stack([item['input_ids'] for item in batch])
    attention_mask = torch.stack([item['attention_mask'] for item in batch])
    labels = torch.stack([item['labels'] for item in batch])
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask,
        'labels': labels
    }

# Inaktivera pinning för CUDA och använd custom collate_fn
train_dataloader = DataLoader(
    train_dataset, 
    batch_size=8, 
    shuffle=True, 
    pin_memory=False,  # Inaktiverar pinning
    collate_fn=collate_fn  # Använd custom collate_fn
)

# Träningsargument
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=5,
    per_device_train_batch_size=8,
    logging_dir='./logs',
    logging_steps=10,
    save_total_limit=1,
    fp16=torch.cuda.is_available(),  # Aktiverar mixed precision om GPU används
)

# Skapa Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# Träna modellen
trainer.train()

# Spara modellen
save_path = "./trained_model_GPU"
os.makedirs(save_path, exist_ok=True)
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)

print(f"Modellen sparades i: {os.path.abspath(save_path)}")
print(f"Total rader bearbetade: {len(df) * training_args.num_train_epochs}")
