from src.generator.scripts import constants
import json
import csv
from openai import OpenAI
from tqdm import tqdm
import re
import os
from pprint import pprint

# GPT-4.0 Mini
# MODEL_NAME = "gpt-4o-mini"

# DeepSeek
MODEL_NAME = "deepseek-chat"
BASE_URL = "https://api.deepseek.com"

dirname = os.path.dirname(__file__)

def extract_data_csv():
    data_list = []

    with open(dirname + "/Data/benchmark_collection/Real_scenario_collection.csv", "r") as csv_file:
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

def fill_reviewed_zero_shot_template(refact_method, code, previous_error):
    with open(constants.REVIEWED_ZERO_SHOT_TEMPLATE_FILE, "r") as zero_shot_template_file:
        zero_shot_template = zero_shot_template_file.read()
        zero_shot_template = zero_shot_template.replace("<refactoring method>", refact_method)
        zero_shot_template = zero_shot_template.replace("<code>", code)
        zero_shot_template = zero_shot_template.replace("<previous_error>", previous_error)

    return zero_shot_template

def fill_instructions_template(refact_method, instruc, code):
    
    with  open(constants.INSTRUCTIONS_TEMPLATE_FILE, "r") as instruc_template_file:
        instruc_template = instruc_template_file.read()
        instruc_template = instruc_template.replace("<refactoring method>", refact_method)
        instruc_template = instruc_template.replace("<steps>", instruc)
        instruc_template = instruc_template.replace("<code>", code)

    return instruc_template

def fill_reviewed_instructions_template(refact_method, instruc, code, previous_error):

    with  open(constants.REVIEWED_INSTRUCTIONS_TEMPLATE_FILE, "r") as instruc_template_file:
        instruc_template = instruc_template_file.read()
        instruc_template = instruc_template.replace("<refactoring method>", refact_method)
        instruc_template = instruc_template.replace("<steps>", instruc)
        instruc_template = instruc_template.replace("<code>", code)
        instruc_template = instruc_template.replace("<previous_error>", previous_error)

    return instruc_template

def fill_few_shot_template(refact_method, examples, code):
    
    with open(constants.FEW_SHOT_TEMPLATE_FILE, "r") as few_shot_template_file:
        few_shot_template = few_shot_template_file.read()
        few_shot_template = few_shot_template.replace("<refactoring method>", refact_method)
        few_shot_template = few_shot_template.replace("<refactoring examples>", examples)
        few_shot_template = few_shot_template.replace("<code>", code)
    
    return few_shot_template

def fill_reviewed_few_shot_template(refact_method, examples, code, previous_error):

    with open(constants.REVIEWED_FEW_SHOT_TEMPLATE_FILE, "r") as few_shot_template_file:
        few_shot_template = few_shot_template_file.read()
        few_shot_template = few_shot_template.replace("<refactoring method>", refact_method)
        few_shot_template = few_shot_template.replace("<refactoring examples>", examples)
        few_shot_template = few_shot_template.replace("<code>", code)
        few_shot_template = few_shot_template.replace("<previous_error>", previous_error)

    return few_shot_template

def fill_context_template(code):

    with open(constants.CONTEXT_TEMPLATE_FILE, "r") as context_template_file:
        context_template = context_template_file.read()
        context_template = context_template.replace("<code>", code)

    return context_template

def fill_reviewed_context_template(code, previous_error):

    with open(constants.REVIEWED_CONTEXT_TEMPLATE_FILE, "r") as context_template_file:
        context_template = context_template_file.read()
        context_template = context_template.replace("<code>", code)
        context_template = context_template.replace("<previous_error>", previous_error)

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

def fill_reviewed_rule_template(refact_method, rules, code, previous_error):

    nb_rules = len(rules)

    if nb_rules == 0:
        return ""

    if nb_rules == 1:
        with open(constants.REVIEWED_RULE_TEMPLATE_FILE, "r") as rule_template_file:
            rule_template = rule_template_file.read()
            rule_template = rule_template.replace("<refactoring method>", refact_method)
            rule_template = rule_template.replace("<rule>", rules[0])
            rule_template = rule_template.replace("<code>", code)
            rule_template = rule_template.replace("<previous_error>", previous_error)
    else:
        rule_list = ""
        for sub_rule in rules:
            rule_list += sub_rule + "\n"
        with open(constants.REVIEWED_MULTI_RULE_TEMPLATE_FILE, "r") as multi_rule_template_file:
            rule_template = multi_rule_template_file.read()
            rule_template = rule_template.replace("<refactoring method>", refact_method)
            rule_template = rule_template.replace("<number>", str(nb_rules))
            rule_template = rule_template.replace("<rules>", rule_list)
            rule_template = rule_template.replace("<code>", code)
            rule_template = rule_template.replace("<previous_error>", previous_error)

    return rule_template

