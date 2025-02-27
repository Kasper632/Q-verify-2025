import os
from sentence_transformers import SentenceTransformer

# Ange sökvägen till din lokala modell
EMBEDDING_MODEL = "python/AI-models/restored-model"

def test_local_model():
    # Ladda modellen från den lokala sökvägen
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Exempeltext som ska testas
    test_sentences = [
        "Det här är ett test.",
        "Vi använder en lokal modell för att skapa embeddings.",
        "Sentimentanalys är en viktig del av NLP.",
        "Charles Åkerstedt, charles.akerstedt@gmail.com",
        "Tindra Jutterström, filip.nyden@gmail.com",
        "Filip Nydén, Filip Nydén",
    ]
    
    # Skapa embeddings för test-texten
    embeddings = model.encode(test_sentences, convert_to_numpy=True)
    
    # Skriv ut embeddings för att verifiera att modellen fungerar
    print("Test Embeddings:")
    for sentence, embedding in zip(test_sentences, embeddings):
        print(f"Sentence: {sentence}")
        print(f"Embedding: {embedding[:5]}...")  # Visar de första 5 värdena av varje embedding
    
    # Kontrollera om modellen faktiskt producerar embeddings
    if embeddings is not None and len(embeddings) == len(test_sentences):
        print("\nTestet lyckades! Modellen genererade embeddings för alla meningar.")
    else:
        print("\nTestet misslyckades. Modellen genererade inte embeddings.")

if __name__ == "__main__":
    test_local_model()
