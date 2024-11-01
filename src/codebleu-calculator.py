from codebleu import calc_codebleu
import constants
import json
from tqdm import tqdm
#Need tree-sitter==0.23.1

from prettytable import PrettyTable 
import collections

def generate_codebleu_json():
    with open(constants.LLM_CODE_JSON_FILE, "r+") as llm_generated_json_file:
        json_data = json.load(llm_generated_json_file)

        codebleu_json = {}

        for test_case in tqdm(json_data):

            reference = json_data[test_case]["AfterRefact"]

            zero_shot_code = json_data[test_case]["ZeroShotCode"]
            instruc_code = json_data[test_case]["InstrucCode"]
            few_shot_code = json_data[test_case]["FewShotCode"]

            zero_shot_score = calc_codebleu([reference], [zero_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
            instruc_score = calc_codebleu([reference], [instruc_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
            few_shot_score = calc_codebleu([reference], [few_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)

            codebleu_json[test_case] = {}
            codebleu_json[test_case]["RefactMethod"] = json_data[test_case]["RefactMethod"].upper()
            codebleu_json[test_case]["ZeroShotCodeBleu"] = zero_shot_score["codebleu"]
            codebleu_json[test_case]["InstrucCodeBleu"] = instruc_score["codebleu"]
            codebleu_json[test_case]["FewShotCodeBleu"] = few_shot_score["codebleu"]
    # {
    #   'codebleu': 0.5537, 
    #   'ngram_match_score': 0.1041, 
    #   'weighted_ngram_match_score': 0.1109, 
    #   'syntax_match_score': 1.0, 
    #   'dataflow_match_score': 1.0
    # }

    with open(constants.CODEBLEU_JSON_FILE, "w") as llm_json:
        json.dump(codebleu_json, llm_json, indent=4)


def find_average_codebleu_scores():

    zeroshot_scores = collections.defaultdict(list)
    instruc_scores = collections.defaultdict(list)
    fewshot_scores = collections.defaultdict(list)

    compiled_scores = {}

    with open(constants.CODEBLEU_JSON_FILE, "r") as codebleu_json:
        json_data = json.load(codebleu_json)

        for id in json_data:
            current_id = json_data[id]
            zeroshot_scores[current_id["RefactMethod"]].append(current_id["ZeroShotCodeBleu"])
            instruc_scores[current_id["RefactMethod"]].append(current_id["InstrucCodeBleu"])
            fewshot_scores[current_id["RefactMethod"]].append(current_id["FewShotCodeBleu"])
    
    for extract_method, zeroshot_score in zeroshot_scores.items():
        compiled_scores[extract_method] = {}
        compiled_scores[extract_method]["ZeroShotAverageScore"] = sum(zeroshot_score)/len(zeroshot_score)
    
    for extract_method, instruc_score in instruc_scores.items():
        compiled_scores[extract_method]["InstrucAverageScore"] = sum(instruc_score)/len(instruc_score)

    for extract_method, fewshot_score in fewshot_scores.items():
        compiled_scores[extract_method]["FewShotAverageScore"] = sum(fewshot_score)/len(fewshot_score)
    
    return compiled_scores


def generate_table(average_scores):

    table = PrettyTable(["Refactoring Method", "Average Zero-Shot CodeBLEU Score", "Average Instruction CodeBLEU Score", "Average Few-Shots CodeBLEU Score"])

    for refact_method in average_scores:
        table.add_row([refact_method, average_scores[refact_method]["ZeroShotAverageScore"], average_scores[refact_method]["InstrucAverageScore"], average_scores[refact_method]["FewShotAverageScore"]])

    print(table)


generate_codebleu_json()
# generate_table(find_average_codebleu_scores())