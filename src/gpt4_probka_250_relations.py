""" analiza próbki 250 biogramów - relacje rodzinne głównego bohatera/bohaterki """
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import tiktoken
import spacy
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)


# tryb pracy, jeżeli True używa API OpenAI, jeżeli False  to tylko test
USE_API = True

# maksymalna wielkość odpowiedzi
OUTPUT_TOKENS = 1200

# maksymalna liczba tokenów w treści biogramu
MAX_TOKENS = 6000

# ceny gpt-4 w dolarach
INPUT_PRICE_GPT4 = 0.03
OUTPUT_PRICE_GPT4 = 0.06

# api key
env_path = Path(".") / ".env_ihpan"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


def short_version_relations(text:str) -> str:
    """ skracanie biogramów do zdań zawierających informacje o pokrewieństwie lub powinowactwie """

    select_data = []
    words = ['ojciec', 'matka', 'syn', 'córka', 'brat', 'siostra', 'żona',
                'mąż', 'teść', 'teściowa', 'dziadek', 'babcia', 'wnuk', 'wnuczka',
                'szwagier', 'szwagierka', 'siostrzeniec', 'siostrzenica', 'bratanek',
                'bratanica', 'kuzyn', 'kuzynka', 'zięć', 'synowa', 'dziecko', 'wuj',
                'ciotka', 'rodzina', 'krewni', 'krewny', "ożenić", "bezdzietny", "ożeniony", "zamężna",
                "rodzic", "rodzice", "spokrewniony", "spokrewnieni", "małżeństwo", "rodzeństwo",
                "bratankowie", "siostrzeńcy", "bratanice", "siostrzenice", "małżeństwa",
                "żonaty", "ożenić", "poślubić", "wyjść"]

    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]

    if len(sentences) > 10:
        # pierwszych pięć zdań
        select_data = sentences[0:5]

        # ze środkowych zdań tylko takie wskazujące na opisy relacji rodzinnych
        for i in range(5,len(sentences) - 5):
            sent_doc = nlp(sentences[i])
            for token in sent_doc:
                if token.lemma_ in words:
                    select_data.append(sentences[i])
                    break

        # ostatnie pięć zdań
        select_data += sentences[len(sentences) - 5:]
    else:
        # wszystko
        select_data = sentences[0:]

    result = ' '.join(select_data)
    return result


def count_tokens(text:str, model:str = "gpt2") -> int:
    """ funkcja zlicza tokeny """
    num_of_tokens = 0
    enc = tiktoken.get_encoding(model)
    num_of_tokens = len(enc.encode(text))

    return num_of_tokens


@retry(wait=wait_random_exponential(min=30, max=60), stop=stop_after_attempt(6))
def get_answer_with_backoff(**kwargs):
    """ add exponential backoff to requests using the tenacity library """
    return openai.ChatCompletion.create(**kwargs)


def get_answer(prompt:str='', text:str='', model:str='gpt-4') -> str:
    """ funkcja konstruuje prompt do modelu GPT dostępnego przez API i zwraca wynik """
    result = ''
    prompt_tokens = completion_tokens = 0

    try:
        response = get_answer_with_backoff(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Jesteś pomocnym asystentem, specjalistą w dziedzinie historii, genealogii, życiorysów znanych postaci."},
                        {"role": "user", "content": f"{prompt}\n{text}"}
                    ],
                    temperature=0.0,
                    top_p = 1.0,
                    max_tokens=OUTPUT_TOKENS)

        result = response['choices'][0]['message']['content']
        prompt_tokens = response['usage']['prompt_tokens']
        completion_tokens = response['usage']['completion_tokens']

    except Exception as request_error:
        print(request_error)
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

    # spacy do podziału tekstu na zdania
    nlp = spacy.load('pl_core_news_md')

    # szablon zapytania o podstawowe informacje na temat postaci
    prompt_path = Path("..") / "prompts" / "person_relations.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # dane z pliku tekstowego
    data_folder = Path("..") / "data_psb_250"
    data_file_list = data_folder.glob('*.txt')

    # pomiar czasu wykonania
    start_time = time.time()

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
        output_path = Path("..") / 'output_json_250' / 'relations' / data_file_name.replace('.txt','.relations.json')
        if os.path.exists(output_path):
            print(f'Plik {data_file_name.replace(".txt",".relations.json")} z wynikiem przetwarzania już istnieje, pomijam...')
            continue

        # text biogramu jest zawsze skracany, chyba że ma 10 lub mniej zdań
        text_from_file = short_version_relations(text_from_file)

        # weryfikacja liczby tokenów, za duże teksty (mimo skracania) są na razie pomijane
        tokens_in_data = count_tokens(prompt + text_from_file)
        if tokens_in_data > 8000 - OUTPUT_TOKENS:
            print(f'Za duży kontekst: {tokens_in_data} tokenów, biogram: {data_file_name}')
            continue

        # przetwarzanie modelem gpt-4
        if USE_API:
            llm_result, llm_prompt_tokens, llm_compl_tokens = get_answer(prompt, text_from_file, model='gpt-4')
        else:
            # tryb testowy
            llm_prompt_tokens = count_tokens(prompt + text_from_file)
            llm_compl_tokens = 120 # przeciętna liczba tokenów w odpowiedzi
            llm_result = """Wynik:
                            [
                                {"family_relation":"ojciec", "person":"Niccola Ricasoli"},
                                {"family_relation":"matka", "person":"Annalena Ricasoli"},
                                {"family_relation":"brat", "person":"Bernard"},
                                {"family_relation":"bratanica", "person":"Małgorzata Anna"},
                                {"family_relation":"żona", "person":"Joanna"},
                                {"family_relation":"teść", "person":"Adam Kurozwęcki"}
                            ]
                        """

        llm_dict = format_result(llm_result)

        # zapis do pliku json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(llm_dict, f, indent=4, ensure_ascii=False)

        # obliczenie kosztów
        price_gpt4 = (((llm_prompt_tokens/1000) * INPUT_PRICE_GPT4) +
                      ((llm_compl_tokens/1000) * OUTPUT_PRICE_GPT4))
        print(f'Biogram: {data_file_name} ({llm_prompt_tokens}), koszt: {price_gpt4:.2f}')

        total_price_gpt4 += price_gpt4
        total_tokens += (llm_prompt_tokens + llm_compl_tokens)

        # przerwa między requestami
        time.sleep(0.25)

    print(f'Razem koszt: {total_price_gpt4:.2f} $, tokenów: {total_tokens}')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
