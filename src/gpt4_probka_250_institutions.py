""" analiza próbki 250 biogramów - instytucje związane z postacią """
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import tiktoken
import spacy
import openai


# tryb pracy, jeżeli True używa API OpenAI, jeżeli False  to tylko test
USE_API = True

# parametry modelu gpt-4
MODEL_MAX_TOKENS = 8000

# maksymalna wielkość odpowiedzi
OUTPUT_TOKENS = 2200
# maksymalna liczba tokenów w treści biogramu
MAX_TOKENS = 5000

# ograniczenia API (dla bieżącej organizacji i modelu GPT-4)
MAX_TOKENS_PER_MINUTE = 10000
MAX_REQUESTS_PER_MINUTE=200

# ceny gpt-4 w dolarach
INPUT_PRICE_GPT4 = 0.03
OUTPUT_PRICE_GPT4 = 0.06

# api key
env_path = Path(".") / ".env_ihpan"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


def get_text_parts(text:str, max_tokens:int) -> list:
    """zwraca podzielony tekst w formie listy, tak by każda część
    mieściła się w ograniczeniach tokenów"""

    # sprawdzenie czy tekst jest na tyle duży że trzeba go podzielić
    size_of_text = count_tokens(text)
    if size_of_text < max_tokens:
        return [text]

    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    # pierwsze dwa zdania trafiają do każdej części by model wiedział czego dotyczy tekst
    select_data = sentences[0:2]
    start_text = ' '.join(select_data)
    start_tokens = count_tokens(start_text)

    lista = []
    # przygotowanie partii tekstu mieszczącego się w ograniczeniach
    part_text = start_text
    part_tokens = start_tokens

    for i in range(2,len(sentences)):
        sent_tokens = count_tokens(sentences[i])
        if part_tokens + sent_tokens > max_tokens:
            lista.append(part_text)
            part_text = start_text
            part_tokens = start_tokens

        part_text += ' ' + sentences[i]
        part_tokens += sent_tokens

    lista.append(part_text)

    return lista


def count_tokens(text:str, model:str = "gpt2") -> int:
    """ funkcja zlicza tokeny """
    num_of_tokens = 0
    enc = tiktoken.get_encoding(model)
    num_of_tokens = len(enc.encode(text))

    return num_of_tokens


def get_answer(prompt:str='', text:str='', model:str='gpt-4') -> str:
    """ funkcja konstruuje prompt do modelu GPT dostępnego przez API i zwraca wynik """
    result = ''
    prompt_tokens = completion_tokens = 0

    try:
        response = openai.ChatCompletion.create(
                    model=model,
                    messages=[
                        #{"role": "system", "content": "Jesteś pomocnym asystentem, specjalistą w dziedzinie historii, genealogii, życiorysów znanych postaci."},
                        {"role": "system", "content": "You are a helpful assistant, a specialist in history, genealogy, biographies of famous figures."},
                        {"role": "user", "content": f"{prompt}\n{text}"}
                    ],
                    temperature=0.0,
                    top_p = 1.0,
                    max_tokens=OUTPUT_TOKENS)

        result = response['choices'][0]['message']['content']
        prompt_tokens = response['usage']['prompt_tokens']
        completion_tokens = response['usage']['completion_tokens']
    except openai.error.RateLimitError as api_error:
        print(api_error)
        return '[RateLimitError]', 0, 0
    except Exception as api_error:
        print(api_error)
        sys.exit(1)

    return result, prompt_tokens, completion_tokens


