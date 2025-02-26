from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

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

    # Hämta alla kolumnnamn
    columns = df.columns.tolist()

    # Första textkolumnen för embeddings
    text_column = df.select_dtypes(include=['object']).columns[0] if len(df.select_dtypes(include=['object']).columns) > 0 else None
    if text_column is None:
        return jsonify({"error": "No valid text column found for embeddings."}), 400

    # Skapa embeddings från textkolumnen
    model = SentenceTransformer("python/AI-models/restored-model")
    embeddings = model.encode(df[text_column].tolist(), convert_to_numpy=True)

    # Träna Isolation Forest direkt utan att spara
    iforest = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    iforest.fit(embeddings)

    # Identifiera anomalier
    df["Anomaly"] = iforest.predict(embeddings)
    anomalies = df[df["Anomaly"] == -1]
    
    print(f"Anomalies: {anomalies}")  # Skriver ut anomalier

    anomaly_list = anomalies.to_dict(orient="records")

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,
        "text_column_used": text_column,
        "anomalies": anomaly_list
    })

if __name__ == '__main__':
    app.run(debug=True)
