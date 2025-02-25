import json
from deepdiff import DeepDiff
import subprocess

def llm_generated_code_enhancer():
    data_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/llm_generated_code1.json"
    results_path = "/src/run#19_processed.json"
    with open(data_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)


    prompt_approach =  ["ZeroShotCode", "InstrucCode", "FewShotCode"]
    for generated_code_item in generated_code_data.values():
        for prompt_type in prompt_approach:
            generated_code_item[prompt_type] = {'methods': [generated_code_item[prompt_type], ], 'classes':[], 'others':[]}

    json_object = json.dumps(generated_code_data, indent=4)

    with open(results_path, 'w') as results_file:
        results_file.write(json_object)

def data_collector():
    other_results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results_summary_run#5.json"
    enhanced_results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/enhanced_results_summary_run#5.json"
    with open(other_results_path, 'r') as result_collection_file:
        other_results_collection = json.load(result_collection_file)

    data_path = "/src/utils/Data_collection.json"
    results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/Data_collection_results.json"
    with open(data_path, 'r') as Data_collection_file:
        data_collection = json.load(Data_collection_file)

    for datum in data_collection:
        print(datum["\ufeffID"])
        for key, value in other_results_collection.items():
            if datum["\ufeffID"] in key :
                value["path_before"] = datum["path_before"].replace("\\", "/")
                print(value.keys())
        print("="*150)

    json_object = json.dumps(other_results_collection, indent=4)

    with open(enhanced_results_path, 'w') as enhanced_results_file:
        enhanced_results_file.write(json_object)


if __name__ == "__main__":
    data_collector()
