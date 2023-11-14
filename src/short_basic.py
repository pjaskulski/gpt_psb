""" tworzenie skróconych wersji biogramów PSB - informacje podstawowe """
import os
import time
from pathlib import Path
import tiktoken
import spacy


# ceny gpt-4 w dolarach
INPUT_PRICE_GPT4 = 0.03
OUTPUT_PRICE_GPT4 = 0.06

# ceny gpt-3.5 w dolarach
INPUT_PRICE_GPT35 = 0.0015
OUTPUT_PRICE_GPT35 = 0.002

# spacy do podziału tekstu na zdania
nlp = spacy.load('pl_core_news_lg')


def short_version(text:str) -> str:
    """ proste skracanie biogramów, zdania istotne dla informacji podstawowych """
    result = ''
    select_data = []

    words = ['urodzony', 'narodzony', 'zmarł', 'umarł', 'pochowany', 'pochówek',
             'pogrzeb', 'kaplica', 'kolegiata',
             'grób', 'grobowiec', 'cmentarz', 'kościół', 'poległ', 'poległa', 'zmarła',
             'umarła', 'pochowana', 'urodzona', 'urodzić', 'urodził', 'urodziła', 'umrzeć',
             'zgasnać', 'zemrzeć', "żyć", "żył", "żyła", "życie", "choroba", "wypadek",
             "ulec", "śmierć", "paść", "zginąć", "zgon", 'polec',
             "zamordować", "mord", "mordować", "zabić", "odejść"
            ]
    s_words = ['um', 'zm', 'ur']

    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    selected_sentences = {}
    for x in range(0, len(sentences)):
        selected_sentences[x] = False

    # pierwsze dwa zdania
    select_data = sentences[0:2]
    selected_sentences[0] = True
    selected_sentences[1] = True

    # ze dalszych zdań tylko takie wskazujące na związek z informacjami podstawowymi
    for i in range(2,len(sentences)):
        if selected_sentences[i]:
            continue
        sent_doc = nlp(sentences[i])
        for token in sent_doc:
            if (token.lemma_.lower() in words or
                token.text.lower() in words or
                token.text.lower() in s_words):

                # zdanie poprzednie
                if not selected_sentences[i-1]:
                    select_data.append(sentences[i - 1])
                    selected_sentences[i - 1] = True
                # bieżące zdanie
                select_data.append(sentences[i])
                selected_sentences[i] = True

                # następne zdanie
                if (i + 1) < (len(sentences) -1) and not selected_sentences[i + 1]:
                    select_data.append(sentences[i + 1])
                    selected_sentences[i + 1] = True

                break

    result = ' '.join(select_data)

    return result


def count_tokens(text:str, model:str = "gpt-4") -> int:
    """ funkcja zlicza tokeny """
    num_of_tokens = 0
    enc = tiktoken.encoding_for_model(model)
    num_of_tokens = len(enc.encode(text))

    return num_of_tokens


# ------------------------------------------------------------------------------
if __name__ == '__main__':

    # pomiar czasu wykonania
    start_time = time.time()

    #podsumowanie kosztów
    total_price_gpt4 = 0
    total_price_gpt35 = 0
    total_tokens_data = 0
    total_tokens_output = 0

    # szablon zapytania o relacje rodzinne postaci - do obliczeń kosztów
    prompt_path = Path("..") / "prompts" / "person_basic_en.txt"
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt = f.read()

    # dane z pliku tekstowego

    for i in range(1, 52):
        tom = 'tom_' + str(i).zfill(2)
        data_folder = Path("..") / "data_psb" / "full" / tom
        data_file_list = data_folder.glob('*.txt')


        for data_file in data_file_list:
            # wczytanie tekstu z podanego pliku
            text_from_file = ''
            with open(data_file, 'r', encoding='utf-8') as f:
                text_from_file = f.read().strip()

            # nazwa pliku bez ścieżki
            data_file_name = os.path.basename(data_file)
            output_path = Path("..") / 'data_psb' / 'short' / tom / data_file_name

            print(f'{tom} / {data_file}')

            text_from_file = short_version(text_from_file)
            tokens_in_data = count_tokens(prompt + text_from_file)
            # przeciętna wielkość zwracanych danych w json (w tokenach)
            tokens_in_output = 150 # około 500 znaków

            total_tokens_data += tokens_in_data
            total_tokens_output += tokens_in_output

            # zapis do pliku json
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text_from_file)

    price_gpt4 = (((total_tokens_data/1000) * INPUT_PRICE_GPT4) +
                      ((total_tokens_output/1000) * OUTPUT_PRICE_GPT4))

    price_gpt35 = (((total_tokens_data/1000) * INPUT_PRICE_GPT35) +
                      ((total_tokens_output/1000) * OUTPUT_PRICE_GPT35))


    print(f'Razem tokenów: {total_tokens_data + total_tokens_output}.')
    print(f'Koszt przetworzenia biogramów GPT-4: {price_gpt4:.2f}')
    print(f'Koszt przetworzenia biogramów GPT-3.5: {price_gpt35:.2f}')

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
