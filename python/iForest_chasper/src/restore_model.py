from sentence_transformers import SentenceTransformer, models
import torch
from transformers import AutoTokenizer

# Ange rätt checkpoint-mapp
checkpoint_path = "python/AI-models/checkpoint-2568"

# Om din modell är baserad på DistilBERT eller en BERT-modell
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

# Spara tokenizern i rätt mapp så att den kan användas senare
tokenizer.save_pretrained(checkpoint_path)

# Ladda in modellen från checkpointen
word_embedding_model = models.Transformer(checkpoint_path, max_seq_length=256)
pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())

# Skapa SentenceTransformer-modellen
model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

# Spara modellen i ett nytt format
model_save_path = "python/AI-models/restored-model"
model.save(model_save_path)

print(f"✅ Modellen är nu sparad i {model_save_path} och kan användas normalt!")
