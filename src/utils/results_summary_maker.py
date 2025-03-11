import json

def results_summary_maker():
    results_summary_path = "./results/deep_seek/antlr4_results/antlr4_results_summary_run#2.json"

    with open('./results/deep_seek/antlr4_results/antlr4_results.json', 'r') as file:
        results = json.load(file)

    for item in results.keys():
        if isinstance(results[item], dict):
            for inner_item in results[item].keys():
                if isinstance(results[item][inner_item], list):
                    results[item][inner_item] = len(results[item][inner_item])
        elif isinstance(results[item], list):
            results[item] = len(results[item])

    json_object = json.dumps(results, indent=4)
    with open(results_summary_path, 'w') as results_file:
        results_file.write(json_object)


results_summary_maker()