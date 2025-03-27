# Q-verify 2025

## 🌍 Virtual Environment Setup

För att köra projektet behöver du skapa och aktivera en **virtual environment** samt installera nödvändiga paket.

### 🖥 Windows

```sh
python -m venv .venv  # Skapa en virtuell miljö
.venv\Scripts\activate  # Aktivera miljön
pip install -r Python/requirements.txt  # Installera beroenden
```

### 🍏 macOS & 🐧 Linux

```sh
python3 -m venv .venv  # Skapa en virtuell miljö
source .venv/bin/activate  # Aktivera miljön
pip install -r Python/requirements.txt  # Installera beroenden
```

## Lägga till modellen i projektet

Följ stegen nedan för att lägga till modellen i projektet:

1. **Ladda ner modellfilerna**  
   Hämta följande filer från Teams:

   - `fine_tuned_distilbert_50k_Email_Name`
   - `fine_tuned_distilbert_50k_gender`
   - `maximo_model`

2. **Placera filer i rätt katalog**  
   Lägg till dem i `Python`-mappen i en undermapp som heter `AI-models`.

## Köra projektet

Kör `app.py` som ligger i Python-mappen och sedan `Program.cs`.

## Docker-kommandon

- **`docker-compose up --build`**  
  Bygger om och startar alla tjänster definierade i `docker-compose.yml`-filen. Använd detta när du har gjort ändringar i koden eller Dockerfilerna.

- **`docker-compose start`**  
  Startar containrar som redan har skapats.

- **`docker-compose stop`**  
  Stoppar containrar utan att ta bort dem.

- **`docker-compose down`**  
  Stoppar och tar bort alla containrar, nätverk och volymer skapade av `docker-compose up`. Det här kommandot rensar upp miljön helt.
