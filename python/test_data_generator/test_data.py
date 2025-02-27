
# RANDOM DATA SET MED KORREKTA DATA > random_dataset.csv
# import os
# import pandas as pd
# import random
# from faker import Faker

# # Initiera Faker för svenska namn/adresser
# fake = Faker("sv_SE")

# # Antal rader i datasetet
# num_rows = 1000
# data = []

# # Skapa katalog om den inte finns
# upload_dir = "wwwroot/uploads"
# os.makedirs(upload_dir, exist_ok=True)

# # Generera random data
# for _ in range(num_rows):
#     name = fake.name()
#     email = fake.email()
#     personal_number = f"{random.randint(1900, 2023)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999)}"
#     street = fake.street_address()

#     data.append([email, name, personal_number, street])

# # Skapa DataFrame och spara filen i uploads-mappen
# df = pd.DataFrame(data, columns=["Email", "Name", "PersonalNumber", "Street"])
# file_path = os.path.join(upload_dir, "random_dataset.csv")
# df.to_csv(file_path, index=False, encoding="utf-8")

# print(f"Dataset saved as '{file_path}'")


##### RANDOM DATASET MED CA 20 % SLUMPMÄSSIGA FEL ######
#### >>>> random_dataset2.csv #####
import pandas as pd
import random
from faker import Faker

fake = Faker("sv_SE")

num_rows = 1000
data = []

for _ in range(num_rows):
    name = fake.name()
    email = fake.email()
    personal_number = f"{random.randint(1900, 2023)}{random.randint(1, 12):02d}{random.randint(1, 28):02d}{random.randint(1000, 9999)}"
    street = fake.street_address()

    # 20% av posterna innehåller fel
    if random.random() < 0.2:
        if random.random() < 0.5:  # 50% chans att e-post är felaktig
            email = email.replace("@", " at ").replace(".", " dot ")
        if random.random() < 0.5:  # 50% chans att personnumret är felaktigt
            personal_number = f"{random.randint(1, 99999)}"
        if random.random() < 0.5:  # 50% chans att namnet är felstavat
            name = "".join(random.sample(name, len(name)))  # Slumpar om bokstäverna i namnet
    
    data.append([email, name, personal_number, street])

df = pd.DataFrame(data, columns=["Email", "Name", "PersonalNumber", "Street"])

# Spara i wwwroot/uploads
output_path = "wwwroot/uploads/random_dataset2.csv"
df.to_csv(output_path, index=False, encoding="utf-8")

print(f"Dataset saved as '{output_path}'")

