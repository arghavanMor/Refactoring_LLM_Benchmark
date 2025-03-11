import constants
import csv
from tqdm import tqdm
from openai import OpenAI

MODEL_NAME = "deepseek-chat"
BASE_URL = "https://api.deepseek.com"

# MODEL_NAME = "gpt-4o-mini"

def get_deepseek_response(prompt, client):

    message = {
        'role': 'user',
        'content': prompt
    }
    response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=[message],
    stream=False
    )

    chatbot_response = response.choices[0].message.content
    return chatbot_response.strip()

def fill_llm_agreement_template(refact_method, initial_code, final_code):
    with open(constants.LLM_AGREEMENT_TEMPLATE_FILE, "r") as llm_agreement_tempate_file:
        llm_agreement_template = llm_agreement_tempate_file.read()
        llm_agreement_template = llm_agreement_template.replace("<refactoring method>", refact_method)
        llm_agreement_template = llm_agreement_template.replace("<final code>", final_code)
        llm_agreement_template = llm_agreement_template.replace("<initial code>", initial_code)
    
    return llm_agreement_template


def add_llm_agreement(filepath):
    API_KEY = open("./DeepSeek_key.txt", "r").read()
    # API_KEY = open("./OpenAI_key.txt", "r").read()
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    with open(filepath, "r") as csv_file_input:
        new_column_header = "LlmReview"
        reader = csv.DictReader(csv_file_input)

        rows = list(reader)

        for row in tqdm(rows):
            llm_agreement_template = fill_llm_agreement_template(refact_method=row["RefactMethod"], initial_code=row["BeforeRefact"], final_code=row["LlmCode"])
            response = get_deepseek_response(prompt=llm_agreement_template, client=client)
            row[new_column_header] = response

        with open(filepath, "w") as csv_file_output:
            fieldnames = reader.fieldnames + [new_column_header]
            writer = csv.DictWriter(csv_file_output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

add_llm_agreement(filepath="./Data/fowler_run#5.csv")