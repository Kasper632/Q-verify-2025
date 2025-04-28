def predict_gender(name, model, tokenizer):
    inputs = tokenizer([name], padding=True, truncation=True, return_tensors="pt")
    outputs = model(**inputs)
    prediction = outputs.logits.argmax(dim=-1).detach().numpy()[0]
    return "Kvinna" if prediction == 1 else "Man"
