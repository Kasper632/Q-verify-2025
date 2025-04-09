import os
import pandas as pd
from flask import Blueprint, request, jsonify
from AI_models.model_loader import load_maximo_model_and_tokenizer
from services.maximo_validation import predict_maximo

maximo_bp = Blueprint('maximo_bp', __name__)
DATA_DIR = 'wwwroot/uploads'

maximo_model, maximo_tokenizer, device = load_maximo_model_and_tokenizer()

@maximo_bp.route("/analyze-maximo-data", methods=["POST"])
def analyze_maximo_file():
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

    result = predict_maximo(df.to_dict(orient="records"), maximo_model, maximo_tokenizer, device)
    return jsonify(result)


@maximo_bp.route("/analyze-maximo-from-db", methods=["POST"])
def analyze_maximo_from_db():
    try:
        new_data = request.get_json()
        if not new_data:
            return jsonify({"error": "Ingen data mottagen."}), 400

        result = predict_maximo(new_data, maximo_model, maximo_tokenizer, device)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
