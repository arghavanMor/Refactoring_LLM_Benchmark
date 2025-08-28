
import os
import constants
import json
import tempfile
from tqdm import tqdm
from pyccmetrics import Metrics
import csv
#Need tree-sitter==0.20.1

def calculate_metrics_from_json(filename, json_keys_array, is_fowler_ex=True):
    with open(constants.JSON_FILES_PATH + "/" + filename, "r") as json_data:
        data = json.load(json_data)
        results = {}
        for ex in data:
            for key in json_keys_array:
                if key not in data[ex]:
                    continue
                with tempfile.NamedTemporaryFile(delete=False, suffix=".java") as temp_file:
                    temp_file_path = temp_file.name
                    temp_file.write(data[ex][key].encode("utf-8"))
                    temp_file.close()

                    metrics = Metrics(file_path=temp_file_path)
                    metrics.calculate()
                    refact_method = ex if is_fowler_ex else data[ex]["RefactMethod"] + "-" + ex
                    if refact_method.startswith("FOWLER_EX_"):
                        refact_method = refact_method.replace("FOWLER_EX_", "")
                    if refact_method not in results:
                        results[refact_method] = {}
                    results[refact_method][key] = {}
                    results[refact_method][key]["Total CC"] = str(metrics.metrics_dict["VG_sum"])
                    results[refact_method][key]["Total method calls"] = str(metrics.metrics_dict["FOUT_sum"])
                    results[refact_method][key]["Total lines of code"] = str(metrics.metrics_dict["TLOC"])
                    os.remove(temp_file_path)

        return results
    
def combine_fowler_runs_into_json(nb_runs):
    result = calculate_metrics_from_json(filename="fowler_examples.json", json_keys_array=["BeforeRefact", "AfterRefact"])
    for x in tqdm(range(nb_runs)):
        run_nb = x + 1
        filename = "fowler_run#" + str(run_nb) + ".json"
        current_run_name = "Run #" + str(run_nb)
        run_result = calculate_metrics_from_json(filename=filename, json_keys_array=constants.FOWLER_PROMPT_TYPES)
        for key in run_result:
            if key in result:
                new_run_data = {}
                new_run_data[current_run_name] = {}
                new_run_data[current_run_name]= run_result[key]
                result[key].update(new_run_data)
    with open(constants.FINAL_RESULTS_JSON_FILE, "w") as export:
        json.dump(result, export, indent=4)


def calculate_metrics_from_folder(run_folder_name, process_ground_truth=False):
    code_folders = ["after"] if not process_ground_truth else ["before", "after-ground-truth"]
    results_path = os.path.join(constants.RESULTS_PATH, run_folder_name)
    results = {}
    for folder in os.listdir(results_path):
        folder_path = os.path.join(results_path, folder)
        for sub_folder in os.listdir(folder_path):
            split = sub_folder.split("&")
            id = split[0]
            refact_method = split[1]
            prompt_type = split[2]

            for state in code_folders:
                state_folder = os.path.join(folder_path, sub_folder, state)
                state_file = os.path.join(state_folder, os.listdir(state_folder)[0])
                state_metrics = Metrics(file_path=state_file)
                state_metrics.calculate()

                json_key = refact_method + "-" + id
                if json_key not in results:
                    results[json_key] = {}

                sub_key = prompt_type
                if process_ground_truth and state == "before":
                    sub_key = "BeforeRefact"
                if process_ground_truth and state == "after-ground-truth":
                    sub_key = "AfterRefact"
                
                results[json_key][sub_key] = {}
                results[json_key][sub_key]["Total CC"] = str(state_metrics.metrics_dict["VG_sum"])
                results[json_key][sub_key]["Total method calls"] = str(state_metrics.metrics_dict["FOUT_sum"])
                results[json_key][sub_key]["Total lines of code"] = str(state_metrics.metrics_dict["TLOC"])

    return results

