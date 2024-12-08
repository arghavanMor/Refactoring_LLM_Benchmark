import json

with open('antlr4_results.json', 'r') as file:
    results = json.load(file)


def results_summary_maker(results):
    with open("results_summary.txt", "w") as file:
        file.write("===================== Here are the results: =====================" + "\n\n")
    for item in results.keys():
        if isinstance(results[item], dict):
            with open("results_summary.txt", "a") as file:
                file.write("commit_hash: " + results[item]["commit_hash"] + "\n")
                file.write("refactoring_id: " + results[item]["refactoring_id"] + "\n")
                file.write("refactoring_type: " + results[item]["refactoring_type"] + "\n")
                file.write("prompt_approach_item: " + results[item]["prompt_approach_item"] + "\n")
            for inner_item in results[item].keys():
                if '_length' in inner_item:
                    with open("results_summary.txt", "a") as file:
                        file.write(inner_item + ": " + str(results[item][inner_item]) + "\n")
            with open("results_summary.txt", "a") as file:
                file.write("="*150 + "\n\n")

results_summary_maker(results)
