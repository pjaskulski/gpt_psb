# Extraction of information from biographies of historical figures with scripts using the GPT-4 model through an API
(Polish version below: [link](#ekstrakcja-informacji-z-biogram%C3%B3w-postaci-historycznych-za-pomoc%C4%85-skrypt%C3%B3w-wykorzystuj%C4%85cych-model-gpt-4-przez-api))

- [Introduction](#introduction)
- [Basic information](#basic-information)
- [Family Relations (of the main protagonist of the biogram)](#family-relations-of-the-main-protagonist-of-the-biogram)
- [Searching for 'important persons' in the biography of the protagonist](#searching-for-important-persons-in-the-biography-of-the-protagonist)
- [Searching for locations associated with the protagonist of the biogram](#searching-for-locations-associated-with-the-protagonist-of-the-biogram)
- [Institutions associated with the protagonist](#institutions-associated-with-the-protagonist)
- [Searching for roles and positions of the biogram protagonist](#searching-for-roles-and-positions-of-the-biogram-protagonist)
- [Remarks](#remarks)
- [Analysis of Result Accuracy](#analysis-of-result-accuracy)
    - [Basic Data](#basic-data)


## Introduction

A sample of 250 biograms from the Polish Biographical Dictionary was processed by the GPT-4 model (via API) to extract several types of information using appropriately constructed prompts. Types of expected information:

Basic details (date of birth, place of birth, date of death, place of death, date of burial, place of burial)
Family relations (related to the main protagonist of the biogram)
Important persons (outside of relatives and in-laws)
Places associated with the main protagonist
Institutions associated with the main protagonist
Roles and positions held by the main protagonist.

The results in the JSON format are in the directory output_json_250, divided by the types of information. **In the subdirectory `combined_results`, the results are merged into one json file for each historical figure**. In the full subdirectory, there is the result of the experiment with a prompt that extracts many types of information simultaneously. The results_evaluation subdirectory contains results with an accuracy assessment. The extraction_chain subdirectory holds the result of the experiment with information extraction using the create_extraction_chain function from the langchain library. The subdirectories summary (for biogram summaries) and nicknames (for pseudonyms and cryptonyms) are currently empty; the biograms have not yet been processed to extract such information.

In the src directory, there are source scripts (Python) for processing biograms, additional scripts for embeddings, function_calling tests, and extraction chain tests from langchain.

In the prompts directory, there are templates of prompts used to extract specific types of information, as well as test prompts for extracting multiple pieces of information simultaneously.

In the short_data_psb_250 directory, there are the results of experiments with shortening biograms based on embeddings and the similarity of biogram sentences to queries.

In the emb_psb_250 directory, there are sample files containing embeddings prepared using the text-embedding-ada-002 model, divided by sentences, which were used for shortening biograms.

The GPT-4 model, which can handle a context of up to 8,000 tokens, is used for processing (the 32k version of the model that handles texts 4 times larger is not yet widely available). 256 tokens have been reserved for the response (it later turned out that this parameter should be increased for basic information, e.g., to 400, and even more for other data). The prompt template for extracting basic information (passed to the model each time along with the biogram content) is 1,150 tokens long (prompts for other types of information may vary, but usually, it's about 900-1,200 tokens). As a result, approximately 6,200 tokens are left for the biogram content to be analyzed. In English, a token corresponds to an average of 4 characters of text; due to characters outside the Latin alphabet, this number is smaller for texts in Polish, leading to higher processing costs. **The limitation in context size (processed biogram content) is significant due to the length of the biograms**; in the analyzed sample, 39 out of 250 exceed the mentioned 6,200 tokens, sometimes significantly - the biogram of Stanisław August Poniatowski is 78,000 tokens. This necessitated either processing the biograms divided into sections or initially shortening the biograms so that they mainly contained fragments (sentences) with the information the model would be seeking. **Another reason for shortening the biograms could be the cost of using the GPT-4 model, which is relatively high**. (The test described here, on a sample of 250 biographies, was mostly funded by the Digital Research Infrastructure for the Arts and Humanities (DARIAH-PL) project conducted at the Institute of History of the Polish Academy of Sciences.)

## Basic information

Since the basic information about the protagonist of the biogram is usually found in the first few and the last dozen or so sentences, this very simple method of limiting context size was adopted - the biogram is divided into sentences (using the spaCy library, model pl_core_news_md) and shortened to the first 10 and last 15 sentences (for a few very long biograms, 35 last sentences were taken). To reduce costs, this shortening procedure was applied to all biograms longer than 25 sentences, which proved to be effective (there were no issues with context size). However, it could lead to worse outcomes - **in some biograms, for instance, information about the exact date of death appeared in the middle of the biogram, not at the end, necessitating re-processing**. The processing results were saved in files in the JSON format (a separate file for each biogram).

Example result ('Gabriel Dyjakiewicz of Kolimata'):
```JSON
 {
        "place_of_birth": {
            "place": "Pułnuszki",
            "note": "pod Dubinkami, województwo wileńskie"
        },
        "place_of_death": {
            "place": "Węgrów"
        },
        "place_of_burial": {
            "place": "brak danych"
        },
        "date_of_birth": {
            "date": "1660"
        },
        "date_of_death": {
            "date": "1724"
        },
        "date_of_burial": {
            "date": "brak danych"
        }
    }
```
## Family Relations (of the main protagonist of the biogram)

A different, though also straightforward, method of shortening biograms was adopted - the first 5 and the last 5 sentences of the biogram are taken into account, as well as those sentences in which there are keywords related to kinship. The spaCy library was used to split into sentences and process them, and base forms of words are compared to an array of keywords ('father', 'mother', 'sister', 'brother', 'son', 'daughter', etc., but also 'marry', 'wed').

Example result (Adam Wacław, Duke of Cieszyn):
```JSON
[
    {
        "family_relation": "ojciec",
        "person": "Wacław Adam"
    },
    {
        "family_relation": "matka",
        "person": "Katarzyna Sydonja"
    },
    {
        "family_relation": "żona",
        "person": "Elżbieta Kettler"
    },
    {
        "family_relation": "teść",
        "person": "Kettler"
    },
    {
        "family_relation": "brat przyrodni",
        "person": "Fryderyk Kazimierz"
    },
    {
        "family_relation": "syn",
        "person": "Fryderyk Wilhelm"
    },
    {
        "family_relation": "córka",
        "person": "Elżbieta Lukrecja"
    }
]
```

## Searching for 'important persons' in the biography of the protagonist

The expected information includes the first name and surname of the person, possibly the date when this person had some relation to the protagonist, and brief additional details about that individual. Example result ('Anna Wanda Lewandowska'):
```JSON
{
  "name": "A. Michałowski",
  "date": "1895",
  "info": "nauczyciel w Konserwatorium Warszawskim"
}
```
Despite the explicit stipulation that the search should exclude relatives and in-laws, and additional post-processing to eliminate relatives based on their description, such individuals can still appear in the results. For example, if the biogram pertains to a king's daughter, and the results include a figure like Zygmunt I the Old described merely as 'king'.

In this case, no shortening method was applied. For longer biograms that exceed the GPT-4 model's limitations, they were processed in parts, and the results were merged into a single JSON file.

## Searching for locations associated with the protagonist of the biogram

The expected result is the name of the location (in the nominative case) and optionally a date. An example result for Sędziwoj of Łęg Kościelny:
```JSON
[
    {
        "place": "Łęg Kościelny",
        "date": "brak danych"
    },
    {
        "place": "Kraków",
        "date": "1412"
    },
    {
        "place": "Rzym",
        "date": "1423"
    },
    {
        "place": "Wyciąże",
        "date": "1431"
    },
    {
        "place": "Poznań",
        "date": "1437"
    },
    {
        "place": "Iłża",
        "date": "brak danych"
    },
    {
        "place": "Bazylea",
        "date": "1441"
    }
]
```
In this case, the shortening was applied to the first 5 sentences, and those sentences (from the subsequent ones) that contained any place names (checked using the spaCy library, with the pl_core_news_lg model). If, after NER analysis for a sentence, at least one entity of type 'placeName' or 'geogName' was found, the sentence was qualified for the shortened version of the biogram intended for GPT.

The challenge is defining what it means for a location to be associated with the main protagonist. Depending on the style in which the biogram was written, the model qualified locations with a relatively loose connection to the protagonist. In the above example, there's Iłża. A sentence from Sędziwoj's biogram reads: "He supported, among others, the handing over of Iłża castle, which belonged to the table properties of the Bishop of Kraków, to the hands of the Castellan of Sandomierz, Jan Oleśnicki." Did the protagonist have any connection to Iłża? In some indirect sense, he did, but perhaps he was never in Iłża.

## Institutions associated with the protagonist

Entire biograms were processed. The expected outcome is a list of institutions along with the locations in which they were situated (if such information was available). Example result for the figure: Cecylia Czesława Orłowska:
```JSON
[
    {
        "institution": "Gimnazjum im. E. Orzeszkowej",
        "place_of_institution": "Łódź"
    },
    {
        "institution": "Związek Młodzieży Komunistycznej",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Komunistyczna Partia Robotnicza Polski",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Komitet Dzielnicowy",
        "place_of_institution": "Łódź"
    },
    {
        "institution": "Komitet Dzielnicowy «Powązki»",
        "place_of_institution": "Warszawa"
    },
    {
        "institution": "Komunistyczny uniwersytet im. J. M. Swierdłowa",
        "place_of_institution": "Moskwa"
    },
    {
        "institution": "Międzynarodówka Komunistyczna",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Fabryka firanek",
        "place_of_institution": "Moskwa"
    }
]
```
Among the problems that could be observed, the model had difficulty distinguishing institutions associated with individuals other than the protagonist appearing in the text. Sometimes a biogram contains a kind of micro-biograms of relatives, see "Stebelski (Stebelskij) Włodzimierz (Władymir)"; in such cases, institutions related to relatives end up on the list of institutions associated with the character.

One could also consider refining the concept of an institution in the query for the model; currently, entities like 'imperial army' or 'court of the Saxon elector' are recognized as institutions.

## Searching for roles and positions of the biogram protagonist

Biograms were processed in their entirety, as information about roles and positions can appear in any part of the text, and there is no reliable method to extract only sentences containing such information. The expected outcome is a list of offices/roles held by the person described in the biogram.
Example result ('Adam Wacław'):

```JSON
[
    { "role_or_office": "książę cieszyński" },
    { "role_or_office": "książę górnogłogowskim" },
    { "role_or_office": "żupan trenczyński" },
    { "role_or_office": "dowódca oddziału w wojsku cesarskim" },
    { "role_or_office": "dowódca Kozaków i Wallonów" },
    { "role_or_office": "radca cesarza" },
    { "role_or_office": "najwyższy dowódca wojskowy" },
    { "role_or_office": "naczelny zarządca całego Śląska, Górnego i Dolnego" }
]
```
A common issue is identifying roles and positions associated with individuals other than the main protagonist appearing in the biogram, especially in longer biograms.

## Remarks

Biograms were processed with **separate queries for each topic** (basic data, family relations, roles, etc.) due to the previously observed lower quality of responses in the case of more complex queries asking for multiple types of information at once. See the result for [Szpręga Teodor](https://github.com/pjaskulski/gpt_psb/blob/main/output_json_250/full/Szprega_Teodor.json) when asking for multiple pieces of information and the result for the same character processed with separate queries: [Szpręgra Teodor](https://github.com/pjaskulski/gpt_psb/blob/main/output_json_250/combined_results/Szprega_Teodor.json).

Tests were also conducted on shortening biograms by filtering sentences using similarity analysis of embeddings (using the 'text-embedding-ada-002' model) to the query content. This allowed the creation of a shortened version of the biogram to the sentences that are most thematically similar to the query, sorted in the order of their original appearance in the biogram text. Sentences were added to the shortened version as long as their token length fit within the limit.

The result of processing the biogram of Stanisław August Poniatowski (78,000 tokens) shortened in the described manner (for a query about family relations) to about 4,000 tokens is:
```JSON
[{"family_relation":"ojciec", "person":"Stanisław Poniatowski"},
 {"family_relation":"matka", "person":"Konstancja Czartoryska"},
 {"family_relation":"brat", "person":"Kazimierz Poniatowski"},
 {"family_relation":"brat", "person":"Andrzej Poniatowski"},
 {"family_relation":"brat", "person":"Michał Poniatowski"},
 {"family_relation":"siostra", "person":"Izabela Branicka"},
 {"family_relation":"bratanek", "person":"Józef Poniatowski"},
 {"family_relation":"córka", "person":"Konstancja Szwanowa"},
 {"family_relation":"syn", "person":"Michał Cichocki"},
 {"family_relation":"córka", "person":"Konstancja Dernałowicz"},
 {"family_relation":"córka", "person":"Izabela Sobolewska"},
 {"family_relation":"syn", "person":"Michał Grabowski"},
 {"family_relation":"syn", "person":"Kazimierz Grabowski"},
 {"family_relation":"syn", "person":"Stanisław Grabowski"},
 {"family_relation":"bratanek", "person":"Stanisław Poniatowski"}
]
```
is comparable to the result achieved by shortening through keywords used earlier during the analysis of 250 biograms (if not better).

## Analysis of Result Accuracy

### Basic Data

In each biography, six pieces of information were sought: the date and place of birth, the date and place of death, and the date and place of burial. **If any information was missing, the model was supposed to return "no data" (which is considered correct information as long as such data actually does not exist in the biography, and false if such data was present)**.

In total, after verification, out of 1500 pieces of information (6 * 250 biographies), **the extraction yielded 1432 (95.5%) true pieces of information and 68 (4.5%) false ones**.

For each of the 6 types of information separately, the results are as follows:

Place of birth: correct: 232, incorrect: 18
Place of death: correct: 229, incorrect: 21
Place of burial: correct: 238, incorrect: 12
Date of birth: correct: 243, incorrect: 7
Date of death: correct: 247, incorrect: 3
Date of burial: correct: 246, incorrect: 4

A large portion of the information extracted from biographies is "no data": 639 out of 1500. Such information is simply missing, especially in biographies of figures from older periods. The number of pieces of information found for each category:

Place of birth: found for 154 out of 250 people (61.6%)
Place of death: for 160 (64%)
Place of burial: 111 (44.4%)
Date of birth: 180 (72%)
Date of death: 230 (92%)
Date of burial: 26 (10.4%)

How does the accuracy of the GPT-4 model look if we only consider the information that was found (i.e., excluding "no data")? The effectiveness of the GPT-4 model looks as follows:

| Type of information | Found | Correct      |
| ---                 | ---   | ---          |
| Place of birth      | 154   | 137 (88.96%) |
| Place of death      | 160   | 141 (88.12%) |
| Burial place        | 111   | 101 (90.99%) |
| Date of birth       | 180   | 177 (98.33%) |
| Date of death       | 230   | 229 (99.57%) |
| Burial date         | 26    | 23 (88.46%)  |
| Total	              | 861   | 808 (93.84%) |

Meanwhile, examining only the cases of no data, the accuracy of the results returned by the model is even higher:

| Type of data   | No data | Correct      |
| ---            | ---     | ---          |
| Place of birth | 96      | 95 (98.96%)  |
| Place of death | 90      | 88 (97.78%)  |
| Burial place   | 139     | 137 (98.56%) |
| Date of birth  | 70      | 65 (92.86%)  |
| Date of death  | 20      | 17 (85.00%)  |
| Burial date    | 224     | 223 (99.55%) |
| Total          | 639     | 625 (97.81%) |

In August 2023, OpenAI made it possible to fine-tune the gpt-3.5-turbo model, and there were opinions that this model, when trained for specific tasks, can match the quality of results of the gpt-4 model. It was decided to verify whether this is actually the case for tasks related to extracting information from texts. The results are available in a separate project: [link](https://github.com/pjaskulski/gpt_historical_text/blob/main/README.md#przetwarzanie-250-biogram%C3%B3w-modelem-gpt-35-turbo-po-fine-tuningu)

---

# Ekstrakcja informacji z biogramów postaci historycznych za pomocą skryptów wykorzystujących model GPT-4 przez API

 - [Wprowadzenie](#wprowadzenie)
 - [Dane podstawowe](#dane-podstawowe)
 - [Relacje rodzinne (głównego bohatera biogramu)](#relacje-rodzinne-głównego-bohatera-biogramu)
 - [Wyszukiwanie 'ważnych osób' w biografii bohatera/bohaterki](#wyszukiwanie-ważnych-osób-w-biografii-bohaterabohaterki)
 - [Wyszukiwanie miejscowości związanych z bohaterem/bohaterką biogramu](#wyszukiwanie-miejscowości-związanych-z-bohaterembohaterką-biogramu)
 - [Instytucje związane z bohaterem/bohaterką](#instytucje-związane-z-bohaterembohaterką)
 - [Wyszukiwanie funkcji i urzędów bohatera/bohaterki biogramu](#wyszukiwanie-funkcji-i-urzędów-bohaterabohaterki-biogramu)
 - [Uwagi](#uwagi)
 - [Analiza poprawności wyników](#analiza-poprawności-wyników)
    - [Dane podstawowe](#dane-podstawowe-1)

## Wprowadzenie

Próbka 250 biogramów z Polskiego Słownika Biograficznego została przetworzona przez model GPT-4 (przez API) w celu wydobycia kilku rodzajów informacji za pomocą odpowiednio skonstruowanych promptów. Rodzaje oczekiwanych informacji:
- dane podstawowe (data urodzenia, miejsce urodzenia, data śmierci, miejsce śmierci, data pochówku, miejsce pochówku)
- relacje rodzinne (wobec głównego bohatera/bohaterki biogramu)
- ważne osoby (spoza krewnych i powinowatych)
- miejsca związane z głównym bohaterem/bohaterką
- instytucje związane z głównym bohaterem/bohaterką
- funkcje, urzędy sprawowane przez głównego bohatera/bohaterkę

Wyniki w formacie JSON w katalogu `output_json_250`, w podziale na poszczególne rodzaje informacji. **W podkatalogu** `combined_results` **wyniki scalone do jednego pliku json dla każdej postaci historycznej**. W podkatalogu `full` wynik eksperymentu z promptem wyciągającym wiele rodzajów informacji jednocześnie. Podkatalog `results_evaluation` zawiera wyniki z oceną poprawności. Podkatalog `extraction_chain` zawiera wynik eksperymentu z wydobywaniem informacji za pomocą funkcji create_extraction_chain z biblioteki langchain. Podkatalogi `summary` (na streszczenia biogramów) i `nicknames` (na pseudonimy i kryptonimy) są na razie puste, biogramy nie były jeszcze przetwarzane w celu wydobywania takich informacji.

W katalogu `src` - źródła skryptów (Python) do przetwarzania biogramów, dodatkowe skrypty do embeddings, testy function_calling i extraction chain z langchain.

W katalogu `prompts` - szablony promptów użytych do wyciągania poszczególnych rodzajów informacji, oraz testowe prompty do ekstrakcji wielu informacji jednocześnie.

W katalogu `short_data_psb_250` wyniki eksperymentów ze skracaniem biogramów na podstawie embeddings i podobieństwa zdań biogramu do zapytań.

W katalogu `emb_psb_250` przykładowe pliki zawierające osadzenia (embeddings) przygotowane za pomocą modelu text-embedding-ada-002 w podziale na zdania, które posłużyły do skracania biogramów.

Do przetwarzania wykorzystywany jest model GPT-4, który może obsłużyć kontekst o wielkości 8 tys. tokenów (model w wersji 32k obsługujący 4x większe teksty nie jest jeszcze powszechnie dostępny). 256 tokenów zostało zarezerwowanych na odpowiedź (później okazało się, że należy ten parametr zwiększyć dla informacji podstawowych np. do 400, dla innych danych nawet bardziej). Szablon promptu do ekstrakcji podstawowych informacji (przekazywany za każdym razem modelowi razem z treścią biogramu) liczy 1150 tokenów (prompty dotyczące innych rodzajów informacji mogą się różnić ale zwykle jest to ok 900-1200 tokenów). W efekcie na analizowaną treść biogramu pozostaje do wykorzystania około 6200 tokenów. Token w języku angielskim odpowiada przeciętnie 4 znakom tekstu, ze względu na znaki spoza alfabetu łacińskiego, dla tekstów w języku polskim jest to mniejsza liczba, co przekłada się na większy koszt przetwarzania tekstów. **Ograniczenie w wielkości kontekstu (przetwarzanej treści biogramu) jest istotne ze względu na długość biogramów**, w analizowanej próbce 39 z 250 przekracza wspomniane 6200 tokenów, niekiedy znacząco - biogram Stanisława Augusta Poniatowskiego to 78 tys. tokenów. Spowodowało to konieczność, albo przetwarzania biogramów w podziale na części, albo wstępnego skracania biogramów, tak by zawierały głównie fragmenty (zdania) z informacjami, których będzie poszukiwał model. **Drugą przyczyną skracania biogramów może być koszt wykorzystania modelu GPT-4**, który jest dość wysoki. (Opisywany test na próbce 250 biogramów został w większości sfinansowany w ramach projektu „Cyfrowa infrastruktura badawcza dla humanistyki i nauk o sztuce DARIAH-PL” (Digital Research Infrastructure for the Arts and Humanities) prowadzonego w Instytucie Historii PAN).

## Dane podstawowe

Ponieważ informacje podstawowe o bohaterze/bohaterce biogramu znajdują się zwykle w pierwszych kilku i kilkunastu ostatnich zdaniach przyjęto właśnie taki bardzo prosty sposób ograniczania wielkości kontekstu - biogram dzielony jest na zdania (biblioteką spaCy, model pl_core_news_md) i skracany do 10 pierwszych i ostatnich 15 zdań (w przypadku kilku bardzo długich biogramów przyjęto 35 ostatnich zdań). Ze względu na chęć ograniczenia kosztów procedurę skracania zastosowano do wszystkich biogramów dłuższych niż 25 zdań, co okazało się skuteczne (nie było problemów z wielkością kontekstu), ale mogło prowadzić do gorszych wyników - **w niektórych biogramach informacja np. o dokładnej dacie śmierci występowała jednak w środku biogramu, nie na końcu, co spowodowało konieczność powtórnego przetwarzania**. Wyniki przetwarzania zostały zapisane w plikach w formacie JSON (osobny plik dla każdego biogramu).

Przykład wyniku ('Gabriel Dyjakiewicz z Kolimata'):

```JSON
 {
        "place_of_birth": {
            "place": "Pułnuszki",
            "note": "pod Dubinkami, województwo wileńskie"
        },
        "place_of_death": {
            "place": "Węgrów"
        },
        "place_of_burial": {
            "place": "brak danych"
        },
        "date_of_birth": {
            "date": "1660"
        },
        "date_of_death": {
            "date": "1724"
        },
        "date_of_burial": {
            "date": "brak danych"
        }
    }
```

## Relacje rodzinne (głównego bohatera biogramu)

Przyjęto inny, choć również prosty, sposób skracania biogramów - uwzględnianych jest pierwszych 5 i ostatnich 5 zdań z biogramu, oraz te zdania w których znajdują się słowa kluczowe związane z pokrewieństwem. Do podziału na zdania i przetwarzania zdań wykorzystana została biblioteka spaCy, porównywane są formy podstawowe wyrazów z tablicą słów kluczowych ('ojciec', 'matka', 'siostra', 'brat', 'syn', 'córka' itp., ale też 'ożenić', 'poślubić').

Przykład wyniku (Adam Wacław, książę cieszyński):
```JSON
[
    {
        "family_relation": "ojciec",
        "person": "Wacław Adam"
    },
    {
        "family_relation": "matka",
        "person": "Katarzyna Sydonja"
    },
    {
        "family_relation": "żona",
        "person": "Elżbieta Kettler"
    },
    {
        "family_relation": "teść",
        "person": "Kettler"
    },
    {
        "family_relation": "brat przyrodni",
        "person": "Fryderyk Kazimierz"
    },
    {
        "family_relation": "syn",
        "person": "Fryderyk Wilhelm"
    },
    {
        "family_relation": "córka",
        "person": "Elżbieta Lukrecja"
    }
]
```

## Wyszukiwanie 'ważnych osób' w biografii bohatera/bohaterki

Oczekiwane informacje to imię i nazwisko osoby, ewentualnie data kiedy dana osoba miała jakiś związek z bohaterem/bohaterką, oraz krótkie dodatkowe informacje o danej osobie, przykład wyniku ('Anna Wanda Lewandowska'):

```JSON
{
  "name": "A. Michałowski",
  "date": "1895",
  "info": "nauczyciel w Konserwatorium Warszawskim"
}
```

Mimo wyraźnego zastrzeżenia, że wyszukiwanie ma pomijać krewnych i powinowatych, oraz dodatkowego post-processingu eliminującego krewnych na podstawie opisu, takie osoby mogą się zdarzyć w wynikach, jeżeli np. biogram dotyczy córki króla, a w wynikach pojawi się postać Zygmunt I Stary opisany tylko jako 'król'.

W tym przypadku nie zastosowano żadnej metody skracania, w przypadku dłuższych biogramów przekraczających ograniczenia modelu GPT-4 były one przetwarzane w częściach a wyniki scalane do jednego pliku json.

## Wyszukiwanie miejscowości związanych z bohaterem/bohaterką biogramu

Oczekiwany wynik to nazwa miejscowości (w mianowniku) oraz opcjonalnie data. Przykładowy wynik dla Sędziwoja z Łęgu Kościelnego:

```JSON
[
    {
        "place": "Łęg Kościelny",
        "date": "brak danych"
    },
    {
        "place": "Kraków",
        "date": "1412"
    },
    {
        "place": "Rzym",
        "date": "1423"
    },
    {
        "place": "Wyciąże",
        "date": "1431"
    },
    {
        "place": "Poznań",
        "date": "1437"
    },
    {
        "place": "Iłża",
        "date": "brak danych"
    },
    {
        "place": "Bazylea",
        "date": "1441"
    }
]
```
W tym przypadku zastosowano skracanie do 5 pierwszych zdań, oraz tych zdań (z kolejnych), które zawierały jakieś nazwy miejscowości (sprawdzane biblioteką spaCy, modelem pl_core_news_lg). Jeżeli po analizie NER dla zdania znaleziono choć jedną encję typu 'placeName' lub 'geogName' zdanie było kwalifikowane do skróconej wersji biogramu przeznaczonej dla GPT.

Problemem jest definicja co to znaczy miejsce związane z głównym bohaterem/bohaterką, zależnie od stylu w którym napisano biogram model kwalifikował do wyników miejscowości o dość luźnym związku z bohaterem. W powyższym przykładzie jest np. Iłża. A zdanie z biogramu Sędziwoja brzmi: "Poparł on m. in. oddanie w ręce kaszt. sandomierskiego Jana Oleśnickiego zamku Iłży, należącego do dóbr stołowych biskupa krakowskiego.". Miał bohater jakiś związek z Iłżą? W jakimś pośrednim sensie miał, ale być może nigdy w Iłży nie był.

## Instytucje związane z bohaterem/bohaterką

Przetwarzane były całe biogramy. Oczekiwany efekt to lista instytucji wraz z miejscowościami, w których się mieściły (o ile była taka informacja). Przykład wyniku dla postaci: Orłowska Cecylia Czesława:

```JSON
[
    {
        "institution": "Gimnazjum im. E. Orzeszkowej",
        "place_of_institution": "Łódź"
    },
    {
        "institution": "Związek Młodzieży Komunistycznej",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Komunistyczna Partia Robotnicza Polski",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Komitet Dzielnicowy",
        "place_of_institution": "Łódź"
    },
    {
        "institution": "Komitet Dzielnicowy «Powązki»",
        "place_of_institution": "Warszawa"
    },
    {
        "institution": "Komunistyczny uniwersytet im. J. M. Swierdłowa",
        "place_of_institution": "Moskwa"
    },
    {
        "institution": "Międzynarodówka Komunistyczna",
        "place_of_institution": "brak danych"
    },
    {
        "institution": "Fabryka firanek",
        "place_of_institution": "Moskwa"
    }
]
```

Wśród problemów, które można było zauważyć, trudność modelowi sprawia odróżnienie instytucji związanych z innymi niż bohater/bohaterka osobami występującymi w tekście. Niekiedy biogram zawiera swego rodzaju mikrobiogramy krewnych zob. "Stebelski (Stebelskij) Włodzimierz (Władymir)", wówczas instytucje dotyczące krewnych trafiają na listę instytucji związanych z postacią.
Można by się też zastanowić nad sprecyzowaniem pojęcia instytucji w zapytaniu dla modelu, obecnie za instytucję uznawane jest np. 'wojsko cesarskie' czy 'dwór elektora saskiego'.

## Wyszukiwanie funkcji i urzędów bohatera/bohaterki biogramu

Biogramy były przetwarzane w całości, informacje o funkcji i urzędzie mogą pojawiać się w każdej części tekstu, nie ma też wiarygodnej metody wyodrębniającej same zdania zawierające tego typu informacje. Oczekiwany wynik to lista urzędów/funkcji pełnionych przez opisywaną w biogramie postać.
Przykład wyniku ('Adam Wacław'):

```JSON
[
    { "role_or_office": "książę cieszyński" },
    { "role_or_office": "książę górnogłogowskim" },
    { "role_or_office": "żupan trenczyński" },
    { "role_or_office": "dowódca oddziału w wojsku cesarskim" },
    { "role_or_office": "dowódca Kozaków i Wallonów" },
    { "role_or_office": "radca cesarza" },
    { "role_or_office": "najwyższy dowódca wojskowy" },
    { "role_or_office": "naczelny zarządca całego Śląska, Górnego i Dolnego" }
]
```

Częstym problemem jest znajdowanie funkcji i urzędów związanych z inną niż główny bohater/bohaterka osobą występującą w biogramie, dotyczy to głównie biogramów dłuższych.

## Uwagi

Biogramy przetwarzane były **osobnymi zapytaniami dla każdego tematu** (dane podstawowe, relacje rodzinne, funkcje itp) ze względu na obserwowaną wcześniej gorszą jakość odpowiedzi w przypadku bardziej skomplikowanych pytań o wiele rodzajów informacji naraz. Zob. wynik dla [Szpręga Teodor](https://github.com/pjaskulski/gpt_psb/blob/main/output_json_250/full/Szprega_Teodor.json) w przypadku pytań o wiele informacji i wynik dla tej samej postaci przetwarzanej osobnymi pytaniami: [Szpręgra Teodor](https://github.com/pjaskulski/gpt_psb/blob/main/output_json_250/combined_results/Szprega_Teodor.json).

Przeprowadzono też testy **skracania biogramów poprzez filtrowanie zdań za pomocą analizy podobieństw osadzeń (embeddings, użyty model 'text-embedding-ada-002') do treści zapytania. To pozwoliło na utworzenie skróconej wersji biogramu do zdań ktore są najbardziej podobne tematycznie do pytania, posortowanych w kolejności oryginalnego występowania w tekście biogramu. Zdania były dodawane do wersji skróconej dopóki ich długość w tokenach mieściła się w limicie.

Wynik przetwarzania biogramu Stanisława Augusta Poniatowskiego (78 tys. tokenów) skróconego w opisany sposób (dla pytania o relacje rodzinne) do  ok 4 tys. tokenów:

```JSON
[{"family_relation":"ojciec", "person":"Stanisław Poniatowski"},
 {"family_relation":"matka", "person":"Konstancja Czartoryska"},
 {"family_relation":"brat", "person":"Kazimierz Poniatowski"},
 {"family_relation":"brat", "person":"Andrzej Poniatowski"},
 {"family_relation":"brat", "person":"Michał Poniatowski"},
 {"family_relation":"siostra", "person":"Izabela Branicka"},
 {"family_relation":"bratanek", "person":"Józef Poniatowski"},
 {"family_relation":"córka", "person":"Konstancja Szwanowa"},
 {"family_relation":"syn", "person":"Michał Cichocki"},
 {"family_relation":"córka", "person":"Konstancja Dernałowicz"},
 {"family_relation":"córka", "person":"Izabela Sobolewska"},
 {"family_relation":"syn", "person":"Michał Grabowski"},
 {"family_relation":"syn", "person":"Kazimierz Grabowski"},
 {"family_relation":"syn", "person":"Stanisław Grabowski"},
 {"family_relation":"bratanek", "person":"Stanisław Poniatowski"}
]
```

jest porównywalny z wynikiem osiągniętym przez skracanie poprzez słowa kluczowe zastosowanym wcześniej podczas analizy 250 biogramów (o ile nie lepszy)

## Analiza poprawności wyników

### Dane podstawowe

W każdym z biogramów poszukiwano sześciu informacji: daty i miejsca urodzenia, daty i miejsca śmierci, daty i miejsca pochówku.
**W przypadku braku jakiejś informacji model miał zwrócić "brak danych" (co jest uznawane za informację poprawną o ile faktycznie takich danych nie ma w biogramie, fałszywą jeżeli jednak takie dane były)**.

Ogółem po weryfikacji, na 1500 informacji (6 * 250 biogramów) **ekstrakcja informacji przyniosła 1432 (95.5%) informacje prawdziwe i 68 (4.5%) fałszywych**.

Dla każdej z 6 rodzajów informacji z osobna wyniki wyglądają następująco:

- miejsce urodzenia: poprawnie: 232, niepoprawnie: 18
- miejsce śmierci: poprawnie: 229, niepoprawnie: 21
- miejsce pochówku: poprawnie: 238, niepoprawnie: 12
- data urodzenia: poprawnie: 243 niepoprawnie: 7
- data śmierci: poprawnie: 247 niepoprawnie: 3
- data pochówku: poprawnie: 246 niepoprawnie: 4

Duża część informacji pobranych z biogramów to "brak danych": 639 z 1500 (42.6%), takich informacji - szczególnie w biogramach postaci ze starszych okresów - po prostu brakuje. Liczba faktycznie znalezionych informacji (czyli pomijając "brak danych") dla każdej z kategorii informacji:

- Miejsce urodzenia: znaleziono dla 154 z 250 postaci (61.6%)
- Miejsce śmierci: dla 160 (64%)
- Miejsce pochówku: 111 (44.4%)
- Data urodzenia: 180 (72%)
- Data śmierci: 230 (92%)
- Data pochówku: 26 (10.4%)

Jak wygląda poprawność modelu gpt-4, jeżeli brać pod uwagę tylko te informacje, które udało się znaleźć (czyli pomijając "brak danych"), skuteczność modelu gpt-4 po wygląda następująco:

| Rodzaj informacji | Znaleziono | Poprawnie    |
| ---               | ---        | ---          |
| Miejsce urodzenia | 154        | 137 (88.96%) |
| Miejsce śmierci   | 160        | 141 (88.12%) |
| Miejsce pochówku  | 111        | 101 (90.99%) |
| Data urodzenia    | 180        | 177 (98.33%) |
| Data śmierci      | 230        | 229 (99.57%) |
| Data pochówku     | 26         | 23 (88.46%)  |
| Ogółem            | 861        | 808 (93.84%) |

Z kolei badając tylko przypadki braku danych, poprawność wyników zwracanych przez model, jest jeszcze większa:

| Rodzaj danych     | Brak danych dla | Poprawnie    |
| ---               | ---             | ---          |
| Miejsce urodzenia | 96              | 95 (98.96%)  |
| Miejsce śmierci   | 90              | 88 (97.78%)  |
| Miejsce pochówku  | 139             | 137 (98.56%) |
| Data urodzenia    | 70              | 65 (92.86%)  |
| Data śmierci      | 20              | 17 (85.00%)  |
| Data pochówku     | 224             | 223 (99.55%) |
| Ogółem            | 639             | 625 (97.81%) |

Ponieważ w sierpniu 2023 firma OpenAI udostępniła możliwość douczania (fine-tuningu) modelu gpt-3.5-turbo i pojawiły się opinie, że model ten przyuczony do konkretnych zadań może dorównywać w jakości wyników modelowi gpt-4 postanowiono zweryfikować czy tak faktycznie jest w przypadku zadań dotyczących ekstrakcji informacji z tekstów. Wyniki dostępne są w osobnym projekcie: [link](https://github.com/pjaskulski/gpt_historical_text/blob/main/README.md#przetwarzanie-250-biogram%C3%B3w-modelem-gpt-35-turbo-po-fine-tuningu).