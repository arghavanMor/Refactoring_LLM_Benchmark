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


FOWLER_PDF_FILE = "./Data/Fowler.pdf"

# JSON files
RULES_JSON_FILE = "./src/json_files/rules.json"
REFACT_METHODS_JSON_FILE = "./src/json_files/refactoring_methods.json"
LLM_CODE_JSON_FILE = "./src/json_files/llm_generated_code.json"
CODEBLEU_JSON_FILE = "./src/json_files/codebleu.json"
RESULT_SUMMARY_JSON_FILE = "./src/json_files/results_summary.json"
FOWLER_EX_JSON_FILE = "./src/json_files/fowler_examples.json"

# Template files
CONTEXT_TEMPLATE_FILE = "./src/prompt_templates/context_template.txt"
INSTRUCTIONS_TEMPLATE_FILE = "./src/prompt_templates/instructions_template.txt"
RULE_TEMPLATE_FILE = "./src/prompt_templates/rule_template.txt"
MULTI_RULE_TEMPLATE_FILE = "./src/prompt_templates/multi_rule_template.txt"
ZERO_SHOT_TEMPLATE_FILE = "./src/prompt_templates/zero_shot_template.txt"
FEW_SHOT_TEMPLATE_FILE = "./src/prompt_templates/few_shot_template.txt"

#Folder paths

FOWLER_DATASET_PATH = "./Data/FowlerDataset"