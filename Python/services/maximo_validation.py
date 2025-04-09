import torch
from datasets import Dataset

def prepare_maximo_texts(data):
    texts = []
    for entry in data:
        competences = entry.get("competences") or entry.get("Competences") or ""
        pmnum = entry.get("pmnum") or entry.get("Pmnum") or ""
        cxlineroutenr = str(entry.get("cxlineroutenr") or entry.get("Cxlineroutenr") or "")
        location = entry.get("location") or entry.get("Location") or ""
        description = entry.get("description") or entry.get("Description") or ""
        combined = f"competences={competences}; pmnum={pmnum}; cxlineroutenr={cxlineroutenr}; location={location}; description={description}"
        texts.append(combined)
    return texts

def predict_maximo(data, model, tokenizer, device):
    texts = prepare_maximo_texts(data)
    dataset = Dataset.from_dict({"text": texts})
    tokenized = dataset.map(lambda x: tokenizer(x["text"], padding="max_length", truncation=True), batched=True)
    tokenized.set_format(type='torch', columns=['input_ids', 'attention_mask'])

    all_preds = []
    with torch.no_grad():
        for batch in torch.utils.data.DataLoader(tokenized, batch_size=32):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = torch.sigmoid(outputs.logits)
            preds = (probs > 0.02).int().cpu().numpy()
            all_preds.extend(preds)

    column_names = ["competences", "pmnum", "cxlineroutenr", "location"]
    results = []
    for i, entry in enumerate(data):
        pred_fields = all_preds[i].tolist()
        valid = int(sum(pred_fields) == 0)
        anomalies = [col for j, col in enumerate(column_names) if pred_fields[j] == 1]
        results.append({
            "input": entry,
            "predicted_fields": pred_fields,
            "predicted_valid": valid,
            "anomaly_fields": anomalies
        })

    return {
        "message": f"{len(results)} rader analyserade.",
        "anomalies": results
    }