def format_result(text: str) -> dict:
    """ poprawianie i formatowanie wyniku zwróconego przez LLM """
    text = text.strip()
    if text.startswith("Wynik:"):
        text = text[6:].strip()
    if text.lower().strip() == 'brak danych':
        text = '{"result": "brak danych"}'
    elif text.lower().strip() == 'brak danych.':
        text = '{"result": "brak danych"}'

    if not '[' in text:
        text = '[' + text + ']'

    if text.endswith('},\n]'):
        text = text.replace('},\n]', '}\n]')

    try:
        data = json.loads(text)
    except json.decoder.JSONDecodeError as json_err:
        print(json_err.msg, '\n', text)
        sys.exit(1)

    return data


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    if USE_API:
        print('UWAGA: uruchomiono w trybie realnego przetwarzania z wykorzystaniem API - to kosztuje!')
    else:
        print('Uruchomiono w trybie testowym, bez użycia API (to nie kosztuje).')

    total_price_gpt4 = 0
    total_tokens = 0
    number_of_request = 0
    tokens_per_minute = 0

    # spacy do podziału tekstu na zdania
    nlp = spacy.load('pl_core_news_lg')

    # szablon zapytania o ważne osoby dla postaci (poza krewnymi)
    prompt_path = Path("..") / "prompts" / "person_institutions.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    prompt_size = count_tokens(prompt_template)

    # dane z pliku tekstowego
    data_folder = Path("..") / "data_psb_250"
    data_file_list = data_folder.glob('*.txt')

    # pomiar czasu wykonania
    start_time = time.time()
    loop_start_time = time.time()

    for data_file in data_file_list:
        # wczytanie tekstu z podanego pliku
        text_from_file = ''
        with open(data_file, 'r', encoding='utf-8') as f:
            text_from_file = f.read().strip()

        if not text_from_file:
            print('Brak tekstu w pliku:', data_file)
            continue

        # nazwa pliku bez ścieżki
        data_file_name = os.path.basename(data_file)
        # ścieżka do pliku wyjściowego
        output_path = Path("..") / 'output_json_250' / 'institutions' / data_file_name.replace('.txt','.institution.json')
        if os.path.exists(output_path):
            print(f'Plik {data_file_name.replace(".txt",".institution.json")} z wynikiem przetwarzania już istnieje, pomijam...')
            continue

        # bez skracania biogramów, efekt wyszukiwania instytucji i organizacji przez spaCy jest słaby
        # tekst dłuższych biogramów jest dzielony
        texts_from_file = get_text_parts(text_from_file, MAX_TOKENS)

        if len(texts_from_file) > 1:
            print(f'Biogram {data_file_name} podzielony na {len(texts_from_file)} części:')
            for p_text in texts_from_file:
                print(f'{prompt_size + count_tokens(p_text)} tokenów')

        # przetwarzanie modelem gpt-4
        if USE_API:
            llm_prompt_tokens = llm_compl_tokens = 0
            llm_dict = []
            for part_of_text in texts_from_file:

                # # zabezpieczenia przed przekroczeniem limitów API (l. przetwarzanych tokenów
                # # na minutę, oraz liczbą zapytań na minutę)
                loop_end_time = time.time()
                loop_elapsed_time = loop_end_time - loop_start_time

                if tokens_per_minute > MAX_TOKENS_PER_MINUTE * 0.9 and loop_elapsed_time < 60:
                    sleep_lenght = 60.0 - loop_elapsed_time + 1
                    print(f'Przetworzono {tokens_per_minute} tokenów w ciągu ostatniej minuty, przerwa {sleep_lenght:.1f} s. ...')
                    time.sleep(sleep_lenght)
                elif number_of_request >= MAX_REQUESTS_PER_MINUTE and loop_elapsed_time < 60:
                    sleep_lenght = 60.0 - loop_elapsed_time + 1
                    print(f'Przetworzono {number_of_request} zapytań w ciągu ostatniej minuty, przerwa {sleep_lenght:.1f} s. ...')
                    time.sleep(sleep_lenght)

                loop_end_time = time.time()
                loop_elapsed_time = loop_end_time - loop_start_time

                if loop_elapsed_time >= 60.0:
                    print('Minęła pełna minuta, reset licznika tokenów i zapytań...')
                    tokens_per_minute = 0
                    number_of_request = 0
                    loop_start_time = time.time()

                # przetwarzanie tekstu przez openai api (gpt-4)
                result_obtained = False
                while not result_obtained:
                    p_llm_result, p_llm_prompt_tokens, p_llm_compl_tokens = get_answer(prompt_template,
                                                                                       part_of_text,
                                                                                       model='gpt-4')
                    if p_llm_result != '[RateLimitError]':
                        result_obtained = True
                    else:
                        print(f'Przerwa {60:.1f} s. ...')
                        time.sleep(60)

                p_llm_dict = format_result(p_llm_result)
                for p_item in p_llm_dict:
                    if p_item not in llm_dict:
                        llm_dict.append(p_item)

                llm_prompt_tokens += p_llm_prompt_tokens
                llm_compl_tokens += p_llm_compl_tokens

                # zliczanie tokenów i zapytań
                tokens_per_minute += (llm_prompt_tokens + llm_compl_tokens)
                number_of_request += 1

        else:
            # tryb testowy
            llm_prompt_tokens = count_tokens((len(texts_from_file) * prompt_template) + ' '.join(texts_from_file))
            llm_compl_tokens = 120 # przeciętna liczba tokenów w odpowiedzi
            llm_result = """Wynik:
                            [{"institution":"Bank Czeski", "place_of_institution":"Wrocław"},
                             {"institution":"Izba Celna", "place_of_institution":"Gdańsk"}
                            ]
                        """
            llm_dict = format_result(llm_result)

        # zapis do pliku json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(llm_dict, f, indent=4, ensure_ascii=False)

        # obliczenie kosztów
        price_gpt4 = (((llm_prompt_tokens/1000) * INPUT_PRICE_GPT4) +
                      ((llm_compl_tokens/1000) * OUTPUT_PRICE_GPT4))
        print(f'Biogram: {data_file_name} ({llm_prompt_tokens}, {llm_compl_tokens}), koszt: {price_gpt4:.2f}')

        total_price_gpt4 += price_gpt4
        total_tokens += (llm_prompt_tokens + llm_compl_tokens)

        # przerwa między requestami
        time.sleep(0.25)

    print(f'Razem koszt: {total_price_gpt4:.2f} $, tokenów: {total_tokens}')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
