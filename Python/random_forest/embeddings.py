import json
import os
import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from preprocess import preprocess_text_data
from embeddings import generate_embeddings

# Paths
DATA_PATH = "wwwroot/uploads/allData.json"
MODEL_PATH = "Python/AI-models/random_forest_model3.pkl"

# Load data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Combine all text columns into a single column "data"
df["data"] = df.astype(str).agg(' '.join, axis=1)
labels = df["label"]  # Assuming a "label" column exists for training

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Generate embeddings
embeddings = generate_embeddings(df, model)

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(embeddings, labels, test_size=0.2, random_state=42)

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Evaluate Model
y_pred = rf.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred))

# Save Model
joblib.dump(rf, MODEL_PATH)
print(f"Model saved to: {os.path.abspath(MODEL_PATH)}")
