from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest

# Ladda modellen
model = joblib.load('python/AI-models/isolation_forest_model.pkl')

# Läs in data för att beräkna medelvärde och standardavvikelse
df = pd.read_csv('python/data/company_data.csv')
average_values = df.mean(numeric_only=True).to_dict()
std_values = df.std(numeric_only=True).to_dict()

app = Flask(__name__)

@app.route('/predict', methods=["POST"])
def predict():
    try:
        # Hämta inmatad data från form
        input_data = {
            "employees": int(request.form["employees"]),
            "revenue": float(request.form["revenue"]),
            "profit_margin": float(request.form["profit_margin"]),
            "credit_rating": float(request.form["credit_rating"]),
            "years_in_business": int(request.form["years_in_business"])
        }

        # Omvandla till numpy-array för prediktion
        input_array = np.array(list(input_data.values())).reshape(1, -1)

        # Gör en prediktion (-1 = anomali, 1 = normal)
        prediction = model.predict(input_array)
        result = "Anomaly" if prediction[0] == -1 else "Normal"

        # Beräkna avvikelse och Z-score för varje värde
        analysis_results = {}
        for key, value in input_data.items():
            avg_value = round(average_values[key], 2)
            std_dev = round(std_values[key], 2)
            deviation = round(value - avg_value, 2)
            z_score = round((value - avg_value) / std_dev, 2) if std_dev != 0 else 0  # Undvik division med 0

            analysis_results[key] = {
                "value": value,
                "avg": avg_value,
                "std_dev": std_dev,
                "deviation": deviation,
                "z_score": z_score
            }

        # Returnera JSON med prediktionen och analysen
        return jsonify({
            "result": result,
            "analysis_results": analysis_results
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    
# Här börjar iForest

MODEL_PATH = "models/isolation_forest_model.pkl"
DATA_DIR = "data"

# Skapa mappar vid behov
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

# Ladda eller träna modellen
def load_model():
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def train_and_save_model(embeddings, contamination=0.05):
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(embeddings)
    joblib.dump(model, MODEL_PATH)
    return model

@app.route("/process-file", methods=["POST"])
def process_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join(DATA_DIR, file.filename)
    file.save(file_path)

    df = pd.read_csv(file_path)

    # Hämta alla kolumnnamn dynamiskt
    columns = df.columns.tolist()
    for c in columns:
        print(c)
    
    # För att skapa embeddings på den första textkolumnen
    text_column = df.select_dtypes(include=['object']).columns[0]  # Välj första textkolumnen

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

    anomaly_list = anomalies.to_dict(orient="records")

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,  # Skickar de dynamiskt hämtade kolumnnamnen
        "text_column_used": text_column,
        "anomalies": anomaly_list
    })

if __name__ == '__main__':
    app.run(debug=True)
