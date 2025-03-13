from transformers import DistilBertTokenizer, DistilBertModel
import torch
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, log_loss, confusion_matrix
import json
import numpy as np

# Läs träningsdatan från träningsdata.json
with open('Python/data/träningsdata.json', 'r') as f:
    data = json.load(f)

# Extrahera text och etiketter
texts = [entry["text"] for entry in data]
labels = [entry["label"] for entry in data]

# Dela upp data i tränings- och testuppsättningar
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Ladda DistilBERT-tokenizer och modell
tokenizer = DistilBertTokenizer.from_pretrained("./fine_tuned_distilbert")
model = DistilBertModel.from_pretrained("./fine_tuned_distilbert")

# Funktion för att omvandla text till DistilBERT-inbäddningar
def get_embeddings(texts, tokenizer, model):
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    # Skicka data till modellen (utan att beräkna gradienter)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Använd inbäddningen för den första tokenen ([CLS]) från last_hidden_state
    embeddings = outputs.last_hidden_state[:, 0, :].numpy()  # Hämta den första tokenen ([CLS]) för varje sekvens
    return embeddings

# Hämta DistilBERT-inbäddningar för tränings- och testdata
X_train_embeddings = get_embeddings(X_train, tokenizer, model)
X_test_embeddings = get_embeddings(X_test, tokenizer, model)

# Träna en Random Forest-modell på de DistilBERT-genererade funktionerna
rf_model = RandomForestClassifier()
rf_model.fit(X_train_embeddings, y_train)

# Förutsägelser på testdatan
y_pred = rf_model.predict(X_test_embeddings)

# Utvärdera modellen: Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Utvärdera modellen: F1-Score, Precision, Recall
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Om du har sannolikheter från RandomForest kan du beräkna log_loss:
# För att få sannolikheter från RandomForest:
y_prob = rf_model.predict_proba(X_test_embeddings)

# Beräkna log_loss
loss = log_loss(y_test, y_prob)
print(f"Log Loss: {loss:.4f}")

# Confusion Matrix
conf_matrix = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(conf_matrix)

# Skriv ut resultat för ytterligare analys:
print("\nUtvärderingsresultat:")
print(f"Accuracy: {accuracy * 100:.2f}%")
print(f"Log Loss: {loss:.4f}")
print(f"Confusion Matrix:\n{conf_matrix}")
