import os
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest

MODEL_PATH = "models/isolation_forest_model.pkl"

def train_and_save_model(embeddings):
    """Tränar Isolation Forest-modellen och sparar den."""
    model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
    model.fit(embeddings)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    
    return model

def load_model():
    """Laddar en sparad Isolation Forest-modell."""
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

def detect_anomalies(embeddings):
    """Använder Isolation Forest för att identifiera anomalier."""
    model = load_model()
    if model is None:
        raise ValueError("Ingen tränad modell hittades. Träna modellen först.")

    return model.predict(embeddings)
