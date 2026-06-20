# Misc
SEPARATOR = ": "

# Constants for Fowler Catalog PDF
CHAP6_INDEX = 120
LAST_PAGE_INDEX = 454
TITLES_CONST = {
    "color": "-8568482",
    "font": "Source Sans Pro"
}

# Refactoring methods that have no rules
RULES_EXCEPTION = [9, 11, 29, 61, 68, 70, 71]


FOWLER_PDF_FILE = "./../Data/Fowler.pdf"

# JSON files
JSON_FILES_PATH = "./json_files/"
RULES_JSON_FILE = "./json_files/rules.json"
REFACT_METHODS_JSON_FILE = "./json_files/refactoring_methods.json"
LLM_CODE_JSON_FILE = "./json_files/llm_generated_code.json"
CODEBLEU_JSON_FILE = "./json_files/codebleu.json"
RESULT_SUMMARY_JSON_FILE = "./json_files/results_summary.json"
FOWLER_EX_JSON_FILE = "./json_files/fowler_examples.json"
FINAL_RESULTS_JSON_FILE = "./json_files/final_results.json"
FINAL_RESULTS_FOWLER_JSON_FILE = "./json_files/final_results_fowler.json"
FINAL_RESULTS_DS_JSON_FILE = "./json_files/final_ds_results.json"
FINAL_RESULTS_DS_FOWLER_JSON_FILE = "./json_files/final_ds_results_fowler.json"

# Template files
CONTEXT_TEMPLATE_FILE = "./prompt_templates/context_template.txt"
INSTRUCTIONS_TEMPLATE_FILE = "./prompt_templates/instructions_template.txt"
RULE_TEMPLATE_FILE = "./prompt_templates/rule_template.txt"
MULTI_RULE_TEMPLATE_FILE = "./prompt_templates/multi_rule_template.txt"
ZERO_SHOT_TEMPLATE_FILE = "./prompt_templates/zero_shot_template.txt"
FEW_SHOT_TEMPLATE_FILE = "./prompt_templates/few_shot_template.txt"

LLM_AGREEMENT_TEMPLATE_FILE = "./prompt_templates/llm_agreement_template.txt"

# Folder paths
FOWLER_DATASET_PATH = "./Data/FowlerDataset"
EXTERNAL_DATASET_PATH = "./Data/ExternalDataset"
RESULTS_PATH = "./results/"

# Prompt Types
FOWLER_PROMPT_TYPES = ["ZeroShotCode", "InstrucCode", "ContextCode", "RulesCode"]
PROMPT_TYPES = ["ZeroShotCode", "FewShotCode", "InstrucCode", "ContextCode", "RulesCode"]

#Exceptions
FILE_LEVEL_EXCEPTIONS = ["INTRODUCE SPECIAL CASE", "REPLACE FUNCTION WITH COMMAND"]