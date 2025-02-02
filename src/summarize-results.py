import json
import constants
from prettytable import PrettyTable 


def compile_data():

    compiled_data = {}

    with open(constants.RESULT_SUMMARY_JSON_FILE, "r+") as result_json_file:
        json_data = json.load(result_json_file)

        prompt_types = ["ZeroShotCode", "InstrucCode", "FewShotCode"]
        data_types = ["new_failed_test", "new_test_error"]

        for test_case in json_data:
            if not isinstance(json_data[test_case], dict):
                continue
            refact_type = json_data[test_case]["refactoring_type"]
            prompt_type = json_data[test_case]["prompt_approach_item"]
            new_failed_test = json_data[test_case]["new_failed_test"]
            new_test_error = json_data[test_case]["new_test_error"]

            if refact_type not in compiled_data:
                compiled_data[refact_type] = {}
                for type in prompt_types:
                    compiled_data[refact_type][type] = {}
                    for data_type in data_types:
                        compiled_data[refact_type][type][data_type] = 0
            
            compiled_data[refact_type][prompt_type]["new_failed_test"] += new_failed_test
            compiled_data[refact_type][prompt_type]["new_test_error"] += new_test_error

    return compiled_data

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





generate_table(compile_data())