def write_example(ex_nb, before_refact, after_refact):
    ex = "".join(("Example #", str(ex_nb), ": "))
    return " ".join((ex, "Before Refactoring:", str(before_refact), "\nAfter Refactoring:", str(after_refact)))

def get_openai_response(prompt, client, model_name):

    message = {
        'role': 'user',
        'content': prompt
    }

    response = client.chat.completions.create(
        model=model_name,
        messages=[message]
    )

    chatbot_response = response.choices[0].message.content
    return chatbot_response.strip()

def get_failed_refactoring(llm, run_number, project_name):
    base_path = "/Users/jeancarlorspaul/Downloads/Refactoring_LLM_Benchmark-pdf-extractor/src/review/results"
    parsing_failures = dict()
    parsing_failures_list = list()
    compilation_failures_list = list()
    compilation_failures = dict()


    parsing_failures_path_suffix = llm + "/" + run_number + "/" + project_name + "/" + "refactoring_parsing" + "/" + "stderr" + "/" "parsing_stderr_summary.json"
    parsing_failures_path = base_path + "/" + parsing_failures_path_suffix


    compilation_failures_path_suffix = llm + "/" + run_number + "/" + project_name + "/" + "compilation" + "/" + "stdout" + "/" "compilation_error_summary.json"
    compilation_failures_path = base_path + "/" + compilation_failures_path_suffix

    print(compilation_failures_path)

    with open(parsing_failures_path, "r") as parsing_failures_file, open(compilation_failures_path, "r") as compilation_failures_file:
        parsing_failures_data = json.load(parsing_failures_file)
        compilation_failures_data = json.load(compilation_failures_file)

    for parsing_failure_key, parsing_failure_value in parsing_failures_data.items():
        if "total" in parsing_failure_key:
            continue
        parsing_failure_key_components = parsing_failure_key.split("&")[:-1]
        parsing_failures_list.append((parsing_failure_key_components, parsing_failure_value),)

    for compilation_failure_key, compilation_failure_value in compilation_failures_data.items():
        if "total" in compilation_failure_key or "summary" in compilation_failure_key:
            continue
        compilation_failure_key_components = compilation_failure_key.split("&")[:-1]
        compilation_failures_list.append((compilation_failure_key_components, compilation_failure_value),)

    parsing_failures["failures"] = parsing_failures_list
    compilation_failures["failures"] = compilation_failures_list
    #pprint(parsing_failures)
    #pprint(compilation_failures)
    return parsing_failures, compilation_failures

