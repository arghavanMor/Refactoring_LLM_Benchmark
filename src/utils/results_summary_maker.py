import json
from config import antlr4_project

def results_summary_maker():
    antlr4_results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results/chat_gpt_4o_mini/antlr4_results/antlr4_results_run#1.json" #antlr4_project["results_path"]
    antlr4_results_summary_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results/chat_gpt_4o_mini/antlr4_results/antlr4_results_summary_run#1.json" #antlr4_project["results_summary_path"]

    with open(antlr4_results_path, 'r') as file:
        results = json.load(file)

    for item in results.keys():
        if isinstance(results[item], dict):
            for inner_item in results[item].keys():
                if isinstance(results[item][inner_item], list):
                    results[item][inner_item] = len(results[item][inner_item])
        elif isinstance(results[item], list):
            results[item] = len(results[item])

    json_object = json.dumps(results, indent=4)
    with open(antlr4_results_summary_path, 'w') as results_file:
        results_file.write(json_object)

if __name__ == '__main__':
    pass
    results_summary_maker()
