import pandas as pd
import re

# Funktion för att normalisera personnummer och extrahera kön
def extract_gender(personnummer):
    # Ta bort alla icke-numeriska tecken (för att hantera bindestreck, punkter, slash)
    clean_pnr = re.sub(r'\D', '', personnummer)

    # Säkerställ att vi har ett personnummer med minst 10 siffror
    if len(clean_pnr) < 10:
        return None, None, None, None  # Ogiltigt

    # Om numret är 12 siffror långt, ta bort de första två siffrorna (århundrade)
    if len(clean_pnr) == 12:
        clean_pnr = clean_pnr[2:]

    # Extrahera år, månad, dag
    year = clean_pnr[:2]
    month = clean_pnr[2:4]
    day = clean_pnr[4:6]
    last_four = clean_pnr[-4:]  # De fyra sista siffrorna

    # Kontrollera att de fyra sista siffrorna finns
    if len(last_four) != 4:
        return None, None, None, None

    # Hämta den näst sista siffran
    gender_digit = int(last_four[-2])

    # Avgör kön
    gender = "Kvinna" if gender_digit % 2 == 0 else "Man"

    return year, month, day, gender

# Testdata med olika format
test_data = pd.DataFrame({
    "personnummer": [
        "19900301-1234",  # Kvinna (4:e sista siffran är 4)
        "20030531-5671",  # Man (4:e sista siffran är 7)
        "8901301235",      # Man (4:e sista siffran är 3)
        "151206-9824",     # Kvinna (4:e sista siffran är 2)
        "780229-6543",     # Man (4:e sista siffran är 3)
        "20220412-8796",   # Kvinna (4:e sista siffran är 6)
    ]
})

# Applicera funktionen på testdatan
test_data[['year', 'month', 'day', 'gender']] = test_data['personnummer'].apply(lambda pnr: pd.Series(extract_gender(pnr)))

print(test_data)
