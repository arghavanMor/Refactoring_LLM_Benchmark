import constants
import json
import csv
from openai import OpenAI
from tqdm import tqdm
import re
import os

MODEL_NAME = "gpt-4o-mini"

dirname = os.path.dirname(__file__)

def extract_data_csv():
    data_list = []

    with open(dirname + "/../Data/Data_collection.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data_list.append(row)

    return data_list

def fowler_examples_to_json():
    data = {}
    for folder in os.listdir(constants.FOWLER_DATASET_PATH):
        data[folder] = {}

        before_refact_file = os.path.join(constants.FOWLER_DATASET_PATH, folder, "BeforeRefact.java")
        after_refact_file = os.path.join(constants.FOWLER_DATASET_PATH, folder, "PostRefact.java")

        with open(before_refact_file, "r") as before_refact, open(after_refact_file, "r") as after_refact:
            data[folder]["BeforeRefact"] = before_refact.read()
            data[folder]["AfterRefact"] = after_refact.read()

    with open(constants.FOWLER_EX_JSON_FILE, "w") as fowler_ex_json_file:
        json.dump(data, fowler_ex_json_file, indent=4)


def rules_cvs_to_json():

    data = {}

    with open(dirname + "/../Data/rules.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            refact_name = row["Name"].upper()

            if "-" in refact_name:
                split = refact_name.split("-")
                super_category = split[0]
                sub_category = split[1]

                if not super_category in data:
                    data[super_category] = {}
                data[super_category][sub_category] = {}
                data[super_category][sub_category]["Ref-Finder ID"] = row["ID"]
                data[super_category][sub_category]["Rule"] = row["Logic Rule"]
                data[super_category][sub_category]["Description"] = row["English Description"]
                    
            else:
                data[refact_name] = {}
                data[refact_name]["Ref-Finder ID"] = row["ID"]
                data[refact_name]["Rule"] = row["Logic Rule"]
                data[refact_name]["Description"] = row["English Description"]

        
    with open(constants.RULES_JSON_FILE, "w") as rules_json_file:
        json.dump(data, rules_json_file, indent=4)

def find_rule(refact_method, json_data):
    rule = []
    if refact_method in json_data:
        if "Rule" not in json_data[refact_method]:
            for sub_rule in json_data[refact_method]:
                rule.append(sub_rule + constants.SEPARATOR + json_data[refact_method][sub_rule]["Rule"])
        else:
            rule.append(json_data[refact_method]["Rule"])

    return rule


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

def fill_context_template(code):

    with open(constants.CONTEXT_TEMPLATE_FILE, "r") as context_template_file:
        context_template = context_template_file.read()
        context_template = context_template.replace("<code>", code)

    return context_template

def fill_rule_template(refact_method, rules, code):

    nb_rules = len(rules)

    if nb_rules == 0:
        return ""
    
    if nb_rules == 1:
        with open(constants.RULE_TEMPLATE_FILE, "r") as rule_template_file:
            rule_template = rule_template_file.read()
            rule_template = rule_template.replace("<refactoring method>", refact_method)
            rule_template = rule_template.replace("<rule>", rules[0])
            rule_template = rule_template.replace("<code>", code)
    else:
        rule_list = ""
        for sub_rule in rules:
            rule_list += sub_rule + "\n"
        with open(constants.MULTI_RULE_TEMPLATE_FILE, "r") as multi_rule_template_file:
            rule_template = multi_rule_template_file.read()
            rule_template = rule_template.replace("<refactoring method>", refact_method)
            rule_template = rule_template.replace("<number>", str(nb_rules))
            rule_template = rule_template.replace("<rules>", rule_list)
            rule_template = rule_template.replace("<code>", code)
    
    return rule_template
            

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

    API_KEY = open(dirname + "/../OpenAI_key.txt", "r").read()

    with open(constants.REFACT_METHODS_JSON_FILE, "r+") as REFACT_METHODS_JSON_FILE, open(constants.RULES_JSON_FILE, "r") as rules_json_file, open(constants.FOWLER_EX_JSON_FILE, "r") as fowler_ex_json_file:
        json_data = json.load(REFACT_METHODS_JSON_FILE)
        rules_data = json.load(rules_json_file)
        fowler_ex_data = json.load(fowler_ex_json_file)

        data_list = extract_data_csv()

        client = OpenAI(api_key=API_KEY)

        json_llm_generated_code = {}

        for f_fowler_type in tqdm(fowler_ex_data):
            f_before_refact_code = fowler_ex_data[f_fowler_type]["BeforeRefact"]
            f_after_refact_code = fowler_ex_data[f_fowler_type]["AfterRefact"]

            f_rules = find_rule(f_fowler_type, rules_data)

            f_zero_shot_prompt = fill_zero_shot_template(f_fowler_type, f_before_refact_code)
            f_instruc_prompt = fill_instructions_template(f_fowler_type, instruc=json_data[f_fowler_type]["Mechanics"], code=f_before_refact_code)
            f_context_prompt = fill_context_template(code=f_before_refact_code)
            f_rule_prompt = fill_rule_template(f_fowler_type, rules=f_rules, code=f_before_refact_code)

            f_zero_shot_generated_code = get_openai_response(f_zero_shot_prompt, client)
            f_instruc_generated_code = get_openai_response(f_instruc_prompt, client)
            if f_rule_prompt:
                f_rule_generated_code = get_openai_response(f_rule_prompt, client)
            f_context_generated_code = get_openai_response(f_context_prompt, client)


            fowler_ex_id = "FOWLER_EX_" + f_fowler_type
            json_llm_generated_code[fowler_ex_id] = {}
            json_llm_generated_code[fowler_ex_id]["RefactMethod"] = f_fowler_type
            json_llm_generated_code[fowler_ex_id]["BeforeRefact"] = f_before_refact_code
            json_llm_generated_code[fowler_ex_id]["AfterRefact"] = f_after_refact_code
            json_llm_generated_code[fowler_ex_id]["ZeroShotCode"] = f_zero_shot_generated_code
            json_llm_generated_code[fowler_ex_id]["InstrucCode"] = f_instruc_generated_code
            json_llm_generated_code[fowler_ex_id]["ContextCode"] = f_context_generated_code
            if f_rule_prompt:
                json_llm_generated_code[fowler_ex_id]["RulesCode"] = f_rule_generated_code

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
            context_prompt = fill_context_template(code=before_refact_code)

            rules = find_rule(f_fowler_type, rules_data)

            rule_prompt = fill_rule_template(fowler_type, rules=rules, code=before_refact_code)

            zero_shot_generated_code = get_openai_response(zero_shot_prompt, client)
            instruc_generated_code = get_openai_response(instruc_prompt, client)
            few_shot_generated_code = get_openai_response(few_shot_prompt, client)
            context_generated_code = get_openai_response(context_prompt, client)
            if rule_prompt:
                rule_generated_code = get_openai_response(rule_prompt, client)

            # Write to JSON format
            csv_id = example["\ufeffID"]
            json_llm_generated_code[csv_id] = {}
            json_llm_generated_code[csv_id]["RefactMethod"] = fowler_type
            json_llm_generated_code[csv_id]["BeforeRefact"] = example["BeforeRefact"]
            json_llm_generated_code[csv_id]["AfterRefact"] = example["AfterRefact"]
            json_llm_generated_code[csv_id]["ZeroShotCode"] = zero_shot_generated_code
            json_llm_generated_code[csv_id]["InstrucCode"] = instruc_generated_code
            json_llm_generated_code[csv_id]["FewShotCode"] = few_shot_generated_code
            json_llm_generated_code[csv_id]["ContextCode"] = context_generated_code
            if rule_prompt:
                json_llm_generated_code[csv_id]["RulesCode"] = rule_generated_code

    with open("./src/json_files/new_run.json", "w") as llm_json:
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
        all_prompt_types = ["ZeroShotCode", "InstrucCode", "FewShotCode", "ContextCode", "RulesCode"]

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
