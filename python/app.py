from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

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

if __name__ == '__main__':
    app.run(debug=True)
