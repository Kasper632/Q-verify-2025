import os
import pandas as pd
from flask import Blueprint, request, jsonify
from services.personal_data_handler import process_uploaded_file
from AI_models.model_loader import load_model_and_tokenizer

personal_bp = Blueprint("personal_bp", __name__)
DATA_DIR = "wwwroot/uploads"

# Ladda modeller
email_model, email_tokenizer, _ = load_model_and_tokenizer("./Python/AI-models/fine_tuned_distilbert_50k_Email_Name")
gender_model, gender_tokenizer, _ = load_model_and_tokenizer("./Python/AI-models/fine_tuned_distilbert_50k_gender")

@personal_bp.route("/analyze-personal-data", methods=["POST"])
def process_personal_data():
    uploaded_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not uploaded_files:
        return jsonify({"error": "No uploaded files found."}), 400

    latest_file = max(uploaded_files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    latest_file_path = os.path.join(DATA_DIR, latest_file)

    if not latest_file.endswith((".json", ".csv")):
        return jsonify({"error": "Unsupported file type. Please upload a CSV or JSON file."}), 400

    if latest_file.endswith(".csv"):
        df = pd.read_csv(latest_file_path)
        df.to_json(latest_file_path.replace(".csv", ".json"), orient="records")
        latest_file_path = latest_file_path.replace(".csv", ".json")

    try:
        file_result = process_uploaded_file(
            latest_file_path,
            email_model,
            email_tokenizer,
            gender_model,
            gender_tokenizer
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(file_result)
