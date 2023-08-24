# Ekstrakcja informacji z biogramów postaci historycznych za pomocą skryptów wykorzystujących model GPT-4 przez API

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

Do przetwarzania wykorzystywany jest model GPT-4, który może obsłużyć kontekst o wielkości 8 tys. tokenów (model w wersji 32k obsługujący 4x większe teksty nie jest jeszcze powszechnie dostępny). 256 tokenów zostało zarezerwowanych na odpowiedź (później okazało się, że należy ten parametr zwiększyć dla informacji podstawowych np. do 400, dla innych danych nawet bardziej). Szablon promptu do ekstrakcji podstawowych informacji (przekazywany za każdym razem modelowi razem z treścią biogramu) liczy 1150 tokenów (prompty dotyczące innych rodzajów informacji mogą się różnić ale zwykle jest to ok 900-1200 tokenów). W efekcie na analizowaną treść biogramu pozostaje do wykorzystania około 6200 tokenów. Token w języku angielskim odpowiada przeciętnie 4 znakom tekstu, ze względu na znaki spoza alfabetu łacińskiego, dla tekstów w języku polskim jest to mniejsza liczba, co przekłada się na większy koszt przetwarzania tekstów. **Ograniczenie w wielkości kontekstu (przetwarzanej treści biogramu) jest istotne ze względu na długość biogramów**, w analizowanej próbce 39 z 250 przekracza wspomniane 6200 tokenów, niekiedy znacząco - biogram Stanisława Augusta Poniatowskiego to 78 tys. tokenów. Spowodowało to konieczność, albo przetwarzania biogramów w podziale na części, albo wstępnego skracania biogramów, tak by zawierały głównie fragmenty (zdania) z informacjami, których będzie poszukiwał model. **Drugą przyczyną skracania biogramów może być koszt wykorzystania modelu GPT-4**, który jest dość wysoki. 

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

Po zweryfikowaniu 137 z 250 plików json z danymi podstawowymi, 784 informacje
znalezione przez model były prawdziwe, 35 zaś nie.