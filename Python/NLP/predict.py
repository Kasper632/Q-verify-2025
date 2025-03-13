from transformers import DistilBertTokenizer, DistilBertModel
import torch
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import json
import numpy as np

torch.manual_seed(42)
np.random.seed(42)

# Läs träningsdatan från träningsdata.json
with open('träningsdata.json', 'r') as f:
    data = json.load(f)

# Extrahera text och etiketter
texts = [entry["text"] for entry in data]
labels = [entry["label"] for entry in data]

# Dela upp data i tränings- och testuppsättningar
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Ladda DistilBERT-tokenizer och modell
tokenizer = DistilBertTokenizer.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k")
model = DistilBertModel.from_pretrained("./Python/AI-models/fine_tuned_distilbert_50k")

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
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train_embeddings, y_train)

# Förutsägelser på testdatan
y_pred = rf_model.predict(X_test_embeddings)

# Utvärdera modellen
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Funktion för att förutsäga för en given text
def predict(text, model, tokenizer, rf_model):
    embedding = get_embeddings([text], tokenizer, model)
    prediction = rf_model.predict(embedding)
    return prediction[0]

# Läs in testdatan från testdata.json
with open('testdata.json', 'r') as f:
    test_data = json.load(f)

# Extrahera texten från testdatan
test_texts = [entry["text"] for entry in test_data]

# Förutsäg för varje testtext
test_predictions = [predict(text, model, tokenizer, rf_model) for text in test_texts]

# Filtrera ut de texter som har en förutsägelse av 0 (felaktiga förutsägelser)
incorrect_predictions = [
    {
        "text": test_texts[i],
        "predicted_label": int(test_predictions[i])  # Konvertera till vanlig int
    }
    for i in range(len(test_predictions)) if test_predictions[i] == 0
]

# Räknare för felaktiga förutsägelser
incorrect_count = len(incorrect_predictions)
print(f"Antal felaktiga förutsägelser: {incorrect_count}")

# Skriv ut de felaktiga förutsägelserna till en JSON-fil
with open("incorrect_predictions.json", "w") as f:
    json.dump(incorrect_predictions, f, indent=4)
