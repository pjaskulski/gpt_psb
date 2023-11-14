""" uzupełnianie danych postaci w pliku  """
import json
import time
from pathlib import Path


# pomiar czasu wykonania
start_time = time.time()


# ----------------------------------- MAIN -------------------------------------

if __name__ == '__main__':

    postacie_path = Path("..") / "data_psb" / "postacie.json"

    with open(postacie_path, "r", encoding='utf-8') as f:
        json_data = json.load(f)
        for i, person in enumerate(json_data['persons']):
            name = person['name']
            psb_id = person.get('ID','')
            tom = person.get('volume','')

            if not tom:
                print(f'ERROR (brak tomu): {name} {psb_id}')
                continue

            tom_path = f'tom_{tom.zfill(2)}'
            biogram_file = person.get('file_new','')
            print(f'{name} ({psb_id} {biogram_file})')
            biogram_file = biogram_file.replace('’', '_')
            json_file = biogram_file.replace('.txt','.json')
            json_file_path = Path("..") / "output_psb" / "basic" / tom_path / json_file
            with open(json_file_path, "r", encoding='utf-8') as f_result:
                json_result = json.load(f_result)
                if type(json_result) == list:
                    person['gpt_place_of_birth'] = json_result[0].get('place_of_birth', None)
                    person['gpt_place_of_death'] = json_result[0].get('place_of_death', None)
                    person['gpt_place_of_burial'] = json_result[0].get('place_of_burial', None)
                    person['gpt_date_of_birth'] = json_result[0].get('date_of_birth', None)
                    person['gpt_date_of_death'] = json_result[0].get('date_of_death', None)
                    person['gpt_date_of_burial'] = json_result[0].get('date_of_burial', None)
                else:
                    person['gpt_place_of_birth'] = json_result.get('place_of_birth', None)
                    person['gpt_place_of_death'] = json_result.get('place_of_death', None)
                    person['gpt_place_of_burial'] = json_result.get('place_of_burial', None)
                    person['gpt_date_of_birth'] = json_result.get('date_of_birth', None)
                    person['gpt_date_of_death'] = json_result.get('date_of_death', None)
                    person['gpt_date_of_burial'] = json_result.get('date_of_burial', None)

                # place of birth
                if isinstance(person['gpt_place_of_birth'], dict):
                    if person['gpt_place_of_birth']['place'] in ["brak danych", "no data"]:
                        person['gpt_place_of_birth']['place'] = None
                elif isinstance(person['gpt_place_of_birth'], list):
                    for item in person['gpt_place_of_birth']:
                        if item['place'] in ["brak danych", "no data"]:
                            item['place'] = None

                # place of death
                if isinstance(person['gpt_place_of_death'], dict):
                    if person['gpt_place_of_death']['place'] in ["brak danych", "no data"]:
                        person['gpt_place_of_death']['place'] = None
                elif isinstance(person['gpt_place_of_death'], list):
                    for item in person['gpt_place_of_death']:
                        if item['place'] in ["brak danych", "no data"]:
                            item['place'] = None

                # place of burial
                if isinstance(person['gpt_place_of_burial'], dict):
                    if person['gpt_place_of_burial']['place'] in ["brak danych", "no data"]:
                        person['gpt_place_of_burial']['place'] = None
                elif isinstance(person['gpt_place_of_burial'], list):
                    for item in person['gpt_place_of_burial']:
                        if item['place'] in ["brak danych", "no data"]:
                            item['place'] = None

                # obsługa częstego błędu w wynikowych json
                if ('place' in person['gpt_date_of_birth'] and
                     person['gpt_date_of_birth']['place'] in ["brak danych", "no data"]):
                    person['gpt_date_of_birth']['date'] = person['gpt_date_of_birth'].pop('place')
                if ('place' in person['gpt_date_of_death'] and
                     person['gpt_date_of_death']['place'] in ["brak danych", "no data"]):
                    person['gpt_date_of_death']['date'] = person['gpt_date_of_death'].pop('place')
                if ('place' in person['gpt_date_of_burial'] and
                     person['gpt_date_of_burial']['place'] in ["brak danych", "no data"]):
                    person['gpt_date_of_burial']['date'] = person['gpt_date_of_burial'].pop('place')

                if isinstance(person['gpt_date_of_birth'], dict):
                    if person['gpt_date_of_birth']['date'] == "brak danych" or person['gpt_date_of_birth']['date'] == "no data":
                        person['gpt_date_of_birth']['date'] = None
                elif isinstance(person['gpt_date_of_birth'], list):
                    for item in person['gpt_date_of_birth']:
                        if item['date'] in ["brak danych", "no data"]:
                            item['date'] = None

                if isinstance(person['gpt_date_of_death'], dict):
                    if person['gpt_date_of_death']['date'] == "brak danych" or person['gpt_date_of_death']['date'] == "no data":
                        person['gpt_date_of_death']['date'] = None
                elif isinstance(person['gpt_date_of_death'], list):
                    for item in person['gpt_date_of_death']:
                        if item['date'] in ["brak danych", "no data"]:
                            item['date'] = None

                if isinstance(person['gpt_date_of_burial'], dict):
                    if person['gpt_date_of_burial']['date'] == "brak danych" or person['gpt_date_of_burial']['date'] == "no data":
                        person['gpt_date_of_burial']['date'] = None
                elif isinstance(person['gpt_date_of_burial'], list):
                    for item in person['gpt_date_of_burial']:
                        if item['date'] in ["brak danych", "no data"]:
                            item['date'] = None

    postacie_output_path = Path("..") / "data_psb" / "postacie_gpt.json"
    with open(postacie_output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
