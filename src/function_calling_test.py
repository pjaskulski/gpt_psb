""" function calling test """
import openai
import os
from dotenv import load_dotenv
from pathlib import Path


# api key
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


function_basic_info = [
    {
        "name": "ekstrakcja_podstawowych_danych",
        "description": "wyszukiwanie podstawowych danych: miejsca urodzenia, miejsca śmierci, miejsca pochówku, daty urodzenia, daty śmierci i daty pochówku głównego bohatera/bohaterki",
        "parameters": {
            "type": "object",
            "properties": {
                "place_of_birth": {
                    "type": "string",
                    "description": "miejsce urodzenia głównego bohatera/bohaterki tekstu"
                },
                "place_of_death": {
                    "type": "string",
                    "description": "miejsce śmierci głównego bohatera/bohaterki tekstu"
                },
                "place_of_burial":{
                    "type": "string",
                    "description": "miejsce pochówku głównego bohatera/bohaterki tekstu"
                },
                "date_of_birth": {
                    "type": "string",
                    "format": "date",
                    "description": "data urodzin głównego bohatera/bohaterki tekstu"
                },
                "date_of_death":{
                    "type": "string",
                    "format": "date",
                    "description": "data śmierci głównego bohatera/bohaterki tekstu"
                },
                "date_of_burial": {
                    "type": "string",
                    "format": "date",
                    "description": "data pochówku głównego bohatera/bohaterki tekstu"
                },
            },
            "required": ["place_of_birth", "place_of_death", "place_of_burial", "date_of_birth", "date_of_death", "date_of_burial"]
        }
    }
]


tekst = """
Adam Wacław (1574–1617) z rodu Piastów, książę cieszyński, tytułujący się
także księciem górnogłogowskim, choć tego księstwa już nie posiadał, był synem Wacława Adama
i drugiej jego żony, Katarzyny Sydonji, księżniczki saskiej. Urodził się 12 XII 1574 r.
Miał 5 lat, gdy umarł mu ojciec. W czasie jego małoletności rządziła księstwem matka
wraz z dodanymi jej przez cesarza opiekunami księcia. Przyjeżdżała ona w tym celu
od czasu do czasu do Cieszyna, po powtórnem wyjściu zamąż – z wiedzą króla Stefana
Batorego – za Emeryka Forgacha, żupana trenczyńskiego, A.-W. wychowywał się przez 8 lat
na dworze elektora saskiego, w r. 1595 objął rządy w księstwie i w tym samym roku ożenił się
z Elżbietą, córką ks. kurlandzkiego, Kettlera.
A.-W. umarł w Cieszynie na Brandysie 13 VII 1617; ciało jego złożono najpierw na zamku
i dopiero 4 IV następnego roku pochowano w kościele dominikanów cieszyńskich, gdzie
spoczywały zwłoki wszystkich jego poprzedników. Zostawił 5 dzieci, z których Fryderyk Wilhelm,
ostatni cieszyński Piast męski, i Elżbieta Lukrecja, ostatnia Piastówna,
rządzili kolejno Księstwem.
"""

prompt = f"Na podstawie podanego tekstu biografii wyszukaj proszę podstawowe dane głównego bohatera: {tekst} "
message = [{"role": "system", "content": "Jesteś pomocnym asystentem, specjalistą w dziedzinie historii, genealogii, życiorysów znanych postaci."},
           {"role": "user", "content": prompt}]

response = openai.ChatCompletion.create(
    model="gpt-4-0613",
    messages=message,
    functions = function_basic_info,
    function_call="auto"
)

result = response['choices'][0]['message']['function_call']['arguments']
print(result)

# wynik:
# {
# "place_of_birth": "Cieszyn",
# "place_of_death": "Cieszyn",
# "place_of_burial": "kościół dominikanów cieszyńskich",
# "date_of_birth": "12 XII 1574",
# "date_of_death": "13 VII 1617",
# "date_of_burial": "4 IV 1618"
# }
