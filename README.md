# F1 Analyzer

Aplikacja do przeglądania statystyk Formuły 1 na podstawie danych pobieranych z biblioteki FastF1.  
Dane są ładowane do bazy PostgreSQL, a następnie wykorzystywane przez moduły `stats/*`.

## Funkcje
- GUI z zakładkami:
  - **Tory** (filtr sezonu, sortowanie, statystyki toru)
  - **Kierowcy** (filtr sezonu, sortowanie, statystyki kierowcy)
  - **Zespoły** (filtr sezonu, sortowanie, statystyki zespołu)
- ETL:
  - pełne przeładowanie danych (drop + init + load)
  - częściowe odświeżenie (dociągnięcie nowych sezonów)

## Wymagania
- Python 3.10+ (zalecane)
- PostgreSQL (lokalnie)

## Uruchamianie
1. Skopiuj plik `.env.example` do `.env` i uzupełnij `DATABASE_URL`, np.:
2. Uruchom main.py