def test2(run_folder_name, ex_id, process_ground_truth=False):
    code_folders = ["after"] if not process_ground_truth else ["before", "after-ground-truth"]
    results_path = os.path.join(constants.RESULTS_PATH, run_folder_name)
    results = {}
    for folder in os.listdir(results_path):
        folder_path = os.path.join(results_path, folder)
        for sub_folder in os.listdir(folder_path):
            split = sub_folder.split("&")
            
            id = split[0]
            if id != ex_id:
                continue

            refact_method = split[1]
            prompt_type = split[2]

            for state in code_folders:
                state_folder = os.path.join(folder_path, sub_folder, state)
                state_file = os.path.join(state_folder, os.listdir(state_folder)[0])
                state_metrics = Metrics(file_path=state_file)
                state_metrics.calculate()

                json_key = refact_method + "-" + id
                if json_key not in results:
                    results[json_key] = {}

                sub_key = prompt_type
                if process_ground_truth and state == "before":
                    sub_key = "BeforeRefact"
                if process_ground_truth and state == "after-ground-truth":
                    sub_key = "AfterRefact"
                
                results[json_key][sub_key] = {}
                results[json_key][sub_key]["Total CC"] = str(state_metrics.metrics_dict["VG_sum"])
                results[json_key][sub_key]["Total method calls"] = str(state_metrics.metrics_dict["FOUT_sum"])
                results[json_key][sub_key]["Total lines of code"] = str(state_metrics.metrics_dict["TLOC"])

    return results

            

# This function is used to calculate metrics for a number of runs and put them inside a JSON file
def combine_runs_into_json(nb_runs, is_fowler_ex=True):
    # Change filename for GPT or DeepSeek
    result = calculate_metrics_from_json(filename="deepseek_results/ds_run#1.json", json_keys_array=["BeforeRefact", "AfterRefact"], is_fowler_ex=is_fowler_ex)
    # for ex in result:
    #     for exception in constants.FILE_LEVEL_EXCEPTIONS:
    #         if ex.startswith(exception):
    #             id = ex.split("-")[1]
    #             result[ex] = calculate("run#1", ex_id=id, process_ground_truth=True)
    for x in tqdm(range(nb_runs)):
        run_nb = x + 1
        filename = "deepseek_results/ds_run#" + str(run_nb) + ".json"
        current_run_name = "Run #" + str(run_nb)
        run_result = calculate_metrics_from_json(filename=filename, json_keys_array=constants.PROMPT_TYPES, is_fowler_ex=is_fowler_ex)

        for key in run_result:
            if key in result:
                new_run_data = {}
                new_run_data[current_run_name] = {}
                new_run_data[current_run_name]= run_result[key]
                result[key].update(new_run_data)
    # Change this filename as well for GPT or DeepSeek
    # filename = constants.FINAL_RESULTS_FOWLER_JSON_FILE if is_fowler_ex else constants.FINAL_RESULTS_JSON_FILE
    filename = constants.FINAL_RESULTS_DS_FOWLER_JSON_FILE if is_fowler_ex else constants.FINAL_RESULTS_DS_JSON_FILE
    with open(filename, "w") as export:
        json.dump(result, export, indent=4)

def get_raw_data(is_fowler):
    raw_data = []
    ground_truth = calculate_metrics_from_json(filename="deepseek_results/ds_run#1.json", json_keys_array=["BeforeRefact", "AfterRefact"], is_fowler_ex=False)
    # result = calculate_metrics_from_json(filename="deepseek_results/fowler_ds_run#1.json", json_keys_array=constants.FOWLER_PROMPT_TYPES, is_fowler_ex=True)
    for refact_method in ground_truth:
        for prompt in ground_truth[refact_method]:
            for metric in ground_truth[refact_method][prompt]:
                value = ground_truth[refact_method][prompt][metric]
                new_refact_method = refact_method
                if "-" in refact_method:
                    new_refact_method = refact_method.split("-")[0]
                raw_data.append({"Refactoring method": new_refact_method, "Prompt": prompt, "Metric": metric, "Value": value})
    for i in range(1,6):
        filename = "deepseek_results/ds_run#" + str(i) +".json"
        results = calculate_metrics_from_json(filename=filename, json_keys_array=constants.PROMPT_TYPES, is_fowler_ex=is_fowler)
        for refact_method in results:
            for prompt in results[refact_method]:
                for metric in results[refact_method][prompt]:
                    value = results[refact_method][prompt][metric]
                    new_refact_method = refact_method
                    if "-" in refact_method:
                        new_refact_method = refact_method.split("-")[0]
                    raw_data.append({"Refactoring method": new_refact_method, "Prompt": prompt, "Metric": metric, "Value": value})
    
    with open('./src/analysis/raw_data_ds.csv', "w") as file:
        fieldnames = ["Refactoring method", "Prompt", "Metric", "Value"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(raw_data)

# Run combine_runs_into_json() to generate metrics file
# combine_runs_into_json(nb_runs=5, is_fowler_ex=False)

# get_raw_data(False)\
