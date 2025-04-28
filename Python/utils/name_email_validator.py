def validate_name_email(name, email, model, tokenizer):
    combined = f"{name} {email}"
    inputs = tokenizer([combined], padding=True, truncation=True, return_tensors="pt")
    outputs = model(**inputs)
    prediction = outputs.logits.argmax(dim=-1).detach().numpy()[0]
    return int(prediction)
