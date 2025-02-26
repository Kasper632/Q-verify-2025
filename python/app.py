from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

app = Flask(__name__)

MODEL_PATH = "models/isolation_forest_model.pkl"
DATA_DIR = "wwwroot/uploads"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

def load_model():
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def train_and_save_model(embeddings, contamination=0.05):
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(embeddings)
    joblib.dump(model, MODEL_PATH)
    return model

@app.route("/process-file", methods=["POST"])
def process_file():
    # Första steg: Hämta den uppladdade filen
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded."}), 400
    
    # Kontrollera filens format baserat på filändelse
    file_extension = file.filename.split('.')[-1].lower()

    if file_extension == "csv":
        # Läs CSV-fil
        df = pd.read_csv(file)
    elif file_extension == "json":
        # Läs JSON-fil
        df = pd.read_json(file)
    else:
        return jsonify({"error": "Unsupported file type. Please upload a CSV or JSON file."}), 400

    # Hämta alla kolumnnamn
    columns = df.columns.tolist()

    # Första textkolumnen för embeddings
    text_column = df.select_dtypes(include=['object']).columns[0] if len(df.select_dtypes(include=['object']).columns) > 0 else None
    if text_column is None:
        return jsonify({"error": "No valid text column found for embeddings."}), 400

    # Skapa embeddings från textkolumnen
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = model.encode(df[text_column].tolist(), convert_to_numpy=True)

    # Ladda eller träna Isolation Forest
    iforest = load_model()
    if iforest is None:
        iforest = train_and_save_model(embeddings)

    # Identifiera anomalier
    df["Anomaly"] = iforest.predict(embeddings)
    anomalies = df[df["Anomaly"] == -1]
    
    print(f"Anomalies: {anomalies}")  # Skriver ut anomalier
    print(df.head())

    anomaly_list = anomalies.to_dict(orient="records")

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,
        "text_column_used": text_column,
        "anomalies": anomaly_list
    })


if __name__ == '__main__':
    app.run(debug=True)
