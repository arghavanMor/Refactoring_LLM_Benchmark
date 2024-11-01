import constants
import json
import csv
from openai import OpenAI
from tqdm import tqdm
import re

MODEL_NAME = "gpt-3.5-turbo"

def extract_csv():
    data_list = []

    with open("../Data/Data_collection.csv", "r") as csv_file:
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


def get_openai_response(prompt, client):

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


def generate_llm_json():

    API_KEY = open("./../OpenAI_key.txt", "r").read()


    with open(constants.FOWLER_JSON_FILE, "r+") as fowler_json_file:
        json_data = json.load(fowler_json_file)

        data_list = extract_csv()

        client = OpenAI(api_key=API_KEY)

        json_llm_generated_code = {}

        for example in tqdm(data_list):

            fowler_type = example["Fowler_type"].upper()

            before_refact_code = example["BeforeRefact"]

            zero_shot_prompt = fill_zero_shot_template(fowler_type, before_refact_code)

            refact_examples = ""

            if fowler_type not in json_data:
                print("ERROR: " + fowler_type)
                continue

            for subtitle in json_data[fowler_type]:
                if subtitle == "Mechanics":
                    instruc_prompt = fill_instructions_template(fowler_type, instruc=json_data[fowler_type]["Mechanics"], code=before_refact_code)

                elif subtitle.startswith("Example"):
                    refact_examples += subtitle + ":\n"
                    refact_examples += json_data[fowler_type][subtitle] + "\n"

            
            few_shot_prompt = fill_few_shot_template(fowler_type, examples=refact_examples, code=before_refact_code)

            zero_shot_generated_code = get_openai_response(zero_shot_prompt, client)
            instruc_generated_code = get_openai_response(instruc_prompt, client)
            few_shot_generated_code = get_openai_response(few_shot_prompt, client)

            # Write to JSON format
            csv_id = example["ï»¿ID"]
            json_llm_generated_code[csv_id] = {}
            json_llm_generated_code[csv_id]["RefactMethod"] = fowler_type
            json_llm_generated_code[csv_id]["BeforeRefact"] = example["BeforeRefact"]
            json_llm_generated_code[csv_id]["BeforeRefact"] = example["AfterRefact"]
            json_llm_generated_code[csv_id]["ZeroShotCode"] = zero_shot_generated_code
            json_llm_generated_code[csv_id]["InstrucCode"] = instruc_generated_code
            json_llm_generated_code[csv_id]["FewShotCode"] = few_shot_generated_code

    with open(constants.LLM_CODE_JSON_FILE, "w") as llm_json:
        json.dump(json_llm_generated_code, llm_json, indent=4)

def all_class_occurences(string):
    return [m.start() for m in re.finditer(r'class \b', string)]
    
def find_ending_point(string):

    opening_bracket_found = False
    unclosed_bracket = 0
    substring = ""

    for char in string:
        if char == "{":
            if not opening_bracket_found:
                opening_bracket_found = True
            unclosed_bracket += 1
        
        if char == "}":
            unclosed_bracket -= 1
        
        substring += char

        if unclosed_bracket == 0 and opening_bracket_found:
            return substring
        
    return substring

# Make strings out of all indexes not included in ranges
def filter_remaining_code(string, ranges):
    segments = []
    current_segment = ""

    for index, char in enumerate(string):
        if any(start <= index < end for start, end in ranges):
            if current_segment:
                segments.append(''.join(current_segment))
                current_segment = "" 
        else:
            current_segment += char

    if current_segment:
        segments.append(''.join(current_segment))

    return segments

def clean_llm_output():

    # Access modifier is left mandatory on purpose
    method_regex = r"(public|protected|private|static) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"
    regex = re.compile(method_regex)

    with open(constants.LLM_CODE_JSON_FILE, "r+") as llm_json:

        json_data = json.load(llm_json)
        all_prompt_types = ["ZeroShotCode", "InstrucCode", "FewShotCode"]

        for test_case in json_data:
            for prompt in all_prompt_types:

                methods = []
                classes = []
                all_indexes = []

                prompt_code = repr(json_data[test_case][prompt])[1:-1] # Since we take a string literal, we need to remove quotation marks at beginning and end

                # Find and add classes
                class_starting_index_array = all_class_occurences(prompt_code)
                if class_starting_index_array:
                    for index in class_starting_index_array:
                        current_class = find_ending_point(prompt_code[index:])
                        classes.append(current_class)
                        all_indexes.append((index, index + len(current_class)))

                # Find and add methods
                for hit in regex.finditer(prompt_code):
                    if class_starting_index_array:
                        for counter, index in enumerate(class_starting_index_array):
                            if index < hit.start() < len(classes[counter]): # Method is within a class
                                continue
                    current_method = find_ending_point(prompt_code[hit.start():])
                    methods.append(current_method)
                    all_indexes.append((hit.start(), hit.start() + len(current_method)))
                
                # Flag everything else as "others"
                sorted_indexes = sorted(all_indexes)
                others = filter_remaining_code(prompt_code, sorted_indexes)

                new_format = {}
                new_format["methods"] = [method.replace("\\n", "\n").replace("\\t", "\t") for method in methods]
                new_format["classes"] = [single_class.replace("\\n", "\n").replace("\\t", "\t") for single_class in classes]
                new_format["others"] = [other.replace("\\n", "\n").replace("\\t", "\t") for other in others]

                # Overwrite JSON
                json_data[test_case][prompt] = new_format
                llm_json.seek(0)
                json.dump(json_data, llm_json, indent=4)
                llm_json.truncate()
