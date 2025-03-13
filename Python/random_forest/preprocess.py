import pandas as pd

def preprocess_text_data(df):
    """Extract text columns and create labeled dataset"""
    df["text"] = df["Name"] + " " + df["Email"] + " " + df["Street"]
    texts = df["text"].tolist()
    labels = df["valid"].tolist()
    return texts, labels