# Example filename: "run#1.json"
def generate_llm_json(filename, api_key_path, model_name):

    API_KEY = open(dirname + api_key_path, "r").read()
    # API_KEY = open(dirname + "/../OpenAI_key.txt", "r").read()

    with open(constants.REFACT_METHODS_JSON_FILE, "r+") as refact_methods_json_file, open(constants.RULES_JSON_FILE, "r") as rules_json_file, open(
            constants.FOWLER_EX_JSON_FILE, "r") as fowler_ex_json_file:
        json_data = json.load(refact_methods_json_file)
        rules_data = json.load(rules_json_file)
        fowler_ex_data = json.load(fowler_ex_json_file)

        data_list = extract_data_csv()

        # Add URL if Deepseek
        if model_name=="deepseek-chat":
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        
        else:
            client = OpenAI(api_key=API_KEY)


        f_json_llm_generated_code = {}

        for f_fowler_type in tqdm(fowler_ex_data):
            f_before_refact_code = fowler_ex_data[f_fowler_type]["BeforeRefact"]
            f_after_refact_code = fowler_ex_data[f_fowler_type]["AfterRefact"]

            f_rules = find_rule(f_fowler_type, rules_data)

            f_zero_shot_prompt = fill_zero_shot_template(f_fowler_type, f_before_refact_code)
            f_instruc_prompt = fill_instructions_template(f_fowler_type, instruc=json_data[f_fowler_type]["Mechanics"], code=f_before_refact_code)
            f_context_prompt = fill_context_template(code=f_before_refact_code)
            f_rule_prompt = fill_rule_template(f_fowler_type, rules=f_rules, code=f_before_refact_code)

            f_zero_shot_generated_code = get_openai_response(f_zero_shot_prompt, client, model_name=model_name)
            f_instruc_generated_code = get_openai_response(f_instruc_prompt, client, model_name=model_name)
            if f_rule_prompt:
                f_rule_generated_code = get_openai_response(f_rule_prompt, client, model_name=model_name)
            f_context_generated_code = get_openai_response(f_context_prompt, client, model_name=model_name)


            fowler_ex_id = "FOWLER_EX_" + f_fowler_type
            f_json_llm_generated_code[fowler_ex_id] = {}
            f_json_llm_generated_code[fowler_ex_id]["RefactMethod"] = f_fowler_type
            f_json_llm_generated_code[fowler_ex_id]["BeforeRefact"] = f_before_refact_code
            f_json_llm_generated_code[fowler_ex_id]["AfterRefact"] = f_after_refact_code
            f_json_llm_generated_code[fowler_ex_id]["ZeroShotCode"] = f_zero_shot_generated_code
            f_json_llm_generated_code[fowler_ex_id]["InstrucCode"] = f_instruc_generated_code
            f_json_llm_generated_code[fowler_ex_id]["ContextCode"] = f_context_generated_code
            if f_rule_prompt:
                f_json_llm_generated_code[fowler_ex_id]["RulesCode"] = f_rule_generated_code

        f_filename_output = os.path.join(constants.JSON_FILES_PATH, "fowler_" + filename)
        with open(f_filename_output, "w") as llm_json:
            json.dump(f_json_llm_generated_code, llm_json, indent=4)

        
        json_llm_generated_code = {}

        for example in tqdm(data_list):

            nb_ex = 0

            fowler_type = example["Fowler_type"].upper()

            before_refact_code = example["BeforeRefact"]

            zero_shot_prompt = fill_zero_shot_template(fowler_type, before_refact_code)

            refact_examples = ""

            if fowler_type not in json_data:
                print("ERROR: " + fowler_type)
                continue

            if "Mechanics" in json_data[fowler_type]:
                instruc_prompt = fill_instructions_template(fowler_type, instruc=json_data[fowler_type]["Mechanics"], code=before_refact_code)

            for subtitle in json_data[fowler_type]:
                if subtitle.startswith("Example"):
                    nb_ex += 1
                    refact_examples += "Example " + str(nb_ex) + ": "
                    refact_examples += subtitle + ":\n"
                    refact_examples += json_data[fowler_type][subtitle] + "\n"
                    break

            if nb_ex == 0:
                nb_ex +=1
                before_refact_file = os.path.join(constants.EXTERNAL_DATASET_PATH, fowler_type, "BeforeRefact.java")
                after_refact_file = os.path.join(constants.EXTERNAL_DATASET_PATH, fowler_type, "PostRefact.java")

                with open(before_refact_file, "r") as bef_ref_file, open(after_refact_file, "r") as aft_ref_file:
                    before_refact_ex = bef_ref_file.read()
                    after_refact_ex = aft_ref_file

                ex_before_refact = write_example(nb_ex, before_refact=before_refact_ex, after_refact=after_refact_ex)
            
                refact_examples += ex_before_refact + "\n"

            refact_examples += write_example(nb_ex + 1, before_refact=fowler_ex_data[fowler_type]["BeforeRefact"], after_refact=fowler_ex_data[fowler_type]["AfterRefact"])

            few_shot_prompt = fill_few_shot_template(fowler_type, examples=refact_examples, code=before_refact_code)
            context_prompt = fill_context_template(code=before_refact_code)

            rules = find_rule(fowler_type, rules_data)

            rule_prompt = fill_rule_template(fowler_type, rules=rules, code=before_refact_code)

            zero_shot_generated_code = get_openai_response(zero_shot_prompt, client, model_name=model_name)
            instruc_generated_code = get_openai_response(instruc_prompt, client, model_name=model_name)
            few_shot_generated_code = get_openai_response(few_shot_prompt, client, model_name=model_name)
            context_generated_code = get_openai_response(context_prompt, client, model_name=model_name)
            if rule_prompt:
                rule_generated_code = get_openai_response(rule_prompt, client, model_name=model_name)

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

    filename_output = os.path.join(constants.JSON_FILES_PATH, filename)
    with open(filename_output, "w") as llm_json:
        json.dump(json_llm_generated_code, llm_json, indent=4)

