""" create embeddings """
import os
import openai
import time
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from numpy.linalg import norm
import pickle
import spacy
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential
)


# api key
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text):
    text = text.replace('\n', ' ')
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    # np.array
    return response['data'][0]['embedding']  # Returns the embedding vector


def cosine_similarity(A, B):
    return np.dot(A, B) / (norm(A) * norm(B))


if __name__ == '__main__':
    # spacy do podziału tekstu na zdania
    nlp = spacy.load('pl_core_news_lg')

    # dane z pliku tekstowego
    data_folder = Path("..") / "data_psb_250"
    data_file_list = data_folder.glob('*.txt')

    # pomiar czasu wykonania
    start_time = time.time()

    for data_file in data_file_list:

        embedding_cache = {}

        # wczytanie tekstu z podanego pliku
        text_from_file = ''
        with open(data_file, 'r', encoding='utf-8') as f:
            text_from_file = f.read().strip()

        if not text_from_file:
            print('Brak tekstu w pliku:', data_file)
            continue

        # nazwa pliku bez ścieżki
        data_file_name = os.path.basename(data_file)
        if 'Poniatowski' not in data_file_name:
            continue
        print(f'Przetwarzanie pliku: {data_file_name}')

        # ścieżka do pliku wyjściowego
        output_path = Path("..") / 'emb_psb_250' / data_file_name.replace('.txt', '.pkl')
        if os.path.exists(output_path):
            print(f'Plik {data_file_name.replace(".txt",".pkl")} już istnieje, pomijam...')
            continue

        doc = nlp(text_from_file)
        sentences = [sent.text for sent in doc.sents]
        for i, sent in enumerate(sentences):
            embedding_cache[i] = (sent, get_embedding(sent))

        with open(output_path, "wb") as embedding_pkl_file:
            pickle.dump(embedding_cache, embedding_pkl_file)

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')

