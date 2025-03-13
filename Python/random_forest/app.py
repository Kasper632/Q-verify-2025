from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
import joblib
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
app = Flask(__name__)

DATA_DIR = "wwwroot/uploads"
MODEL_PATH = "Python/AI-models/random_forest_model.pkl"

os.makedirs(DATA_DIR, exist_ok=True)

# Load trained model
rf = joblib.load(MODEL_PATH)

model = DistilBertForSequenceClassification.from_pretrained('Python/AI-models/fine_tuned_distilbert_50k', num_labels=2)
tokenizer = DistilBertTokenizer.from_pretrained('Python/AI-models/fine_tuned_distilbert_50k')

@app.route("/process-file", methods=["POST"])
def process_file():
    uploaded_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not uploaded_files:
        return jsonify({"error": "No uploaded files found."}), 400

    latest_file = max(uploaded_files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    latest_file_path = os.path.join(DATA_DIR, latest_file)

    file_extension = latest_file.split('.')[-1].lower()
    if file_extension == "csv":
        df = pd.read_csv(latest_file_path)
    elif file_extension == "json":
        df = pd.read_json(latest_file_path)
    else:
        return jsonify({"error": "Unsupported file type. Please upload a CSV or JSON file."}), 400

    if df.empty:
        return jsonify({"error": "Uploaded file is empty."}), 400

    # Combine all columns into a single "data" column
    df["data"] = df.astype(str).agg(' '.join, axis=1)

    # Generate embeddings
    embeddings = model.encode(df["data"].tolist(), convert_to_numpy=True)

    # Predict using trained model
    predictions = rf.predict(embeddings)
    df["anomalies"] = predictions.tolist()

    # Ensure anomalies key exists to avoid key error
    response = {
        "message": "File processed successfully",
        "anomalies": df[["data", "anomalies"]].to_dict(orient="records")
    }

    if "anomalies" not in response:
        response["anomalies"] = []

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
