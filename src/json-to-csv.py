import json
import csv
import constants

def json_to_csv(filename, reviewers_array=[]):
    with open(constants.JSON_FILES_PATH + "/" + filename, 'r') as json_file:
        data = json.load(json_file)

        filename_no_extension = filename.split("/")[1].split(".")[0]

        data_file = open("./Data/" + filename_no_extension + ".csv", "w")

        csv_writer = csv.writer(data_file)

        field_names = ["RefactMethod", "BeforeRefact", "AfterRefact", "PromptType", "LlmCode"]


        for reviewer in reviewers_array:
            field_names.append(reviewer)

        csv_writer.writerow(field_names)

        for sample in data:
            refact_method = data[sample]["RefactMethod"]
            before_refact = data[sample]["BeforeRefact"]
            after_refact = data[sample]["AfterRefact"]
            if "ZeroShotCode" in data[sample]:
                csv_writer.writerow([refact_method, before_refact, after_refact, "ZeroShot", data[sample]["ZeroShotCode"]])
            if "InstrucCode" in data[sample]:
                csv_writer.writerow([refact_method, before_refact, after_refact, "Instruc", data[sample]["InstrucCode"]])
            if "ContextCode" in data[sample]:
                csv_writer.writerow([refact_method, before_refact, after_refact, "Context", data[sample]["ContextCode"]])
            if "RulesCode" in data[sample]:
                csv_writer.writerow([refact_method, before_refact, after_refact, "Rules", data[sample]["RulesCode"]])


json_to_csv("deepseek_results/fowler_ds_run#2.json")