import os
import pandas as pd
from flask import Flask, request, jsonify
import json
import re
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from datetime import datetime

app = Flask(__name__)

# Sökväg för uppladdade filer
DATA_DIR = 'wwwroot/uploads'

# Ladda in modeller och tokenizers för e-post och kön
email_model = DistilBertForSequenceClassification.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_Email_Name")
email_tokenizer = DistilBertTokenizer.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_Email_Name")

gender_model = DistilBertForSequenceClassification.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_gender")
gender_tokenizer = DistilBertTokenizer.from_pretrained("Python/AI-models/fine_tuned_distilbert_50k_gender")

# Funktion för att extrahera och validera personnummer
def extract_info(personnummer):
    clean_pnr = re.sub(r'\D', '', personnummer)

    if len(clean_pnr) not in [10, 12]:
        return None, None, None, None, None, "Avvikelse: Felaktig längd"

    century_prefix = ""
    if len(clean_pnr) == 12:
        century_prefix = clean_pnr[:2]
        clean_pnr = clean_pnr[2:]

    year, month, day = clean_pnr[:2], clean_pnr[2:4], clean_pnr[4:6]
    last_four = clean_pnr[-4:]
    gender_digit = int(last_four[-2])
    gender = "Kvinna" if gender_digit % 2 == 0 else "Man"

    return year, month, day, gender, century_prefix, None

# Funktion för att kontrollera om årtalet är rimligt
def is_valid_year(year, prefix=""):
    if not year:
        return 0

    year_int = int(year)
    current_year = datetime.now().year

    if prefix:
        full_year = int(f"{prefix}{year}")
    else:
        if year_int <= current_year % 100:
            full_year = 2000 + year_int
        else:
            full_year = 1900 + year_int

    if full_year < 1925 or full_year > current_year:
        return 0

    return 1

# Funktion för att validera om månad/dag är rimligt
def is_valid_date(year, month, day):
    if not year or not month or not day:
        return "Avvikelse: Saknar datumkomponent"

    if not (1 <= int(month) <= 12):
        return "Avvikelse: Ogiltig månad"

    if not (1 <= int(day) <= 31):
        return "Avvikelse: Ogiltig dag"

    return None

# Funktion för att validera personnummer
def validate_personnummer(pnr):
    year, month, day, gender, prefix, error = extract_info(pnr)
    
    if error:
        return error

    if is_valid_year(year, prefix) == 0:
        return "Avvikelse: Ogiltigt år"

    date_error = is_valid_date(year, month, day)
    if date_error:
        return date_error

    return {"year": year, "month": month, "day": day, "gender": gender}

# Funktion för att förutsäga kön baserat på namn
def predict_gender(name):
    inputs = gender_tokenizer([name], padding=True, truncation=True, return_tensors="pt")
    outputs = gender_model(**inputs)
    prediction = outputs.logits.argmax(dim=-1).detach().numpy()[0]
    return "Kvinna" if prediction == 1 else "Man"

# Funktion för att förutsäga kön baserat på namn
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

        if isinstance(personnummer_valid, dict):
            personnummer_gender = personnummer_valid["gender"]
            predicted_gender = predict_gender(entry['name'])

            if personnummer_gender != predicted_gender:
                gender_result = f"Avvikelse: Namn tyder på {predicted_gender.lower()} men personnummer tyder på {personnummer_gender.lower()}"
            else:
                gender_result = "Godkänt"
        else:
            gender_result = personnummer_valid  # Här finns en avvikelse
            predicted_gender = predict_gender(entry["name"])

        results.append({
            "name": entry["name"],
            "email": entry["email"],
            "personnummer": entry["personalnumber"],
            "name_email_validity": int(prediction),
            "predicted_gender": predicted_gender,
            "personnummer_gender": gender_result
        })

    return {
        "message": "File processed successfully",
        "anomalies": results
    }

# Route för att ladda upp filer
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
