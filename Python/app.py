import os
import pandas as pd
from flask import Flask, request, jsonify
import json
import re
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from datetime import datetime

app = Flask(__name__)

# Definiera sökväg för uppladdade filer
DATA_DIR = 'wwwroot/uploads'

# Ladda in modeller och tokenizers
email_model = DistilBertForSequenceClassification.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k")
email_tokenizer = DistilBertTokenizer.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k")

gender_model = DistilBertForSequenceClassification.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_gender")
gender_tokenizer = DistilBertTokenizer.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_gender")

def extract_info(personnummer):
    clean_pnr = re.sub(r'\D', '', personnummer)
    if len(clean_pnr) not in [10, 12]:  
        return None, None, None, None, "Avvikelse: Felaktig längd"
    if len(clean_pnr) == 12:
        clean_pnr = clean_pnr[2:]
    year, month, day = clean_pnr[:2], clean_pnr[2:4], clean_pnr[4:6]
    last_four = clean_pnr[-4:]
    gender_digit = int(last_four[-2])
    gender = "Kvinna" if gender_digit % 2 == 0 else "Man"
    return year, month, day, gender, None

def is_valid_year(year):
    if not year:
        return 0  # Saknar data

    year_int = int(year)
    current_year = datetime.now().year  # Helt årtal (t.ex. 2025)

    if year_int <= current_year % 100:
        century_prefix = 20
    else:
        century_prefix = 19

    full_year = int(f"{century_prefix}{year_int:02d}")

    if full_year < 1925 or full_year > current_year:
        return 0  # Orimligt år

    return 1  # Rimligt år

# Funktion för att validera om datumet är rimligt
def is_valid_date(year, month, day):
    if not year or not month or not day:
        return 0  # Saknar data

    if not (1 <= int(month) <= 12):
        return 0  # Ogiltig månad

    if not (1 <= int(day) <= 31):
        return 0  # Ogiltig dag

    return 1  # Ser rimligt ut

# Uppdaterad funktion för att validera personnummer

def validate_personnummer(pnr):
    # Extrahera information från personnumret
    year, month, day, gender, error = extract_info(pnr)
    
    if error:
        return error  # Returnera fel om längden var felaktig

    # Kontrollera om året är rimligt
    if is_valid_year(year) == 0:
        return "Avvikelse: Ogiltigt år"

    # Kontrollera om datumet är rimligt
    if is_valid_date(year, month, day) == 0:
        return "Avvikelse: Ogiltigt datum"

    return {"year": year, "month": month, "day": day, "gender": gender}

def predict_gender(name):
    inputs = gender_tokenizer([name], padding=True, truncation=True, return_tensors="pt")
    outputs = gender_model(**inputs)
    prediction = outputs.logits.argmax(dim=-1).detach().numpy()[0]
    return "Kvinna" if prediction == 1 else "Man"

def process_uploaded_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")
    if not data:
        raise ValueError("Uploaded file is empty.")
    results = []
    for entry in data:
        combined_data = f"{entry['name']} {entry['email']}"
        inputs = email_tokenizer([combined_data], padding=True, truncation=True, return_tensors="pt")
        outputs = email_model(**inputs)
        prediction = outputs.logits.argmax(dim=-1).detach().numpy()[0]
        personnummer_valid = validate_personnummer(entry['personalnumber'])
        predicted_gender = predict_gender(entry['name'])
        personnummer_gender = personnummer_valid.get("gender", "") if isinstance(personnummer_valid, dict) else "Okänd"
        gender_match = predicted_gender == personnummer_gender
        results.append({
            "name": entry["name"],
            "email": entry["email"],
            "personnummer": entry["personalnumber"],
            "name_email_validity": int(prediction),
            "predicted_gender": predicted_gender,
            "personnummer_gender": personnummer_gender,
            "gender_match": gender_match
        })
    return {"message": "File processed successfully", "anomalies": results}

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
    try:
        file_result = process_uploaded_file(latest_file_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    response = {
        "message": file_result["message"],
        "anomalies": file_result["anomalies"]
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
