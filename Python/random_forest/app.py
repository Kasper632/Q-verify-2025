from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import os
import torch
import re
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from transformers import DistilBertModel, DistilBertTokenizer

app = Flask(__name__)

DATA_DIR = "wwwroot/uploads"
os.makedirs(DATA_DIR, exist_ok=True)

# Ladda din egen finjusterade DistilBERT-modell
model_path = "Python/AI-models/fine_tuned_distilbert_50k_Email_Name"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertModel.from_pretrained(model_path)

def get_embeddings(text_list):
    """Skapar DistilBERT-embeddings för en lista med texter"""
    inputs = tokenizer(text_list, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():  # Inaktiverar gradientberäkning
        outputs = model(**inputs)

    return outputs.last_hidden_state[:, 0, :].numpy()  # Hämtar [CLS]-tokenens embedding

# Funktion för att normalisera personnummer och extrahera kön
def extract_info(personnummer):
    clean_pnr = re.sub(r'\D', '', personnummer)  # Ta bort icke-numeriska tecken

    if len(clean_pnr) not in [10, 12]:  
        return None, None, None, None, "Avvikelse: Felaktig längd"

    if len(clean_pnr) == 12:
        clean_pnr = clean_pnr[2:]  # Ta bort sekelskiftesprefix

    year, month, day = clean_pnr[:2], clean_pnr[2:4], clean_pnr[4:6]
    last_four = clean_pnr[-4:]

    gender_digit = int(last_four[-2])
    gender = "Kvinna" if gender_digit % 2 == 0 else "Man"

    return year, month, day, gender, None  # Ingen avvikelse om allt är rätt

# Funktion för att kontrollera om årtalet är rimligt
def is_valid_year(year):
    if not year:
        return 0  # Saknar data

    year_int = int(year)
    current_year = datetime.now().year  # Helt årtal (t.ex. 2025)

    # Om årtalet är 00-25 (för 2000-2025), sätt prefix till 20
    if year_int <= current_year % 100:
        century_prefix = 20
    else:
        century_prefix = 19  # Annars är det 1900-talet

    full_year = int(f"{century_prefix}{year_int:02d}")  # Se till att årtalet är två siffror

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

@app.route("/process-file", methods=["POST"])
def process_file():
    # Hitta den senaste uppladdade filen i wwwroot/uploads
    uploaded_files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
    if not uploaded_files:
        return jsonify({"error": "No uploaded files found."}), 400

    # Hitta den senaste filen baserat på ändringstid
    latest_file = max(uploaded_files, key=lambda f: os.path.getmtime(os.path.join(DATA_DIR, f)))
    latest_file_path = os.path.join(DATA_DIR, latest_file)

    # Läs filen baserat på filtyp
    file_extension = latest_file.split('.')[-1].lower()
    if file_extension == "csv":
        df = pd.read_csv(latest_file_path)
    elif file_extension == "json":
        df = pd.read_json(latest_file_path)
    else:
        return jsonify({"error": "Unsupported file type. Please upload a CSV or JSON file."}), 400

    if df.empty:
        return jsonify({"error": "Uploaded file is empty."}), 400

    # Hämta alla kolumnnamn
    columns = df.columns.tolist()

    # Hitta alla textkolumner
    text_columns = df.select_dtypes(include=['object']).columns.tolist()
    if not text_columns:
        return jsonify({"error": "No valid text columns found for embeddings."}), 400

    # Skapa embeddings för varje textkolumn
    column_embeddings = {col: get_embeddings(df[col].astype(str).tolist()) for col in text_columns}

    # Kombinera alla embeddings till en stor matris
    combined_embeddings = np.hstack([column_embeddings[col] for col in text_columns])

    # Random Forest-modell
    rf = RandomForestClassifier(n_estimators=100, random_state=42)

    # Skapa dummy-målvariabel eftersom vi saknar labels
    labels = np.random.randint(0, 2, size=len(df))  # Slumpmässiga 0 eller 1 (anomalier och normala)

    # Träna modellen
    rf.fit(combined_embeddings, labels)

    # Förutsäg anomalier
    predictions = rf.predict(combined_embeddings)

    df["Anomaly"] = predictions  # 0 = Normal, 1 = Anomali

    anomalies = df[df["Anomaly"] == 1].copy()
    anomalies["AnomalyReason"] = ""

    for index, row in anomalies.iterrows():
        reasons = []

        # Beräkna avvikelse per kolumn
        col_deviation = {
            col: np.mean(np.abs(column_embeddings[col][index] - np.mean(column_embeddings[col], axis=0)))
            for col in text_columns
        }

        # Hitta den **genomsnittliga avvikelsen** för alla kolumner
        avg_col_deviation = np.mean(list(col_deviation.values()))

        # Dynamiskt välja endast kolumner med hög avvikelse
        anomalous_cols = [col for col, dev in col_deviation.items() if dev > avg_col_deviation]

        # Bygg dynamisk förklaring
        if len(anomalous_cols) > 1:
            reason = f"{' och '.join(anomalous_cols)} skapar en avvikelse."
        elif len(anomalous_cols) == 1:
            reason = f"{anomalous_cols[0]} har en ovanlig semantisk struktur."
        else:
            reason = "Okänd avvikelse upptäckt."

        anomalies.at[index, "AnomalyReason"] = reason

    anomaly_list = anomalies.to_dict(orient="records")

    # Personnummer-validering
    df["personnummer"] = df["text"].apply(lambda x: x.split(",")[-1].strip())  # Extrahera personnummer
    df[["year", "month", "day", "gender", "anomaly"]] = df["personnummer"].apply(lambda pnr: pd.Series(extract_info(pnr)))

    df["valid_date"] = df.apply(lambda row: is_valid_date(row["year"], row["month"], row["day"]), axis=1)
    df["valid_year"] = df["year"].apply(is_valid_year)

    # Lägg till avvikelse om året är orimligt
    df["anomaly"] = df.apply(lambda row: "Avvikelse: Orimligt årtal" if row["valid_year"] == 0 and row["anomaly"] is None else row["anomaly"], axis=1)

    df["validation_result"] = df.apply(
        lambda row: "Ogiltigt" if row["anomaly"] else "Giltigt", axis=1
    )

    # Lägg till personnummer-anomalier i resultaten
    anomalies_personnummer = df[df["validation_result"] == "Ogiltigt"]

    return jsonify({
        "message": "File processed successfully",
        "columns": columns,
        "text_columns_used": text_columns,
        "anomalies": anomaly_list,
        "personnummer_anomalies": anomalies_personnummer.to_dict(orient="records")
    })

if __name__ == '__main__':
    app.run(debug=True)
