from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

def load_model_and_tokenizer(path, use_cuda=True):
    model = DistilBertForSequenceClassification.from_pretrained(path)
    tokenizer = DistilBertTokenizer.from_pretrained(path)
    device = torch.device("cuda" if torch.cuda.is_available() and use_cuda else "cpu")
    model.to(device)
    return model, tokenizer, device

def load_maximo_model_and_tokenizer(model_path="./Python/AI-models/maximo_model"):
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model, tokenizer, device