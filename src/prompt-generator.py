import constants
import json
import csv



def extract_csv():
    data_list = []

    with open("../Data/Examples.csv", "r") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            data_list.append(row)

    return data_list

with open(constants.JSON_FILE_NAME, "r") as json_file:
    json_data = json.load(json_file)
    few_shot_template = open(constants.FEW_SHOT_TEMPLATE_NAME, "r").read()
    mechanics_template = open(constants.MECHANICS_TEMPLATE_NAME, "r").read()

    data_list = extract_csv()

    for example in data_list:

        fowler_type = example["Fowler_type"].upper()
        before_refact_code = example["BeforeRefact"]

        modified_mechanics_template = mechanics_template.replace("<refactoring method>", fowler_type)
        modified_mechanics_template = modified_mechanics_template.replace("<steps>", json_data[fowler_type]["Mechanics"])
        modified_mechanics_template = modified_mechanics_template.replace("<code>", before_refact_code)
        print(modified_mechanics_template + "\n\n")



# with open(constants.JSON_FILE_NAME, "r") as json_file:
#     json_data = json.load(json_file)
#     few_shot_template = open(constants.FEW_SHOT_TEMPLATE_NAME, "r").read()
#     mechanics_template = open(constants.MECHANICS_TEMPLATE_NAME, "r").read()
#     for refactoring_method in json_data:

#         for subtitle in json_data[refactoring_method]:
#             if subtitle == "Mechanics":
#                modified_mechanics_template = mechanics_template.replace("<refactoring method>", refactoring_method)
#                modified_mechanics_template = modified_mechanics_template.replace("<steps>", json_data[refactoring_method][subtitle])
#                print(modified_mechanics_template + "\n\n")
            
#             elif subtitle.startswith("Example"):
#                 modified_few_shot_template = few_shot_template.replace("<refactoring method>", refactoring_method)
#                 modified_few_shot_template = modified_few_shot_template.replace("<refactoring example>", json_data[refactoring_method][subtitle])
#                 print(modified_few_shot_template + "\n\n")


