""" analiza kosztów biogramów PSB - relacje rodzinne - GPT4-turbo
"""
import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
import tiktoken

MODEL = 'gpt-4-1106-preview'

# maksymalna wielkość odpowiedzi
OUTPUT_TOKENS = 1000
# wielkość angielskiego promptu to ok 900 tokenow, model gpt-4 obsługuje do 8000 tokenów
# model gt-4-1106 - 128 tys.
MODEL_TOKENS = 128000

# ceny gpt-4-1106-preview w dolarach
INPUT_PRICE_GPT = 0.01
OUTPUT_PRICE_GPT = 0.03


def count_tokens(text:str, model:str = "gpt-4") -> int:
    """ funkcja zlicza tokeny """
    num_of_tokens = 0
    enc = tiktoken.encoding_for_model(model)
    num_of_tokens = len(enc.encode(text))

    return num_of_tokens


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    total_price_gpt4 = 0
    total_tokens = 0

    # szablon zapytania o podstawowe informacje na temat postaci
    prompt_path = Path("..") / "prompts" / "person_functions.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # prompt dla relations to obecnie około 1100 tokenów
    PROMPT_TOKENS = count_tokens(prompt)
    # maksymalna liczba tokenów w treści biogramu
    MAX_TOKENS = MODEL_TOKENS - PROMPT_TOKENS - OUTPUT_TOKENS

    for num_tom in range(1, 52):
        tom = f'tom_{str(num_tom).zfill(2)}'
        print(tom)
        data_folder = Path("..") / "data_psb" / "full" / tom
        data_file_list = data_folder.glob('*.txt')

        # pomiar czasu wykonania
        start_time = time.time()

        for data_file in data_file_list:
            # nazwa pliku bez ścieżki
            data_file_name = os.path.basename(data_file)
            print(data_file_name)

            # wczytanie tekstu z podanego pliku
            text_from_file = ''
            with open(data_file, 'r', encoding='utf-8') as f:
                text_from_file = f.read().strip()

            # weryfikacja liczby tokenów
            llm_prompt_tokens = count_tokens(prompt + text_from_file)
            llm_compl_tokens = 500

            # obliczenie kosztów
            price_gpt4 = (((llm_prompt_tokens/1000) * INPUT_PRICE_GPT) +
                        ((llm_compl_tokens/1000) * OUTPUT_PRICE_GPT))

            total_price_gpt4 += price_gpt4
            total_tokens += (llm_prompt_tokens + llm_compl_tokens)

            # zapis w logu
            with open('tokeny_full.log', 'a', encoding='utf-8') as f_tok:
                f_tok.write(f"{tom}@{data_file_name}@{price_gpt4:.2f}@{llm_prompt_tokens + llm_compl_tokens}\n")

            # przerwa między requestami
            time.sleep(0.25)

    print(f'Razem koszt: {total_price_gpt4:.2f} $, tokenów: {total_tokens}')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
