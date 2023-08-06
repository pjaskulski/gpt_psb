# Ekstrakcja informacji z biogramów postaci historycznych za pomocą skryptów wykorzystujących model GPT-4 przez API

Próbka 250 biogramów z Polskiego Słownika Biograficznego została przetworzona przez model GPT-4 (przez API) w celu wydobycia kilku rodzajów informacji za pomocą odpowiednio skonstruowanych promptów. Rodzaje oczekiwanych informacji:
- dane podstawowe (data urodzenia, miejsce urodzenia, data śmierci, miejsce śmierci, data pochówku, miejsce pochówku)
- relacje rodzinne (wobec głównego bohatera/bohaterki biogramu)
- ważne osoby (spoza krewnych i powinowatych)
- miejsca związane z głównym bohaterem/bohaterką
- instytucje związane z głównym bohaterem/bohaterką
- funkcje, urzędy sprawowane przez głównego bohatera/bohaterkę

Wyniki w formacie JSON w katalogu `output_json_250`