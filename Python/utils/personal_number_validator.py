import re
from datetime import datetime

def extract_info(personnummer):
    clean_pnr = re.sub(r'\D', '', personnummer)

    if len(clean_pnr) not in [10, 12]:
        return None, None, None, None, None, "Avvikelse: Felaktig längd"

    century_prefix = ""
    if len(clean_pnr) == 12:
        century_prefix = clean_pnr[:2]
        clean_pnr = clean_pnr[2:]

    year, month, day = clean_pnr[:2], clean_pnr[2:4], clean_pnr[4:6]
    last_four = clean_pnr[-4:]
    gender_digit = int(last_four[-2])
    gender = "Kvinna" if gender_digit % 2 == 0 else "Man"

    return year, month, day, gender, century_prefix, None

def is_valid_year(year, prefix=""):
    if not year:
        return 0
    year_int = int(year)
    current_year = datetime.now().year
    full_year = int(f"{prefix}{year}") if prefix else (2000 + year_int if year_int <= current_year % 100 else 1900 + year_int)
    return 1 if 1925 <= full_year <= current_year else 0

def is_valid_date(year, month, day):
    if not (year and month and day):
        return "Avvikelse: Saknar datumkomponent"
    if not (1 <= int(month) <= 12):
        return "Avvikelse: Ogiltig månad"
    if not (1 <= int(day) <= 31):
        return "Avvikelse: Ogiltig dag"
    return None

def validate_personnummer(pnr):
    year, month, day, gender, prefix, error = extract_info(pnr)
    if error:
        return error
    if not is_valid_year(year, prefix):
        return "Avvikelse: Ogiltigt år"
    date_error = is_valid_date(year, month, day)
    if date_error:
        return date_error
    return {"year": year, "month": month, "day": day, "gender": gender}
