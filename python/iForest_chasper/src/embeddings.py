import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

def generate_embeddings(data_file="data/generated_data.csv", output_file="data/embeddings.npy"):
    df = pd.read_csv(data_file)
    
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Skapa embeddings från företagsbeskrivningar
    embeddings = model.encode(df["Description"].tolist(), convert_to_numpy=True)

    os.makedirs("data", exist_ok=True)
    np.save(output_file, embeddings)
    print(f"Generated embeddings and saved to {output_file}")

if __name__ == "__main__":
    generate_embeddings()
