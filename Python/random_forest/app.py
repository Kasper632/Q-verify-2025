from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
import torch
from sklearn.ensemble import RandomForestClassifier
from transformers import DistilBertModel, DistilBertTokenizer

app = Flask(__name__)

DATA_DIR = "wwwroot/uploads"
os.makedirs(DATA_DIR, exist_ok=True)

# Ladda din egen finjusterade DistilBERT-modell
model_path = "Python/AI-models/fine_tuned_distilbert_50k"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertModel.from_pretrained(model_path)

def get_embeddings(text_list):
    """Skapar DistilBERT-embeddings för en lista med texter"""
    inputs = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():  # Inaktiverar gradientberäkning
        outputs = model(**inputs)

    return outputs.last_hidden_state[:, 0, :].numpy()  # Hämtar [CLS]-tokenens embedding

@app.route("/process-file", methods=["POST"])
def process_file():
    # Hitta den senaste uppladdade filen i wwwroot/uploads
    uploaded_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not uploaded_files:
        return jsonify({"error": "No uploaded files found."}), 400

    # Hitta den senaste filen baserat på ändringstid
    latest_file = max(uploaded_files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    latest_file_path = os.path.join(DATA_DIR, latest_file)

    # Läs filen baserat på filtyp
    file_extension = latest_file.split('.')[-1].lower()
    if file_extension == "csv":
        df = pd.read_csv(latest_file_path)
    elif file_extension == "json":
        df = pd.read_json(latest_file_path)
    else:
        return jsonify({"error": "Unsupported file type. Please upload a CSV or JSON file."}), 400

    if df.empty:
        return jsonify({"error": "Uploaded file is empty."}), 400

    # Hämta alla kolumnnamn
    columns = df.columns.tolist()

    # Hitta alla textkolumner
    text_columns = df.select_dtypes(include=['object']).columns.tolist()
    if not text_columns:
        return jsonify({"error": "No valid text columns found for embeddings."}), 400

    # Skapa embeddings för varje textkolumn
    column_embeddings = {col: get_embeddings(df[col].astype(str).tolist()) for col in text_columns}

    # Kombinera alla embeddings till en stor matris
    combined_embeddings = np.hstack([column_embeddings[col] for col in text_columns])

    # Random Forest-modell
    rf = RandomForestClassifier(n_estimators=100, random_state=42)

    # Skapa dummy-målvariabel eftersom vi saknar labels
    labels = np.random.randint(0, 2, size=len(df))  # Slumpmässiga 0 eller 1 (anomalier och normala)

    # Träna modellen
    rf.fit(combined_embeddings, labels)

    # Förutsäg anomalier
    predictions = rf.predict(combined_embeddings)

    df["Anomaly"] = predictions  # 0 = Normal, 1 = Anomali

    anomalies = df[df["Anomaly"] == 1].copy()
    anomalies["AnomalyReason"] = ""

    for index, row in anomalies.iterrows():
        reasons = []

        # Beräkna avvikelse per kolumn
        col_deviation = {
            col: np.mean(np.abs(column_embeddings[col][index] - np.mean(column_embeddings[col], axis=0)))
            for col in text_columns
        }

        # Hitta den **genomsnittliga avvikelsen** för alla kolumner
        avg_col_deviation = np.mean(list(col_deviation.values()))

        # Dynamiskt välja endast kolumner med hög avvikelse
        anomalous_cols = [col for col, dev in col_deviation.items() if dev > avg_col_deviation]

        # Bygg dynamisk förklaring
        if len(anomalous_cols) > 1:
            reason = f"{' och '.join(anomalous_cols)} skapar en avvikelse."
        elif len(anomalous_cols) == 1:
            reason = f"{anomalous_cols[0]} har en ovanlig semantisk struktur."
        else:
            reason = "Okänd avvikelse upptäckt."

        anomalies.at[index, "AnomalyReason"] = reason

    anomaly_list = anomalies.to_dict(orient="records")

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,
        "text_columns_used": text_columns,
        "anomalies": anomaly_list
    })

if __name__ == '__main__':
    app.run(debug=True)
