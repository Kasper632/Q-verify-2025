from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
from sklearn.ensemble import IsolationForest
from scipy.spatial.distance import euclidean
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

app = Flask(__name__)

DATA_DIR = "wwwroot/uploads"
os.makedirs(DATA_DIR, exist_ok=True)

@app.route("/process-file", methods=["POST"])
def process_file():
    # Hitta den senaste uppladdade filen i wwwroot/uploads
    uploaded_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not uploaded_files:
        return jsonify({"error": "No uploaded files found."}), 400

    # Hitta den senaste filen baserat på ändringstid
    latest_file = max(uploaded_files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    latest_file_path = os.path.join(DATA_DIR, latest_file)

    # Läs den senaste uppladdade filen baserat på filtyp
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

    # Skapa embeddings för varje textkolumn och lagra dem
    model = DistilBertForSequenceClassification.from_pretrained('Python/AI-models/fine_tuned_distilbert_50k', num_labels=2)
    tokenizer = DistilBertTokenizer.from_pretrained('Python/AI-models/fine_tuned_distilbert_50k')    
    column_embeddings = {
        col: model.encode(df[col].astype(str).tolist(), convert_to_numpy=True) for col in text_columns
    }

    # Kombinera alla embeddings till en stor matris
    combined_embeddings = np.hstack([column_embeddings[col] for col in text_columns])

    # Träna Isolation Forest
    iforest = IsolationForest(n_estimators=10000, contamination='auto', random_state=42)
    iforest.fit(combined_embeddings)

    # Identifiera anomalier
    df["Anomaly"] = iforest.predict(combined_embeddings)
    anomalies = df[df["Anomaly"] == -1].copy()

    # Beräkna medelvärde av normaldata för jämförelse
    normal_embeddings = combined_embeddings[df["Anomaly"] == 1]
    avg_embedding = np.mean(normal_embeddings, axis=0) if len(normal_embeddings) > 0 else np.zeros_like(combined_embeddings[0])

    # Lägg till en förklarande orsak till varför en rad är en anomali
    anomalies["AnomalyReason"] = ""

    for index, row in anomalies.iterrows():
        reasons = []

        # Hämta embedding för denna rad
        row_embedding = combined_embeddings[index]
        
        # Beräkna avvikelse per kolumn
        col_deviation = {col: np.mean(np.abs(column_embeddings[col][index] - np.mean(column_embeddings[col], axis=0))) for col in text_columns}
        
        # Hitta den **genomsnittliga avvikelsen** för alla kolumner
        avg_col_deviation = np.mean(list(col_deviation.values()))

        # Dynamiskt välja endast kolumner med hög avvikelse
        anomalous_cols = [col for col, dev in col_deviation.items() if dev > avg_col_deviation * 1]  # 1.2x tröskel

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
