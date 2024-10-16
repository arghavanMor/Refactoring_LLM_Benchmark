from codebleu import calc_codebleu
import constants
import json
from tqdm import tqdm
#Need tree-sitter==0.23.1


with open(constants.LLM_CODE_JSON_FILE_NAME, "r+") as llm_generated_json_file:
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

with open(constants.CODEBLEU_JSON_FILE_NAME, "w") as llm_json:
    json.dump(codebleu_json, llm_json)