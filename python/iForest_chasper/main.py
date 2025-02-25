import os
from src.generate_data import generate_company_data
from src.embeddings import generate_embeddings
from src.isolation_forest import detect_anomalies, load_model, train_and_save_model
import numpy as np

EMBEDDING_FILE = "data/embeddings.npy"

if __name__ == "__main__":
    print("1️⃣ Genererar dataset...")
    generate_company_data()

    print("2️⃣ Skapar NLP-embeddings med MiniLM...")
    generate_embeddings()

    print("3️⃣ Laddar inbäddningar...")
    embeddings = np.load(EMBEDDING_FILE)

    print("4️⃣ Laddar eller tränar Isolation Forest-modellen...")
    model = load_model()
    if model is None:
        print("Ingen tidigare modell hittades. Tränar en ny modell...")
        model = train_and_save_model(embeddings)

    print("5️⃣ Analyserar anomalier med Isolation Forest...")
    detect_anomalies()

    print("✅ Allt klart!")
