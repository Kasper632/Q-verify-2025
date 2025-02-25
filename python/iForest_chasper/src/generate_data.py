import pandas as pd
import random
import os
from sentence_transformers import SentenceTransformer
import numpy as np

def generate_company_data(num_samples=50000, output_dir="data"):
    # Om data redan finns, gör inget
    if os.path.exists(f"{output_dir}/generated_data.csv") and os.path.exists(f"{output_dir}/embeddings.npy"):
        print("Data and embeddings already exist. Skipping generation.")
        return

    # Definiera branscher och marknadsnischer
    industries = {
        "Tech": [
            "AI-driven solutions for automation.",
            "Blockchain-based security services.",
            "Cloud computing and SaaS platforms.",
            "Cybersecurity solutions for enterprises.",
            "E-commerce and digital marketing tools."
        ],
        "Finance": [
            "Investment banking and asset management.",
            "FinTech innovations for digital banking.",
            "Risk assessment and insurance solutions.",
            "Cryptocurrency trading platforms.",
            "AI-powered fraud detection."
        ],
        "Healthcare": [
            "Medical devices and healthcare analytics.",
            "Telemedicine and digital health records.",
            "Pharmaceutical research and drug development.",
            "AI-driven diagnostics and personalized medicine.",
            "Wearable technology for health monitoring."
        ],
        "Retail": [
            "Omnichannel shopping experiences.",
            "E-commerce and supply chain optimization.",
            "Sustainable and eco-friendly product lines.",
            "Customer loyalty and reward programs.",
            "AI-driven product recommendations."
        ],
        "Manufacturing": [
            "Smart factories and IoT automation.",
            "Lean production and waste reduction strategies.",
            "3D printing and rapid prototyping.",
            "Supply chain resilience and risk management.",
            "Industrial robotics and machine learning integration."
        ]
    }

    company_sizes = ["Small", "Medium", "Large"]
    market_niches = [
        "B2B solutions for enterprises.",
        "Direct-to-consumer sales strategy.",
        "Subscription-based revenue model.",
        "Freemium model with premium features.",
        "Government and public sector contracts."
    ]
    
    data = []
    for _ in range(num_samples):
        company_name = f"Company_{random.randint(1000, 9999)}"
        industry = random.choice(list(industries.keys()))
        description = random.choice(industries[industry])
        revenue = round(random.uniform(1e6, 1e9), 2)
        size = random.choice(company_sizes)
        employees = random.randint(10, 5000)
        market_niche = random.choice(market_niches)

        # Samla data
        data.append([company_name, industry, description, market_niche, revenue, size, employees])

    # Skapa DataFrame
    df = pd.DataFrame(data, columns=["Name", "Industry", "Description", "Market_Niche", "Revenue", "Size", "Employees"])
    
    # Spara till CSV
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(f"{output_dir}/generated_data.csv", index=False)
    print(f"Generated {num_samples} company records.")

    # Skapa NLP-embeddings med MiniLM
    model = SentenceTransformer('all-MiniLM-L6-v2')
    descriptions = df["Description"].tolist()
    embeddings = model.encode(descriptions, show_progress_bar=True)

    # Spara embeddings till en fil
    np.save(f"{output_dir}/embeddings.npy", embeddings)
    print("Generated embeddings and saved to data/embeddings.npy")

if __name__ == "__main__":
    generate_company_data()
