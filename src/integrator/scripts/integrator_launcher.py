import os
import json

from src.integrator.scripts.results_summary_maker import results_summary_maker
from src.integrator.scripts.main import main

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

def refact_integrator_launcher():
    llm_list = ["chat_gpt_4o_mini", "deep_seek" ]
    for llm_id in llm_list:
        for item in range(3,6):
            which_run = "/run#" + str(item)
            llm_generated_code_path = "src/integrator/llm_generated_code/" + llm_id + which_run + "_processed.json"
            before_and_after_path_prefix = "src/evaluation/results/" + llm_id + which_run + "/before_and_after/"
            antlr4_results_path = "src/evaluation/results/" + llm_id + which_run + "/antlr4/antlr4_results" + ".json"
            antlr4_results_summary_path ="src/evaluation/results/" + llm_id + which_run + "/antlr4/antlr4_results_summary" + ".json"
            junit4_results_path = "src/evaluation/results/" + llm_id + which_run + "/junit4/junit4_results" + ".json"

            config_preparation(llm_generated_code_path, before_and_after_path_prefix, antlr4_results_path, antlr4_results_summary_path,
                junit4_results_path)
            print(llm_generated_code_path, before_and_after_path_prefix, antlr4_results_path, antlr4_results_summary_path,
                   junit4_results_path)
            print("@"*200)
            main(llm_id, which_run)
            results_summary_maker()

def review_refact_integrator_launcher(error_type):
    llm_list = ["chat_gpt_4o_mini", "deep_seek"]
    for llm_id in llm_list:
        parent_dir = "review-" + llm_id
        for item in range(1, 6):
            which_run = "/" + error_type +  "_run#" + str(item)
            llm_generated_code_path = "src/integrator/llm_generated_code/" + parent_dir + which_run + ".json"
            before_and_after_path_prefix =  "src/evaluation/results/" + parent_dir + which_run + "/before_and_after/"
            antlr4_results_path = "src/evaluation/results/" + parent_dir + which_run + "/antlr4/antlr4_results" + ".json"
            antlr4_results_summary_path ="src/evaluation/results/" + parent_dir + which_run + "/antlr4/antlr4_results_summary" + ".json"
            junit4_results_path = "src/evaluation/results/" + parent_dir + which_run + "/junit4/junit4_results" + ".json"

            config_preparation(llm_generated_code_path, before_and_after_path_prefix, antlr4_results_path, antlr4_results_summary_path,
                              junit4_results_path)
            print("@"*200)
            main(llm_id, which_run)
            results_summary_maker()

if __name__ == "__main__":
    pass


