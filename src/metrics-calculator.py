
import os
import constants
import json
import tempfile
from tqdm import tqdm
from pyccmetrics import Metrics
#Need tree-sitter==0.20.1


# CODE_DIR = os.path.join(os.getcwd(), "Data/FowlerDataset/EXTRACT FUNCTION/Example: No Variables Out of Scope/Before Refact.java")

def calculate_metrics_from_json(filename, json_keys_array):
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
                    refact_method = ex
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
        filename = "fowler_run#" + str(run_nb) +".json"
        current_run_name = "Run #" + str(run_nb)
        run_result = {}
        run_result = calculate_metrics_from_json(filename=filename, json_keys_array=constants.FOWLER_PROMPT_TYPES)
        for key in run_result:
            if key in result:
                new_run_data = {}
                new_run_data[current_run_name] = {}
                new_run_data[current_run_name]= run_result[key]
                result[key].update(new_run_data)
            # else:
            #     result[key] = run_result[key]
    with open(constants.FINAL_RESULTS_JSON_FILE, "w") as export:
        json.dump(result, export, indent=4)



def calculate_metrics_from_folder(run_folder_name):
    results_path = os.path.join(constants.RESULTS_PATH, run_folder_name)
    for folder in os.listdir(results_path):
        folder_path = os.path.join(results_path, folder)
        for sub_folder in os.listdir(folder_path):
            before_refact_folder = os.path.join(folder_path, sub_folder, "before")
            after_refact_folder = os.path.join(folder_path, sub_folder,  "after")
            print(os.listdir(before_refact_folder))

# metrics = Metrics(file_path=CODE_DIR)
# metrics.calculate()

# print("Average CC: " + str(metrics.metrics_dict["VG_avg"]))
# print("Max CC: " + str(metrics.metrics_dict["VG_max"]))

# calculate_metrics_from_folder("run#1")
# print(calculate_metrics_from_json("fowler_run#5.json"))

combine_fowler_runs_into_json(5)