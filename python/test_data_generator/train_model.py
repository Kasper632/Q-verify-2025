import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score
import joblib
from sentence_transformers import SentenceTransformer

bert_model = SentenceTransformer("all-MiniLM-L6-v2")

# Skapa en funktion för att generera ett realistiskt företagsdataset
def generate_company_data(n_samples=5000, random_seed=None):
    np.random.seed(random_seed)
    
    # Generera normalfördelade data för företag med realistiska intervall
    num_employees = np.random.randint(1, 500, n_samples)  # Antal anställda mellan 1 och 5000
    revenue = np.random.uniform(1e6, 50e6, n_samples)  # Omsättning mellan 1M och 500M SEK
    profit_margin = np.random.uniform(5, 30, n_samples)  # Vinstmarginal mellan 5% och 30%
    credit_rating = np.random.uniform(50, 100, n_samples)  # Kreditvärdighet mellan 50 och 100
    years_in_business = np.random.randint(1, 30, n_samples)  # Antal år i verksamhet mellan 1 och 100
    industries = np.random.choice(['Technology', 'Finance', 'Manufacturing', 'Retail'], n_samples)  # Branscher
    
    # Skapa DataFrame
    data = pd.DataFrame({
        'employees': num_employees,
        'revenue': revenue,
        'profit_margin': profit_margin,
        'credit_rating': credit_rating,
        'years_in_business': years_in_business,
        'industry': industries
    })
    
    # Skapa en "anomali"-kolumn där vi sätter vissa företag som anomalier baserat på extrema värden
    anomalies = (data['revenue'] < 1e7) | (data['credit_rating'] < 60)  # Företag med låg omsättning och låg kreditvärdighet
    data['anomaly'] = anomalies.astype(int)
    
    return data

# Generera företagsdata
company_data = generate_company_data(5000)

industry_embeddings = bert_model.encode(company_data["industry"].tolist())

industry_df = pd.DataFrame(industry_embeddings, columns=[f"industry_{i}" for i in range(industry_embeddings.shape[1])])
x = pd.concat([company_data.drop(columns=['industry']), industry_df], axis=1)

y = company_data["anomaly"]

print("Tränar modellen...")
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(x)
print("Modell tränad!")

# Prediktera resultat för hela datasetet
predictions = model.predict(x)

# Justera prediktionerna (1=normal, -1=anomali) så de matchar y-värdena
predictions_adjusted = [1 if p == -1 else 0 for p in predictions]


# Visa resultat för alla exempel
print("\nResultat för alla exempel:")
for i, (index, row) in enumerate(x.iterrows()):
    # Hämtar den ursprungliga branschen
    industry_text = company_data.loc[index, 'industry']  
    
    # Här skriver vi ut en sammanfattning utan att visa embedding-värdena
    print(f"Exempel {i+1}:")
    print(f"Data: {{'employees': {row['employees']}, 'revenue': {row['revenue']:.2f}, 'profit_margin': {row['profit_margin']:.2f}, 'credit_rating': {row['credit_rating']:.2f}, 'years_in_business': {row['years_in_business']}}}")
    print(f"Bransch (text): {industry_text}")
    print(f"Prediction (1=Normal, -1=Anomali): {predictions[i]}")
    print(f"Prediction justerad (1=Normal, 0=Anomali): {predictions_adjusted[i]}")
    print(f"Verklig etikett (0=Normal, 1=Anomali): {y[i]}")
    print(f"Pricksäkerhet: {'Rätt' if predictions_adjusted[i] == y[i] else 'Fel'}")
    print("-" * 50)

# Beräkna accuracy och skriv ut resultatet i procent
accuracy = accuracy_score(y, predictions_adjusted)

# Skriv ut pricksäkerheten sist
print("\nModellens pricksäkerhet (accuracy) för hela datasetet: {:.2f}%".format(accuracy * 100))
print(f"Antal exempel: {len(x)}")
# Spara modellen
joblib.dump(model, 'python/AI-models/isolation_forest_model.pkl')
x.to_csv("python/data/company_data_traindata.csv", index=False)
