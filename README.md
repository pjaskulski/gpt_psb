# Ekstrakcja informacji z biogramów postaci historycznych za pomocą skryptów wykorzystujących model GPT-4 przez API

Próbka 250 biogramów z Polskiego Słownika Biograficznego została przetworzona przez model GPT-4 (przez API) w celu wydobycia kilku rodzajów informacji za pomocą odpowiednio skonstruowanych promptów. Rodzaje oczekiwanych informacji:
- dane podstawowe (data urodzenia, miejsce urodzenia, data śmierci, miejsce śmierci, data pochówku, miejsce pochówku)
- relacje rodzinne (wobec głównego bohatera/bohaterki biogramu)
- ważne osoby (spoza krewnych i powinowatych)
- miejsca związane z głównym bohaterem/bohaterką
- instytucje związane z głównym bohaterem/bohaterką
- funkcje, urzędy sprawowane przez głównego bohatera/bohaterkę

Wyniki w formacie JSON w katalogu `output_json_250`, w podziale na poszczególne rodzaje informacji. **W podkatalogu** `combined_results` **wyniki scalone do jednego pliku json dla każdej postaci historycznej**. W podkatalogu `full` wynik eksperymentu z promptem wyciagającym wiele rodzajów informacji jednocześnie. Podkatalog `results_evaluation` zawiera wyniki z oceną poprawności. Podkatalog `extraction_chain` zawiera wynik eksperymentu z wydobywaniem informacji za pomocą funkcji create_extraction_chain z biblioteki langchain. Podkatalogi `summary` (na streszczenia biogramów) i `nicknames` (na pseudonimy i kryptonimy) są na razie puste, biogramy nie były jeszcze przetwarzane w celu wydobywania takich informacji.

W katalogu `src` - źródła skryptów (Python).

W katalogu `prompts` - szabony promptów użytych do wyciągania poszczególnych rodzajów informacji, oraz testowe prompty do ektrakcji wielu informacjei jednocześnie.

W katalogu `short_data_psb_250` wyniki eksperymentów ze skracaniem biogramów na podstawie embeddings i podobieństwa zdań biogramu do zapytań.

W katalogu `emb_psb_250` przykładowe pliki zawierające osadzenia (embeddings) przygotowane za pomocą modelu text-embedding-ada-002 w podziale na zdania.

