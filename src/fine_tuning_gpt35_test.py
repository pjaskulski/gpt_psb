""" function calling test """
import openai
import os
import time
from dotenv import load_dotenv
from pathlib import Path


# api key
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY


psb_data = Path("..") / "data" / "pdb_data.jsonl"

file_id = openai.File.create(
  file=open(psb_data, 'r', encoding='utf-8'),
  purpose='fine-tune',
)

ft_job = openai.FineTuningJob.create(
    training_file=file_id,
    model='gpt-3.5-turbo',
)

model_id = None
print('Proces trwa...')

finished = False
while not finished:
    status = openai.FineTuningJob.retrieve(ft_job['id'])
    if status['finished_at']:
      model_id = status['fine_tuned_model']
      finished = True
    else:
      print('...', end='')
      time.sleep(15)

print(model_id)