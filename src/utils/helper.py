import json
from deepdiff import DeepDiff
import subprocess
import os
from git import Repo
import shutil

def llm_generated_code_enhancer():
    data_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/llm_generated_code1.json"
    results_path = "/src/run#19_processed.json"
    with open(data_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)


    prompt_approach =  ["ZeroShotCode", "InstrucCode", "FewShotCode"]
    for generated_code_item in generated_code_data.values():
        for prompt_type in prompt_approach:
            generated_code_item[prompt_type] = {'methods': [generated_code_item[prompt_type], ], 'classes':[], 'others':[]}

    json_object = json.dumps(generated_code_data, indent=4)

    with open(results_path, 'w') as results_file:
        results_file.write(json_object)

def data_collector():
    data_collection_path = "/src/Data/Data_collection.json"
    results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results"
    junit4_repo = Repo("/Users/jeancarlorspaul/IdeaProjects/junit4/")

    antlr4_repo = Repo("/Users/jeancarlorspaul/IdeaProjects/antlr4/")
    antlr4_repo.git.checkout("5e05b71e8b1cd52cf0e77559786cc4c18dc85c37")
    with open(data_collection_path, 'r') as data_collection_file:
        data_collection = json.load(data_collection_file)

    #results_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/Data_collection_results.json"
    #with open(data_path, 'r') as Data_collection_file:
    #    data_collection = json.load(Data_collection_file)
    project_list = ['antlr4', 'junit4']
    local_repository = "/Users/jeancarlorspaul/IdeaProjects"
    for datum in data_collection:
        id = datum["\ufeffID"]
        print(id)
        for runs_path in os.listdir(results_path):
            print(runs_path)
            for project in project_list:
                if project == 'antlr4':
                    print(project)
                    refactored_code_path = os.path.join(results_path, runs_path + "/" + project)
                    for folder in os.listdir(refactored_code_path):
                        if id in folder:
                            print(folder)
                            commitID_after = datum["commitID_after"]
                            print(commitID_after)
                            antlr4_repo.git.checkout(commitID_after)
                            after_ground_truth_path = refactored_code_path + "/" + folder + "/" + 'after-ground-truth'
                            print(after_ground_truth_path)
                            os.makedirs(after_ground_truth_path, exist_ok=True)
                            after_ground_truth_file = local_repository + "/" + project + "/" + datum["path_before"].replace("\\", "/")
                            shutil.copy(after_ground_truth_file, after_ground_truth_path)

                else:
                    print(project)
                    refactored_code_path = os.path.join(results_path, runs_path + "/" + project)
                    for folder in os.listdir(refactored_code_path):
                        if id in folder:
                            print(folder)
                            commitID_after = datum["commitID_after"]
                            print(commitID_after)
                            junit4_repo.git.checkout(commitID_after)
                            after_ground_truth_path = refactored_code_path + "/" + folder + "/" + 'after-ground-truth'
                            print(after_ground_truth_path)
                            os.makedirs(after_ground_truth_path, exist_ok=True)
                            after_ground_truth_file = local_repository + "/" + project + "/" + datum["path_before"].replace("\\", "/")
                            shutil.copy(after_ground_truth_file, after_ground_truth_path)
                print("-"*100)



                #if id in folder:
                #run_path = results_path +"/"+ runs_path
                #antlr4_run_path = run_path + '/antlr4'
                #for factored_code_path in os.listdir(antlr4_run_path):
                 #   print(factored_code_path)
        '''for key, value in other_results_collection.items():
            if datum["\ufeffID"] in key :
                value["path_before"] = datum["path_before"].replace("\\", "/")
                print(value.keys())'''
        print("="*150)



    #json_object = json.dumps(other_results_collection, indent=4)

    #with open(enhanced_results_path, 'w') as enhanced_results_file:
     #   enhanced_results_file.write(json_object)


if __name__ == "__main__":
    #data_collector()


