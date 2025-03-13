import json
import os
import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Paths
DATA_PATH = "wwwroot/uploads/allData.json"
MODEL_PATH = "Python/AI-models/random_forest_model3.pkl"

# Load data
with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Combine all text columns into a single "data" column
df["data"] = df.select_dtypes(include=['object']).astype(str).agg(' '.join, axis=1)

# Ensure label column exists
if "valid" not in df.columns:
    raise ValueError("No label column found in dataset.")

labels = df["valid"].values

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Generate embeddings from "data" column
embeddings = model.encode(df["data"].tolist(), convert_to_numpy=True)

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

# import json
# import os
# import joblib
# import pandas as pd
# from sentence_transformers import SentenceTransformer
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import classification_report
# from preprocess import preprocess_text_data

# # Paths
# DATA_PATH = "wwwroot/uploads/allData.json"
# MODEL_PATH = "Python/AI-models/random_forest_model.pkl"

# # Load data
# with open(DATA_PATH, "r", encoding="utf-8") as f:
#     data = json.load(f)

# df = pd.DataFrame(data)

# # Preprocess data & get embeddings
# texts, labels = preprocess_text_data(df)
# sentence_model = SentenceTransformer("Python/AI-models/restored-model")  # Load your fine-tuned model
# embeddings = sentence_model.encode(texts, convert_to_numpy=True)  # 768-dimensional embeddings

# # Train/Test Split
# X_train, X_test, y_train, y_test = train_test_split(embeddings, labels, test_size=0.2, random_state=42)

# # Train Random Forest
# rf = RandomForestClassifier(n_estimators=100, random_state=42)
# rf.fit(X_train, y_train)

# # Evaluate Model
# y_pred = rf.predict(X_test)
# print("Classification Report:\n", classification_report(y_test, y_pred))

# # Save Model
# joblib.dump(rf, MODEL_PATH)
# print(f"Model saved to: {os.path.abspath(MODEL_PATH)}")
