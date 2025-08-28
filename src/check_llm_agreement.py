import constants
import csv
from tqdm import tqdm
from openai import OpenAI
from sklearn.metrics import cohen_kappa_score


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

def calculate_cohen_kappa_score():

    # Score given by human raters
    human_rater1 = []
    human_rater2 = []
    
    human_agreement_deepseek = []
    deepseek_rater = []

    human_agreement_gpt = []
    gpt_rater = []

    with open("./Data/fowler_run#3_agreement.csv", "r") as gpt_csv:
        reader = csv.DictReader(gpt_csv)
        rows = list(reader)


        for row in rows:
            deepseek_rater.append(row["LlmReview"])
            human_agreement_deepseek.append(row["Agreement"])
            human_rater1.append(row["Reviewer#1"])
            human_rater2.append(row["Reviewer#2"])

    with open("./Data/fowler_ds_run#1_agreement.csv", "r") as ds_csv:
        reader = csv.DictReader(ds_csv)
        rows = list(reader)

        for row in rows:
            gpt_rater.append(row["LlmReview"])
            human_agreement_gpt.append(row["Agreement"])
            human_rater1.append(row["Reviewer#1"])
            human_rater2.append(row["Reviewer#2"])

    print("Human-Human Kappa Score: " + str(cohen_kappa_score(human_rater1, human_rater2)))
    print("DeepSeek-Human Kappa Score: " + str(cohen_kappa_score(human_agreement_deepseek, deepseek_rater)))
    print("GPT-Human Kappa Score: " + str(cohen_kappa_score(human_agreement_gpt, gpt_rater)))
    

    

calculate_cohen_kappa_score()
#add_llm_agreement(filepath="./Data/fowler_run#5.csv")