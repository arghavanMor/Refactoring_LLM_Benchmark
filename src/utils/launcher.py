import os
import json
import results_summary_maker
from src import main



def config_preparation(llm_generated_code_path, before_and_after_path_prefix, antlr4_results_path, antlr4_results_summary_path,
                       junit4_results_path):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'config.json')

    with open(file_path, 'r') as file:
        config_data = json.load(file)

    config_data['llm_generated_code_path'] = llm_generated_code_path
    config_data['before_and_after_path_prefix'] = before_and_after_path_prefix
    config_data['target_projects']['antlr4']['results_path'] = antlr4_results_path
    config_data['target_projects']['antlr4']['results_summary_path'] = antlr4_results_summary_path
    config_data['target_projects']['junit4']['results_path'] = junit4_results_path

    json_object = json.dumps(config_data, indent=4)
    with open(file_path, 'w') as results_file:
         results_file.write(json_object)

def config_preparation_caller():

    for llm_id in ("chat_gpt_4o_mini", "deep_seek"):
        for item in range(4,6):
            which_run = "/run#" + str(item)
            llm_generated_code_path = "./llm_generated_code/" + llm_id + which_run + "_processed.json"
            before_and_after_path_prefix =  "./results/" + llm_id + which_run + "/before_and_after/"
            antlr4_results_path = "./results/" + llm_id + which_run + "/antlr4/antlr4_results" + ".json"
            antlr4_results_summary_path ="./results/" + llm_id + which_run + "/antlr4/antlr4_results_summary_run" + ".json"
            junit4_results_path = "./results/" + llm_id + which_run + "/junit4/junit4_results" + ".json"

            config_preparation(llm_generated_code_path, before_and_after_path_prefix, antlr4_results_path, antlr4_results_summary_path,
                junit4_results_path)
            main.main(llm_id, which_run)
            results_summary_maker.results_summary_maker()

config_preparation_caller()
