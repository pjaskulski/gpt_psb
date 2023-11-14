""" langchain learn """
import os
from langchain import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from pathlib import Path
from dotenv import load_dotenv


# api key
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


if __name__ == '__main__':
    print("Hello LangChain")

    extract_template = """
            Na podstawie podanego tekstu biografii przygotuj podstawowe informacje
            o osobie będącej jej głównym bohaterem: data i miejsce urodzenia, data
            i miejsce śmierci, data i miejsce pochówku. W przypadku braku takich
            informacji napisz: brak danych.
            Tekst: {biografia}
    """

    extract_prompt_template = PromptTemplate(input_variables=["biografia"],
                                             template=extract_template)

    llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")
    chain = LLMChain(llm=llm, prompt=extract_prompt_template)

    # plik z biografią
    file_data_path = Path("..") / "data_psb_250" / "Adam_Waclaw.txt"
    with open(file_data_path, 'r', encoding='utf-8') as f:
        biografia = f.read()

    result = chain.run(biografia=biografia)
    print(result)
