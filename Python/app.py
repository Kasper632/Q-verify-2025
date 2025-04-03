import os
import pandas as pd
from flask import Flask, request, jsonify
import json
import re
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch
from datetime import datetime
from datasets import Dataset


 
app = Flask(__name__)

# Sökväg för uppladdade filer
DATA_DIR = 'wwwroot/uploads'

# Ladda in modeller och tokenizers för e-post och kön
email_model = DistilBertForSequenceClassification.from_pretrained("./Python/AI-models/fine_tuned_distilbert_50k_Email_Name")
email_tokenizer = DistilBertTokenizer.from_pretrained("./Python/AI-models/fine_tuned_distilbert_50k_Email_Name")

gender_model = DistilBertForSequenceClassification.from_pretrained("./Python/AI-models/fine_tuned_distilbert_50k_gender")
gender_tokenizer = DistilBertTokenizer.from_pretrained("./Python/AI-models/fine_tuned_distilbert_50k_gender")

maximo_model = DistilBertForSequenceClassification.from_pretrained("./Python/AI-models/maximo_model")
maximo_tokenizer = DistilBertTokenizer.from_pretrained("./Python/AI-models/maximo_model")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
maximo_model.to(device)

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
@app.route("/analyze-personal-data", methods=["POST"])
def process_personal_data():
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

def process_maximo_data(file_path):
    # 1. Läs in data (JSON eller CSV)
    if file_path.endswith(".json"):
        with open(file_path, "r", encoding="utf-8") as f:
            new_data = json.load(f)
    elif file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        new_data = df.to_dict(orient="records")
    else:
        raise ValueError("Unsupported file format. Must be .json or .csv")

    if not new_data:
        raise ValueError("Datafilen är tom.")

    # 2. Förbered text för modellinmatning
    texts = []
    for entry in new_data:
        competences = entry.get("competences", "")
        pmnum = entry.get("pmnum", "")
        cxlineroutenr = str(entry.get("cxlineroutenr", ""))
        location = entry.get("location", "")
        description = entry.get("description", "")
        combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
        texts.append(combined)

    # 3. Skapa dataset
    predict_dataset = Dataset.from_dict({"text": texts})
    tokenized = predict_dataset.map(lambda x: maximo_tokenizer(x["text"], padding="max_length", truncation=True), batched=True)
    tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])

    # 4. Prediktion
    all_preds = []
    with torch.no_grad():
        for batch in torch.utils.data.DataLoader(tokenized, batch_size=32):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            outputs = maximo_model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.sigmoid(outputs.logits)
            preds = (probs > 0.02).int().cpu().numpy()
            all_preds.extend(preds)

    # 5. Strukturera resultat
    column_names = ["competences", "pmnum", "cxlineroutenr", "location"]
    results = []
    for i, entry in enumerate(new_data):
        pred_fields = all_preds[i].tolist()
        valid = int(sum(pred_fields) == 0)
        anomalies = [col for j, col in enumerate(column_names) if pred_fields[j] == 1]
        results.append({
            "input": entry,
            "predicted_fields": pred_fields,
            "predicted_valid": valid,
            "anomaly_fields": anomalies
        })

    # 6. Returnera JSON-liknande objekt
    return {
        "message": f"{len(results)} rader processade.",
        "anomalies": results
    }

# Route för att hantera maximo-data
@app.route("/analyze-maximo-data", methods=["POST"])
def process_maximo():
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
        file_result = process_maximo_data(latest_file_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
    response = {
        "message": file_result["message"],
        "anomalies": file_result["anomalies"]
    }
    
    return jsonify(response)

@app.route("/analyze-maximo-from-db", methods=["POST"])
def analyze_maximo_from_db():
    try:
        new_data = request.get_json()
        if not new_data:
            return jsonify({"error": "Ingen data mottagen."}), 400

        # Samma logik som process_maximo_data men utan fil
        texts = []
        for entry in new_data:
            competences = entry.get("competences") or entry.get("Competences") or ""
            pmnum = entry.get("Pmnum", "")
            cxlineroutenr = str(entry.get("Cxlineroutenr", ""))
            location = entry.get("Location", "")
            description = entry.get("Description", "")
            combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
            texts.append(combined)

        predict_dataset = Dataset.from_dict({"text": texts})
        tokenized = predict_dataset.map(
            lambda x: maximo_tokenizer(x["text"], padding="max_length", truncation=True),
            batched=True
        )
        tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])

        all_preds = []
        with torch.no_grad():
            for batch in torch.utils.data.DataLoader(tokenized, batch_size=32):
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                outputs = maximo_model(input_ids=input_ids, attention_mask=attention_mask)
                probs = torch.sigmoid(outputs.logits)
                preds = (probs > 0.02).int().cpu().numpy()
                all_preds.extend(preds)

        column_names = ["competences", "pmnum", "cxlineroutenr", "location"]
        results = []
        for i, entry in enumerate(new_data):
            pred_fields = all_preds[i].tolist()
            valid = int(sum(pred_fields) == 0)
            anomalies = [col for j, col in enumerate(column_names) if pred_fields[j] == 1]
            results.append({
                "input": entry,
                "predicted_fields": pred_fields,
                "predicted_valid": valid,
                "anomaly_fields": anomalies
            })

        return jsonify({
            "message": f"{len(results)} rader analyserade frÃ¥n databasen.",
            "anomalies": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)