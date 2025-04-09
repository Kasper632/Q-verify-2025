import json
from utils.personal_number_validator import validate_personnummer
from utils.gender_prediction import predict_gender
from utils.name_email_validator import validate_name_email

def process_uploaded_file(file_path, email_model, email_tokenizer, gender_model, gender_tokenizer):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

    if not data:
        raise ValueError("Uploaded file is empty.")

    results = []
    for entry in data:
        prediction = validate_name_email(entry['name'], entry['email'], email_model, email_tokenizer)
        personnummer_valid = validate_personnummer(entry['personalnumber'])

        if isinstance(personnummer_valid, dict):
            personnummer_gender = personnummer_valid["gender"]
            predicted_gender = predict_gender(entry['name'], gender_model, gender_tokenizer)
            gender_result = (
                "Godkänt" if personnummer_gender == predicted_gender
                else f"Avvikelse: Namn tyder på {predicted_gender.lower()} men personnummer tyder på {personnummer_gender.lower()}"
            )
        else:
            gender_result = personnummer_valid
            predicted_gender = predict_gender(entry['name'], gender_model, gender_tokenizer)

        results.append({
            "name": entry["name"],
            "email": entry["email"],
            "personnummer": entry["personalnumber"],
            "name_email_validity": prediction,
            "predicted_gender": predicted_gender,
            "personnummer_gender": gender_result
        })

    return {
        "message": "File processed successfully",
        "anomalies": results
    }