def generate_llm_json_after_review_caller(filename, api_key_path, model_name):
    run_number = "run#" + filename[16]

    if model_name=="deepseek-chat":
        API_KEY = open(dirname + "/DeepSeek_key.txt", "r").read()
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    else:
        API_KEY = open(dirname + "/OpenAI_key.txt", "r").read()
        client = OpenAI(api_key=API_KEY)

    parsing_failures, compilation_failures = get_failed_refactoring("chat_gpt_4o_mini", run_number, "antlr4")

    json_llm_generated_code = {}

    if 'parsing' in filename:
        for meta_parsing_failure, parsing_failure_message in parsing_failures['failures']:
            ID_parsing_failure = meta_parsing_failure[0]
            fowler_type = meta_parsing_failure[1]
            prompt_strategy = meta_parsing_failure[2]
            generate_llm_json_after_review(client, model_name, ID_parsing_failure, fowler_type, prompt_strategy, str(parsing_failure_message), json_llm_generated_code)
            print("-"*200)
            print(meta_parsing_failure)
            #break

    if 'compilation' in filename:
        for meta_compilation_failure, compilation_failure_message in compilation_failures['failures']:
            ID_compilation_failure = meta_compilation_failure[0]
            fowler_type = meta_compilation_failure[1]
            prompt_strategy = meta_compilation_failure[2]
            generate_llm_json_after_review(client, model_name, ID_compilation_failure, fowler_type, prompt_strategy, str(compilation_failure_message), json_llm_generated_code)
            print("*"*200)
            print(meta_compilation_failure)
            #break
    filename = model_name + "/" + filename
    filename_output = os.path.join(constants.REVIEWED_JSON_FILES_PATH, filename)
    print(filename_output)
    with open(filename_output, "w") as llm_json:
        json.dump(json_llm_generated_code, llm_json, indent=4)

def generate_llm_json_after_review(client, model_name,  ID, fowler_type, prompt_strategy, error_message, json_llm_generated_code):
    with open(constants.REFACT_METHODS_JSON_FILE, "r+") as refact_methods_json_file, open(constants.RULES_JSON_FILE, "r") as rules_json_file, open(
            constants.FOWLER_EX_JSON_FILE, "r") as fowler_ex_json_file:
        json_data = json.load(refact_methods_json_file)
        rules_data = json.load(rules_json_file)
        fowler_ex_data = json.load(fowler_ex_json_file)

        data_list = extract_data_csv()
        sample_to_keep = [item for item in data_list if item['\ufeffID'] == ID]

        nb_ex = 0

        before_refact_code = sample_to_keep[0]["BeforeRefact"]
        after_refact_code = sample_to_keep[0]["AfterRefact"]

        fowler_type = fowler_type.replace("_", " ")

        json_llm_generated_code.setdefault(ID, {})
        json_llm_generated_code[ID].setdefault("RefactMethod", fowler_type)
        json_llm_generated_code[ID].setdefault("BeforeRefact", before_refact_code)
        json_llm_generated_code[ID].setdefault("AfterRefact", after_refact_code)

        if prompt_strategy == "ZeroShotCode":
            zero_shot_prompt = fill_reviewed_zero_shot_template(fowler_type, before_refact_code, previous_error=error_message)
            #print(zero_shot_prompt)
            zero_shot_generated_code = get_openai_response(zero_shot_prompt, client, model_name=model_name)
            json_llm_generated_code[ID]["ZeroShotCode"] = zero_shot_generated_code
        if "Mechanics" in json_data[fowler_type] and prompt_strategy == "InstrucCode":
            instruc_prompt = fill_reviewed_instructions_template(fowler_type, instruc=json_data[fowler_type]["Mechanics"], code=before_refact_code, previous_error=error_message)
            #print(instruc_prompt)
            instruc_generated_code = get_openai_response(instruc_prompt, client, model_name=model_name)
            json_llm_generated_code[ID]["InstrucCode"] = instruc_generated_code
        if prompt_strategy == "ContextCode":
            context_prompt = fill_reviewed_context_template(code=before_refact_code, previous_error=error_message)
            #print(context_prompt)
            context_generated_code = get_openai_response(context_prompt, client, model_name=model_name)
            json_llm_generated_code[ID]["ContextCode"] = context_generated_code
        if prompt_strategy == "RulesCode":
            rules = find_rule(fowler_type, rules_data)
            rule_prompt = fill_reviewed_rule_template(fowler_type, rules=rules, code=before_refact_code, previous_error=error_message)
            #print(rule_prompt)
            rule_generated_code = get_openai_response(rule_prompt, client, model_name=model_name)
            json_llm_generated_code[ID]["RulesCode"] = rule_generated_code
        if prompt_strategy == "FewShotCode" :
            refact_examples = ""
            for subtitle in json_data[fowler_type]:
                if subtitle.startswith("Example"):
                    nb_ex += 1
                    refact_examples += "Example " + str(nb_ex) + ": "
                    refact_examples += subtitle + ":\n"
                    refact_examples += json_data[fowler_type][subtitle] + "\n"
                    break

            if nb_ex == 0:
                nb_ex +=1
                before_refact_file = os.path.join(constants.EXTERNAL_DATASET_PATH, fowler_type, "BeforeRefact.java")
                after_refact_file = os.path.join(constants.EXTERNAL_DATASET_PATH, fowler_type, "PostRefact.java")

                with open(before_refact_file, "r") as bef_ref_file, open(after_refact_file, "r") as aft_ref_file:
                    before_refact_ex = bef_ref_file.read()
                    after_refact_ex = aft_ref_file

                ex_before_refact = write_example(nb_ex, before_refact=before_refact_ex, after_refact=after_refact_ex)

                refact_examples += ex_before_refact + "\n"

            refact_examples += write_example(nb_ex + 1, before_refact=fowler_ex_data[fowler_type]["BeforeRefact"], after_refact=fowler_ex_data[fowler_type]["AfterRefact"])

            few_shot_prompt = fill_reviewed_few_shot_template(fowler_type, examples=refact_examples, code=before_refact_code, previous_error=error_message)
            #print(few_shot_prompt)
            few_shot_generated_code = get_openai_response(few_shot_prompt, client, model_name=model_name)
            json_llm_generated_code[ID]["FewShotCode"] = few_shot_generated_code

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

