import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# Skapa en funktion för att generera ett realistiskt företagsdataset
def generate_company_data(n_samples=1000):
    np.random.seed(42)
    
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
company_data = generate_company_data(1000)

# Visa de första raderna i datat
print(company_data.head())

# Spara datat som en CSV-fil för användning i modellen
company_data.to_csv('python/data/company_data.csv', index=False)

# Ladda företagsdata för modellträning
X = company_data[['employees', 'revenue', 'profit_margin', 'credit_rating', 'years_in_business']]
y = company_data['anomaly']

# Träna modellen
model = IsolationForest(contamination=0.1)
model.fit(X)

# Spara modellen
joblib.dump(model, 'python/AI-models/isolation_forest_model.pkl')