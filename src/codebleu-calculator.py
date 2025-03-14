from codebleu import calc_codebleu
import constants
import json
from tqdm import tqdm
import csv
#Need tree-sitter==0.23.1

import collections
import numpy as np
import pandas as pd


# This function adds CodeBLEU value to final_result.json
# Make sure it's changed if it's DeepSeek
def generate_codebleu_to_final_results(nb_runs, is_fowler_ex=True):
    #final_results_file = constants.FINAL_RESULTS_FOWLER_JSON_FILE if is_fowler_ex else constants.FINAL_RESULTS_JSON_FILE
    final_results_file = constants.FINAL_RESULTS_DS_FOWLER_JSON_FILE if is_fowler_ex else constants.FINAL_RESULTS_DS_JSON_FILE
    with open(final_results_file, "r+") as final_results_json:
        final_results = json.load(final_results_json)
        for x in tqdm(range(nb_runs)):
            run_nb = x + 1
            # Change if it's DeepSeek
            #filename = "gpt-4.0-mini/fowler_run#" + str(run_nb) +".json" if is_fowler_ex else "gpt-4.0-mini/run#" + str(run_nb) +".json"
            filename = "deepseek_results/fowler_ds_run#" + str(run_nb) +".json" if is_fowler_ex else "deepseek_results/ds_run#" + str(run_nb) +".json"
            current_run_name = "Run #" + str(run_nb)

            with open(constants.JSON_FILES_PATH + filename, "r") as json_file:

                current_run_data = json.load(json_file)

                for test_case in tqdm(current_run_data):

                    reference = current_run_data[test_case]["AfterRefact"]

                    zero_shot_code = current_run_data[test_case]["ZeroShotCode"]
                    instruc_code = current_run_data[test_case]["InstrucCode"]
                    context_code = current_run_data[test_case]["ContextCode"]

                    zero_shot_score = calc_codebleu([reference], [zero_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    instruc_score = calc_codebleu([reference], [instruc_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    context_score = calc_codebleu([reference], [context_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    
                    refact_method = current_run_data[test_case]["RefactMethod"].upper() if is_fowler_ex else current_run_data[test_case]["RefactMethod"].upper()+ "-"+ test_case
                    final_results[refact_method][current_run_name]["ZeroShotCode"]["CodeBleu"] = zero_shot_score["codebleu"]
                    final_results[refact_method][current_run_name]["InstrucCode"]["CodeBleu"] = instruc_score["codebleu"]
                    final_results[refact_method][current_run_name]["ContextCode"]["CodeBleu"] = context_score["codebleu"]

                    if "RulesCode" in current_run_data[test_case]:
                        rules_code = current_run_data[test_case]["RulesCode"]
                        rules_score = calc_codebleu([reference], [rules_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                        final_results[refact_method][current_run_name]["RulesCode"]["CodeBleu"] = rules_score["codebleu"]


                    if "FewShotCode" in current_run_data[test_case]:
                        few_shot_code = current_run_data[test_case]["FewShotCode"]
                        few_shot_score = calc_codebleu([reference], [few_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                        final_results[refact_method][current_run_name]["FewShotCode"]["CodeBleu"] = few_shot_score["codebleu"]
        
        final_results_json.seek(0)
        json.dump(final_results, final_results_json, indent=4)
        final_results_json.truncate()

# This function aggregates all the results into the average across all runs.
def generate_results_into_csv():
    refact_method_collection = collections.defaultdict(list)
    metrics = ["CodeBleu", "Total CC", "Total method calls", "Total lines of code"]

    # Load data from the JSON file
    with open(constants.FINAL_RESULTS_DS_FOWLER_JSON_FILE, "r") as json_file:
        data = json.load(json_file)

        # Loop through all examples in the JSON file
        for ex in data:
            refact_method = ex.split("-")[0]  # Split the example name to get the refactoring method
            prompt_values = {prompt: {metric: [] for metric in metrics} for prompt in constants.PROMPT_TYPES + ["BeforeRefact", "AfterRefact"]}

            for ground_truth in ["BeforeRefact", "AfterRefact"]:
                if ground_truth in data[ex]:
                    for metric in metrics:
                        value = data[ex][ground_truth].get(metric)
                        if value is not None:
                            try:
                                value = float(value)  # Convert to float
                                prompt_values[ground_truth][metric].append(value)
                            except ValueError:
                                # If the value cannot be converted to float, skip it or set it as NaN
                                print(f"Warning: Non-numeric value for {metric} in {ground_truth} for {ex}, skipping.")
                                continue
            # Iterate through all runs (1 to 5)
            for run in range(1, 6):
                run_key = f"Run #{run}"
                
                # Iterate through each prompt type in constants.PROMPT_TYPES
                for prompt_type in constants.PROMPT_TYPES:
                    if prompt_type in data[ex][run_key]:
                        # For each metric, extract the value and append it to prompt_values
                        for metric in metrics:
                            value = data[ex][run_key][prompt_type].get(metric)

                            # Ensure value is a numeric type (convert if it's a string)
                            if value is not None:
                                try:
                                    value = float(value)  # Convert to float
                                    prompt_values[prompt_type][metric].append(value)
                                except ValueError:
                                    # If the value cannot be converted to float, skip it or set it as NaN
                                    print(f"Warning: Non-numeric value for {metric} in {prompt_type} for {ex}, skipping.")
                                    continue

            # After collecting all values for a prompt type, store them in refact_method_collection
            for prompt_type, metric_values in prompt_values.items():
                for metric, values in metric_values.items():
                    refact_method_collection[refact_method].append({
                        "Refactoring method": refact_method,
                        "Prompt": prompt_type,
                        "Metric": metric,
                        "Values": values,
                    })

        # List to store final grouped results
        grouped_results = []

        # Iterate through each refactoring method and its associated results
        for refact_method, results in refact_method_collection.items():

            # Group the results by prompt type and metric
            prompt_type_group_values = {prompt_type: {metric: [] for metric in metrics} for prompt_type in constants.PROMPT_TYPES + ["BeforeRefact", "AfterRefact"]}

            # Aggregate values for each prompt and metric
            for result in results:
                prompt_type_group_values[result["Prompt"]][result["Metric"]].extend(result["Values"])

            # Calculate the average for each group (prompt type and metric)
            for prompt_type, metric_values in prompt_type_group_values.items():
                for metric, values in metric_values.items():
                    if values:  # Ensure there are values to calculate the mean
                        average_of_group = np.mean(values)  # Calculate the average
                        average_of_group = round(average_of_group, 3)
                    else:
                        average_of_group = np.nan  # If no values, set to NaN

                    # Append the grouped result (including the average)
                    grouped_results.append({
                        "Refactoring method": refact_method,
                        "Prompt": prompt_type,
                        "Metric": metric,
                        "Average Value": average_of_group  # Add average value here
                        # "Number of examples": len(values)/len(constants.PROMPT_TYPES)
                    })

    # Convert the grouped results into a DataFrame
    df = pd.DataFrame(grouped_results)
    df.to_csv("./src/analysis/final_ds_results_fowler.csv", index=False)

def add_codebleu_to_raw_data(nb_runs, is_fowler_ex):
    with open("./src/analysis/raw_data_ds.csv", "a") as raw_data_csv:
        writer = csv.writer(raw_data_csv)
        raw_data_csv.seek(0, 2)
        for x in tqdm(range(nb_runs)):
            run_nb = x + 1
            filename = "deepseek_results/fowler_ds_run#" + str(run_nb) +".json" if is_fowler_ex else "deepseek_results/ds_run#" + str(run_nb) +".json"
            # current_run_name = "Run #" + str(run_nb)

            with open(constants.JSON_FILES_PATH + filename, "r") as json_file:

                current_run_data = json.load(json_file)

                for test_case in tqdm(current_run_data):

                    reference = current_run_data[test_case]["AfterRefact"]

                    zero_shot_code = current_run_data[test_case]["ZeroShotCode"]
                    instruc_code = current_run_data[test_case]["InstrucCode"]
                    context_code = current_run_data[test_case]["ContextCode"]

                    zero_shot_score = calc_codebleu([reference], [zero_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    instruc_score = calc_codebleu([reference], [instruc_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    context_score = calc_codebleu([reference], [context_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                    refact_method = current_run_data[test_case]["RefactMethod"].upper()



                    if "RulesCode" in current_run_data[test_case]:
                        rules_code = current_run_data[test_case]["RulesCode"]
                        rules_score = calc_codebleu([reference], [rules_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                        rules = [refact_method, "RulesCode", "CodeBleu",rules_score["codebleu"]]
                        writer.writerow(rules)

                    if "FewShotCode" in current_run_data[test_case]:
                        few_shot_code = current_run_data[test_case]["FewShotCode"]
                        few_shot_score = calc_codebleu([reference], [few_shot_code], lang="java", weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
                        few_shot = [refact_method, "FewShotCode", "CodeBleu",few_shot_score["codebleu"]]
                        writer.writerow(few_shot)

                    zero_shot = [refact_method, "ZeroShotCode", "CodeBleu",zero_shot_score["codebleu"]]
                    instruc = [refact_method, "InstrucCode", "CodeBleu",instruc_score["codebleu"]]
                    context = [refact_method, "ContextCode", "CodeBleu",context_score["codebleu"]]
                    
                    writer.writerow(zero_shot)
                    writer.writerow(instruc)
                    writer.writerow(context)


# Add CodeBLEU to final_results.json files
# generate_codebleu_to_final_results(nb_runs=5, is_fowler_ex=False)

# Average value across all runs in final_results.json and generates a csv
# generate_results_into_csv()

add_codebleu_to_raw_data(nb_runs=5, is_fowler_ex=False)