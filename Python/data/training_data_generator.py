import random
import json

# Lista med namn och e-postadresser (exempeldata)
names = [
    ("Anna Johansson", "anna.johansson@example.com"),
    ("Erik Karlsson", "erik.karlsson@example.com"),
    ("Maria Svensson", "maria.svensson@example.com"),
    ("Johan Andersson", "johan.andersson@example.com"),
    ("Elina Gustafsson", "elina.gustafsson@example.com"),
    ("Lars Pettersson", "lars.pettersson@example.com"),
    ("Sofia Nilsson", "sofia.nilsson@example.com"),
    ("Anders Lindberg", "anders.lindberg@example.com"),
    ("Fatima Al-Mansouri", "fatima.almansouri@example.com"),
    ("Hassan El-Khoury", "hassan.elkhoury@example.com"),
    ("Yuki Tanaka", "yuki.tanaka@example.com"),
    ("Satoshi Nakamura", "satoshi.nakamura@example.com"),
    ("Priya Sharma", "priya.sharma@example.com"),
    ("Arjun Patel", "arjun.patel@example.com"),
    ("Emilia Smith", "emilia.smith@example.com"),
    ("Michael Johnson", "michael.johnson@example.com"),
    ("Isabella Rossi", "isabella.rossi@example.com"),
    ("Lucas Ferrari", "lucas.ferrari@example.com"),
    ("Chen Wei", "chen.wei@example.com"),
    ("Mei Ling", "mei.ling@example.com"),
    ("Omar Haddad", "omar.haddad@example.com"),
    ("Aisha Yusuf", "aisha.yusuf@example.com"),
    ("Carlos Mendoza", "carlos.mendoza@example.com"),
    ("Valentina Rodríguez", "valentina.rodriguez@example.com"),
    ("Jean Dupont", "jean.dupont@example.com"),
    ("Sophie Laurent", "sophie.laurent@example.com"),
    ("Ivan Petrov", "ivan.petrov@example.com"),
    ("Anastasia Smirnova", "anastasia.smirnova@example.com"),
    ("David Cohen", "david.cohen@example.com"),
    ("Rachelle Levy", "rachelle.levy@example.com"),
    ("Ahmed Mostafa", "ahmed.mostafa@example.com"),
    ("Layla Hussein", "layla.hussein@example.com"),
    ("Thiago Oliveira", "thiago.oliveira@example.com"),
    ("Camila Santos", "camila.santos@example.com"),
    ("Dimitris Papadopoulos", "dimitris.papadopoulos@example.com"),
    ("Elena Christodoulou", "elena.christodoulou@example.com"),
    ("Jakub Nowak", "jakub.nowak@example.com"),
    ("Katarzyna Kowalska", "katarzyna.kowalska@example.com"),
]

# Funktion för att generera ett personnummer med korrekt könssiffra
def generate_personal_number(is_female, correct=True):
    year = random.randint(1950, 2015)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Undvika ogiltiga datum
    last_two = random.randint(10, 99)  # Slumpmässiga tre sista siffror

    # Näst sista siffran avgör kön (kvinnor = jämn, män = udda)
    gender_digit = random.choice([0, 2, 4, 6, 8]) if is_female else random.choice([1, 3, 5, 7, 9])
    last_last = random.randint(0, 9)  # Sista siffran
    
    # Om vi ska skapa ett felaktigt personnummer, byt könssiffran till motsatsen
    if not correct:
        gender_digit = random.choice([1, 3, 5, 7, 9]) if is_female else random.choice([0, 2, 4, 6, 8])

    personal_number = f"{year:04d}{month:02d}{day:02d}{last_two}{gender_digit}{last_last}"
    return personal_number

# Skapa dataset med lika många positiva (korrekta) och negativa exempel
data = []
for _ in range(250):  # 250 positiva och 250 negativa
    name, email = random.choice(names)
    is_female = name.split()[0][-1].lower() in ["a", "e", "i"]  # Enkel heuristik för kön

    # Skapa korrekt personnummer
    correct_personal_number = generate_personal_number(is_female, correct=True)

    # Positiv text (allt matchar)
    data.append({
        "text": f"{name}, {email}, {correct_personal_number}",
        "label": 1
    })

    # Skapa ett negativt exempel: varannan gång felaktig e-post eller felaktigt personnummer
    if random.choice([True, False]):  # Bestäm om felet ska vara e-post eller personnummer
        # Skapa en negativ text för felaktig e-post
        wrong_email = random.choice(names)[1]
        while wrong_email == email:
            wrong_email = random.choice(names)[1]
        
        data.append({
            "text": f"{name}, {wrong_email}, {correct_personal_number}",
            "label": 0
        })
    else:
        # Skapa en negativ text för felaktigt personnummer
        wrong_personal_number = generate_personal_number(is_female, correct=False)
        
        data.append({
            "text": f"{name}, {email}, {wrong_personal_number}",
            "label": 0
        })

# Spara till JSON-fil
file_path = "Python/data/träningsdata.json"
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Data har sparats i filen 'träningsdata.json'")