def clean_llm_output(filename):

    # Access modifier is left mandatory on purpose
    method_regex = r"(public|protected|private|static) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"
    regex = re.compile(method_regex)

    with open(constants.JSON_FILES_PATH + filename, "r+") as llm_json:

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

def clean_reviewed_llm_output(model_name, filename):
    filename_to_clean = model_name + "/" + filename
    filename_to_clean = os.path.join(constants.REVIEWED_JSON_FILES_PATH, filename_to_clean)
    # Access modifier is left mandatory on purpose
    method_regex = r"(public|protected|private|static) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])"
    regex = re.compile(method_regex)

    #return None
    with open(filename_to_clean, "r+") as llm_json:

        json_data = json.load(llm_json)
        all_prompt_types = ["ZeroShotCode", "InstrucCode", "FewShotCode", "ContextCode", "RulesCode"]
        out_of_prompt_types = ['RefactMethod', 'BeforeRefact', 'AfterRefact']

        for test_case, data_value in json_data.items():
            for prompt in all_prompt_types:
                if prompt not in data_value.keys() or prompt in out_of_prompt_types:
                    continue
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

def clean_deepseek_fowler_run():
    with open(constants.JSON_FILES_PATH + "/" + "fowler_ds_run#5.json", "r+") as json_file:
        data = json.load(json_file)
        for ex in data:
            for prompt_type in constants.FOWLER_PROMPT_TYPES:
                if prompt_type not in data[ex]:
                    continue
                prompt_output = data[ex][prompt_type]
                match = re.search(r'```java(.*?)```', prompt_output, re.DOTALL)
                if match:
                    data[ex][prompt_type] = match.group(0)
            
        json_file.seek(0)
        json.dump(data, json_file, indent=4)
        json_file.truncate()

def clean_reviewed_generated_code(model_name, filename_to_clean):
    filename_to_clean = model_name + "/" + filename
    filename_to_clean = os.path.join(constants.REVIEWED_JSON_FILES_PATH, filename_to_clean)
    print(filename_to_clean)
    with open(filename_to_clean, "r+") as json_file:
        data = json.load(json_file)
        for ex in data:
            for prompt_type in constants.FOWLER_PROMPT_TYPES:
                if prompt_type not in data[ex]:
                    continue
                prompt_output = data[ex][prompt_type]
                match = re.search(r'```java(.*?)```', prompt_output, re.DOTALL)
                if match:
                    data[ex][prompt_type] = match.group(0)

        json_file.seek(0)
        json.dump(data, json_file, indent=4)
        json_file.truncate()

# clean_llm_output("ds_run#5_processed.json")
# generate_llm_json(filename="ds_run#5.json")
#get_failed_refactoring("chat_gpt_4o_mini", "run#1", "antlr4")
for item in range(1,6):
    filename_template = "parsing_run#*.json"
    filename = filename_template.replace("*", str(item))
    clean_reviewed_llm_output("gpt-4o-mini", filename)
    #generate_llm_json_after_review_caller(filename, "api_key_path", "gpt-4o-mini")
