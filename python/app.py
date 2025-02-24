from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from flask_cors import CORS
from sklearn.decomposition import PCA

# Load the Isolation Forest model
model = joblib.load('python/AI-models/isolation_forest_model.pkl')
bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize the Flask app
app = Flask(__name__)
CORS(app) 

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"succsess": False, 'error': 'No file part'})
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"succsess": False, 'error': 'No selected file'})
    
    try:
        file_data = pd.read_csv(file)

        string_columns = file_data.select_dtypes(include=['object']).columns
        for column in string_columns:
            embeddings = bert_model.encode(file_data[column].astype(str).tolist())
            embeddings_df = pd.DataFrame(embeddings, columns=[f"{column}_{i}" for i in range(embeddings.shape[1])])

            file_data = file_data.drop(columns=[column])
            file_data = pd.concat([file_data, embeddings_df], axis=1)

            x = file_data
            predictions = model.predict(x)
            predictions_adjusted = [1 if p == -1 else 0 for p in predictions]
            accuracy = np.mean(predictions_adjusted)*100

        return jsonify({
            "succsess": True,
            'predictions': predictions,
            'accuracy': accuracy,
            "modelAccuracy": model.score(file_data)

        })
    except Exception as e:
        return jsonify({
            "succsess": False,
            'error': str(e)
        })
if __name__ == '__main__':
    app.run(debug=True)
