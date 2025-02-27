from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from flask_cors import CORS
from sklearn.decomposition import PCA

# Load the Isolation Forest model
model = joblib.load('python/AI-models/isolation_forest_model.pkl')
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize the Flask app

app = Flask(__name__)
CORS(app) 

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
    
    # print(f"Anomalies: {anomalies}")  # Skriver ut anomalier

    anomaly_list = anomalies.to_dict(orient="records")

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,
        "text_column_used": text_column,
        "anomalies": anomaly_list
    })

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"succsess": False, 'error': 'No file part'})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"succsess": False, 'error': 'No selected file'})
    
    try:
        file_data = pd.read_csv(file)

        string_columns = file_data.select_dtypes(include=['object']).columns
        for column in string_columns:
            embeddings = bert_model.encode(file_data[column].astype(str).tolist())
            embeddings_df = pd.DataFrame(embeddings, columns=[f"{column}_{i}" for i in range(embeddings.shape[1])])

            file_data = file_data.drop(columns=[column])
            file_data = pd.concat([file_data, embeddings_df], axis=1)

            x = file_data
            predictions = model.predict(x)
            predictions_adjusted = [1 if p == -1 else 0 for p in predictions]
            accuracy = np.mean(predictions_adjusted)*100

        return jsonify({
            "succsess": True,
            'predictions': predictions,
            'accuracy': accuracy,
            "modelAccuracy": model.score(file_data)

        })
    except Exception as e:
        return jsonify({
            "succsess": False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
