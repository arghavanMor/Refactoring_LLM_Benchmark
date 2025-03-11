import json
import constants
import collections
from tqdm import tqdm
from prettytable import PrettyTable 
import pandas as pd


# Use this function to compile compilation files (antlr4_results_summary_run#) into a CSV
def compile_data_into_csv(nb_runs):

    data_collection = {}

    for x in tqdm(range(nb_runs)):
        run_nb = x + 1
        antlr_run_path = "./src/results/deep_seek/antlr4_results/antlr4_results_run#" + str(run_nb ) + ".json"
        junit_run_path = "./src/results/deep_seek/junit4_results/junit4_results_run#" + str(run_nb ) + ".json"

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
        df.to_csv("./src/analysis/ds_compilation_results.csv", index=False)


compile_data_into_csv(nb_runs=5)
