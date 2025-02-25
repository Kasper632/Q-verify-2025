import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR = "data"
EMBEDDING_FILE = os.path.join(DATA_DIR, "embeddings.npy")

def generate_embeddings(data_file):
    """Laddar data, skapar NLP-embeddings och sparar dem."""
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Filen {data_file} finns inte.")

    df = pd.read_csv(data_file)

    # Välj den första textkolumnen att skapa embeddings på
    text_column = df.select_dtypes(include=["object"]).columns[0]

    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(df[text_column].tolist(), convert_to_numpy=True)

    # Skapa data-mapp och spara embeddings
    os.makedirs(DATA_DIR, exist_ok=True)
    np.save(EMBEDDING_FILE, embeddings)

    return embeddings, text_column
