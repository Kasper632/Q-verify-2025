# Q-verify 2025

## 🌍 Virtual Environment Setup

För att köra projektet behöver du skapa och aktivera en **virtual environment** samt installera nödvändiga paket.

### 🖥 Windows

```sh
python -m venv .venv  # Skapa en virtuell miljö
.venv\Scripts\activate  # Aktivera miljön
pip install -r requirements.txt  # Installera beroenden
```

### 🍏 macOS & 🐧 Linux

```sh
python3 -m venv .venv  # Skapa en virtuell miljö
source .venv/bin/activate  # Aktivera miljön
pip install -r requirements.txt  # Installera beroenden
```

## Lägga till modellen i projektet

Följ stegen nedan för att lägga till modellen i projektet:

1. **Ladda ner modellfilerna**  
   Hämta följande filer från Teams:

   - `checkpoint-2568`
   - `trained_model2`

2. **Placera filer i rätt katalog**  
   Lägg till dem i `Python`-mappen i en undermapp som heter `AI-models`.

3. **Återställ modellen**  
   Kör följande script för att återställa modellen:

```sh
python Python/isolation_forest/src/restore_model.py
```
