import constants
import json
import csv
from openai import OpenAI


def extract_csv():
    data_list = []

    with open("../Data/Examples.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data_list.append(row)

    return data_list


def fill_zero_shot_template(refact_method, code):

    with open(constants.ZERO_SHOT_TEMPLATE_FILE, "r") as zero_shot_template_file:
        zero_shot_template = zero_shot_template_file.read()
        zero_shot_template = zero_shot_template.replace("<refactoring method>", refact_method)
        zero_shot_template = zero_shot_template.replace("<code>", code)

    return zero_shot_template

def fill_instructions_template(refact_method, instruc, code):
    
    with  open(constants.INSTRUCTIONS_TEMPLATE_FILE, "r") as instruc_template_file:
        instruc_template = instruc_template_file.read()
        instruc_template = instruc_template.replace("<refactoring method>", refact_method)
        instruc_template = instruc_template.replace("<steps>", instruc)
        instruc_template = instruc_template.replace("<code>", code)

    return instruc_template


def fill_few_shot_template(refact_method, examples, code):
    
    with open(constants.FEW_SHOT_TEMPLATE_FILE, "r") as few_shot_template_file:
        few_shot_template = few_shot_template_file.read()
        few_shot_template = few_shot_template.replace("<refactoring method>", refact_method)
        few_shot_template = few_shot_template.replace("<refactoring example>", examples)
        few_shot_template = few_shot_template.replace("<code>", code)
    
    return few_shot_template


def chat_with_openai(prompt, client):

    message = {
        'role': 'user',
        'content': prompt
    }

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[message]
    )

    chatbot_response = response.choices[0].message.content
    return chatbot_response.strip()



API_KEY = open("./../OpenAI_key.txt", "r").read()
MODEL_NAME = "gpt-3.5-turbo"


with open(constants.FOWLER_JSON_FILE_NAME, "r+") as fowler_json_file:
    json_data = json.load(fowler_json_file)

    data_list = extract_csv()

    client = OpenAI(api_key=API_KEY)
    processed_refact_methods = []

    json_llm_generated_code = {}

    for example in data_list:

        fowler_type = example["Fowler_type"].upper()

        # We only want one example per Refactoring method
        if fowler_type in processed_refact_methods:
            continue

        before_refact_code = example["BeforeRefact"]

        zero_shot_prompt = fill_zero_shot_template(fowler_type, before_refact_code)

        refact_examples = ""
        for subtitle in json_data[fowler_type]:
            if subtitle == "Mechanics":
                instruc_prompt = fill_instructions_template(fowler_type, instruc=json_data[fowler_type]["Mechanics"], code=before_refact_code)

            elif subtitle.startswith("Example"):
                refact_examples += subtitle + ":\n"
                refact_examples += json_data[fowler_type][subtitle] + "\n"

        
        few_shot_prompt = fill_few_shot_template(fowler_type, examples=refact_examples, code=before_refact_code)

        zero_shot_generated_code = chat_with_openai(zero_shot_prompt, client)
        instruc_generated_code = chat_with_openai(instruc_prompt, client)
        few_shot_generated_code = chat_with_openai(few_shot_prompt, client)

        # Write to JSON format
        json_llm_generated_code[fowler_type] = {}
        json_llm_generated_code[fowler_type]["ID"] = example["ï»¿ID"]
        json_llm_generated_code[fowler_type]["BeforeRefact"] = example["BeforeRefact"]
        json_llm_generated_code[fowler_type]["ZeroShotCode"] = zero_shot_generated_code
        json_llm_generated_code[fowler_type]["InstrucCode"] = instruc_generated_code
        json_llm_generated_code[fowler_type]["FewShotCode"] = few_shot_generated_code

        processed_refact_methods.append(fowler_type)

with open(constants.LLM_CODE_JSON_FILE_NAME, "w") as llm_json:
    json.dump(json_llm_generated_code, llm_json)
