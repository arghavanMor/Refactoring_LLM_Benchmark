import json
import constants
import collections
from tqdm import tqdm
from prettytable import PrettyTable 
import pandas as pd


def compile_data_into_csv(nb_runs):

    data_collection = {}

    for x in tqdm(range(nb_runs)):
        run_nb = x + 1
        antlr_run_path = "./src/antlr4_results_summary_run#" + str(run_nb ) + ".json"
        junit_run_path = "./src/junit4_results_run#" + str(run_nb ) + ".json"

        with open(antlr_run_path, "r+") as antlr_json_file, open(junit_run_path, "r+") as junit_json_file:
            antlr_data = json.load(antlr_json_file)
            junit_data = json.load(junit_json_file)

            for test_case in antlr_data:
                # Ignores the first two lines of the JSON
                if not isinstance(antlr_data[test_case], dict):
                    continue
                id = antlr_data[test_case]["refactoring_id"]
                refact_type = antlr_data[test_case]["refactoring_type"]
                prompt_type = antlr_data[test_case]["prompt_approach_item"]
                key = antlr_data[test_case]["refactoring_id"] + "&" + refact_type + "&" + prompt_type
                new_failed_test = antlr_data.get(test_case, {}).get("new_failed_test", 0)
                new_test_error = antlr_data.get(test_case, {}).get("new_test_error", 0)
                compilation = antlr_data.get(test_case, {}).get("compiled", 0)

                if key not in data_collection:
                    data_collection[key] = {}
                    data_collection[key]["ID"] = id
                    data_collection[key]["Refactoring Method"] = refact_type
                    data_collection[key]["Prompt"] = prompt_type
                    data_collection[key]["New Failed Tests"] = 0
                    data_collection[key]["New Test Errors"] = 0
                    data_collection[key]["Compilation"] = 0

                    data_collection[key]["New Failed Tests"] += new_failed_test
                    data_collection[key]["New Test Errors"] += new_test_error
                    data_collection[key]["Compilation"] += compilation
                else:
                    data_collection[key]["New Failed Tests"] += new_failed_test
                    data_collection[key]["New Test Errors"] += new_test_error
                    data_collection[key]["Compilation"] += compilation

            for test_case in junit_data:
                # Ignores the first two lines of the JSON
                if not isinstance(junit_data[test_case], dict):
                    continue
                id = junit_data[test_case]["refactoring_id"]
                refact_type = junit_data[test_case]["refactoring_type"]
                prompt_type = junit_data[test_case]["prompt_approach_item"]
                key = junit_data[test_case]["refactoring_id"] + "&" + refact_type + "&" + prompt_type
                new_failed_test = junit_data.get(test_case, {}).get("new_failed_test", 0)
                new_test_error = junit_data.get(test_case, {}).get("new_test_error", 0)
                compilation = junit_data.get(test_case, {}).get("compiled", 0)
                
                if key not in data_collection:
                    data_collection[key] = {}
                    data_collection[key]["ID"] = id
                    data_collection[key]["Refactoring Method"]= refact_type
                    data_collection[key]["Prompt"] = prompt_type
                    data_collection[key]["New Failed Tests"] = 0
                    data_collection[key]["New Test Errors"] = 0
                    data_collection[key]["Compilation"] = 0

                    data_collection[key]["New Failed Tests"] += new_failed_test
                    data_collection[key]["New Test Errors"] += new_test_error
                    data_collection[key]["Compilation"] += compilation

                else:
                    data_collection[key]["New Failed Tests"] += new_failed_test
                    data_collection[key]["New Test Errors"] += new_test_error
                    data_collection[key]["Compilation"] += compilation
        
        compiled_data = []

        for key in data_collection:
            id = data_collection[key]["ID"]
            refact_type = data_collection[key]["Refactoring Method"]
            prompt_type = data_collection[key]["Prompt"]
            new_failed_test = data_collection[key]["New Failed Tests"]
            new_test_error = data_collection[key]["New Test Errors"]
            compilation = data_collection[key]["Compilation"]

            compiled_data.append({
                    "ID": id,
                    "Refactoring Method": refact_type,
                    "Prompt": prompt_type,
                    "New Failed Tests": new_failed_test/compilation if compilation else 0,
                    "New Test Errors": new_test_error/compilation if compilation else 0,
                    "Compilation": compilation/nb_runs
                })
        
        df = pd.DataFrame(compiled_data)
        df.to_csv("./compilation_results.csv", index=False)


def generate_table(data):
    table_fields = ["Refactoring Type", "New Failed Tests", "New Test Errors"]
    table = PrettyTable(table_fields)

    for refact_type in data:
        table.add_row([refact_type, "", ""])
        for prompt_type in data[refact_type]:
            new_failed_test = data[refact_type][prompt_type]["new_failed_test"]
            new_test_error = data[refact_type][prompt_type]["new_test_error"]
            table.add_row([prompt_type, new_failed_test, new_test_error])

    print(table)

# compile_data_into_csv(5)

with open(constants.REFACT_METHODS_JSON_FILE) as test:
    data = json.load(test)

    count = 0

    for ex in data:
        count+=1
        print(ex)

    print(count)