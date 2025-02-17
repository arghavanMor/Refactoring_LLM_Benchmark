import json
from deepdiff import DeepDiff

def llm_generated_code_enhancer():
    data_path = "/Users/jeancarlorspaul/Documents/Doc_Carl/Poly/LLM_Refactoring_Project/Refactoring_AST/src/llm_generated_code.json"
    results_path = "/Users/jeancarlorspaul/Documents/Doc_Carl/Poly/LLM_Refactoring_Project/Refactoring_AST/src/llm_generated_code6.json"
    with open(data_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)


    prompt_approach =  ["ZeroShotCode", "InstrucCode", "FewShotCode"]
    for generated_code_item in generated_code_data.values():
        for prompt_type in prompt_approach:
            generated_code_item[prompt_type] = {'methods': [generated_code_item[prompt_type], ], 'classes':[], 'others':[]}

    json_object = json.dumps(generated_code_data, indent=4)

    with open(results_path, 'w') as results_file:
        results_file.write(json_object)

def results_comparator(result1_path, result2_path):
    with open(result1_path, 'r') as result1_file:
        result1_path_dict = json.load(result1_file)

    with open(result2_path, 'r') as result2_file:
        result2_path_dict = json.load(result2_file)

    diff = DeepDiff(result1_path_dict, result2_path_dict)
    print(diff)

if __name__ == "__main__":
    result1_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results_summary.json"
    result2_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results_summary_run#1.json"
    results_comparator(result1_path, result2_path)






