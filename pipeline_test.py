import pandas as pd
import json
import re
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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

# Funktion för att träna Random Forest för att identifiera felaktiga personnummer
def train_random_forest():
    data = [
        ["95", "12", "12", 1, 1],  # Giltigt
        ["75", "09", "07", 1, 1],  # Giltigt
        ["98", "09", "01", 1, 1],  # Giltigt
        ["00", "13", "15", 0, 1],  # Ogiltigt (månad > 12)
        ["95", "02", "30", 0, 1],  # Ogiltigt (30 februari)
        ["05", "05", "04", 1, 1],  # Giltigt
        ["03", "00", "12", 0, 1],  # Ogiltigt (månad = 00)
        ["02", "11", "40", 0, 1],  # Ogiltigt (dag = 40)
        ["90", "06", "32", 0, 1],  # Ogiltigt (dag = 32)
        ["00", "01", "01", 0, 0],  # Ogiltigt (år = 1900)
    ]
    labels = [1, 1, 1, 0, 0, 1, 0, 0, 0, 0]  # 1 = Giltigt, 0 = Ogiltigt

    X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    return model

# Bearbeta JSON-filen och validera
def process_json_and_validate(file_path, model):
    with open(file_path, "r") as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    df["personnummer"] = df["text"].apply(lambda x: x.split(",")[-1].strip())  # Extrahera personnummer
    df[["year", "month", "day", "gender", "anomaly"]] = df["personnummer"].apply(lambda pnr: pd.Series(extract_info(pnr)))

    df["valid_date"] = df.apply(lambda row: is_valid_date(row["year"], row["month"], row["day"]), axis=1)
    df["valid_year"] = df["year"].apply(is_valid_year)

    # Lägg till avvikelse om året är orimligt
    df["anomaly"] = df.apply(lambda row: "Avvikelse: Orimligt årtal" if row["valid_year"] == 0 and row["anomaly"] is None else row["anomaly"], axis=1)
    
    # Flagga ogiltiga personnummer direkt om de har avvikelser
    df["validation_result"] = df.apply(
        lambda row: "Ogiltigt" if row["anomaly"] else "Giltigt", axis=1
    )
    
    return df

# Spara resultat till JSON
def save_results_to_json(df, output_file_path):
    df[["text", "personnummer", "gender", "validation_result", "anomaly"]].to_json(output_file_path, orient="records", indent=4, force_ascii=False)

# Träna modellen
model = train_random_forest()

# Filvägar
input_file_path = "Python/data/testdata.json"
output_file_path = "validation_results.json"

# Bearbeta och validera JSON-filen
validated_df = process_json_and_validate(input_file_path, model)

# Spara resultaten
save_results_to_json(validated_df, output_file_path)

print(f"Resultaten har sparats i {output_file_path}")
