import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest

MODEL_PATH = "models/isolation_forest_model.pkl"

def train_and_save_model(embeddings, contamination=0.05):
    """Tränar Isolation Forest-modellen och sparar den lokalt."""
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(embeddings)
    
    # Skapa mapp om den inte finns
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    joblib.dump(model, MODEL_PATH)
    print(f"Modellen har sparats i {MODEL_PATH}")
    return model

def load_model():
    """Laddar den sparade modellen om den finns, annars returneras None."""
    if os.path.exists(MODEL_PATH):
        print(f"Laddar modellen från {MODEL_PATH}")
        return joblib.load(MODEL_PATH)
    return None

def detect_anomalies(embedding_file="data/embeddings.npy", data_file="data/generated_data.csv"):
    # Ladda embeddings och data
    embeddings = np.load(embedding_file)
    df = pd.read_csv(data_file)

    # Försök ladda modellen, annars träna en ny
    model = load_model()
    if model is None:
        print("Ingen tidigare modell hittades. Tränar en ny modell...")
        model = train_and_save_model(embeddings)

    # Använd modellen för att upptäcka anomalier
    df["Anomaly"] = model.predict(embeddings)

    # Visa anomalier
    anomalies = df[df["Anomaly"] == -1]
    print(f"Detected anomalies: {len(anomalies)}")
    print(anomalies[["Name", "Industry", "Description"]])

    # Spara resultat
    df.to_csv("data/anomaly_results.csv", index=False)
    print("Saved anomaly results to data/anomaly_results.csv")

if __name__ == "__main__":
    detect_anomalies()
