import git
from git import Repo
import os
import subprocess
import json
import datetime
import shutil
from utils import config
from utils.runner import compile_call, test
from utils.config import target_projects, initial_branch_name, jar_path, head_path, args_dict, env

llm_generated_code_path = config.llm_generated_code_path
data_collection_path = config.data_collection_path
prompt_approach = config.prompt_approach


def modifier_result_processing(is_refactored, before_and_after_path, repository_path, results_subdict, repo, branch_name, local_repository_path,
                               original_failed_test, original_test_error, results_dictionary):
    print(is_refactored, before_and_after_path, repository_path, results_subdict, repo, branch_name, local_repository_path,
     original_failed_test, original_test_error, results_dictionary)
    """
    if is_refactored == 0:
        after_path = before_and_after_path + "/" + "after"
        os.makedirs(after_path, exist_ok=True)
        if os.path.exists(repository_path):
            shutil.copy(repository_path, after_path)

        results_subdict['refactored'] = 1
        repo.git.add(all=True)
        repo.index.commit(branch_name)
        commit_hash = repo.head.commit.hexsha
        results_subdict['commit_hash'] = commit_hash

        compilation_return_code = compile_call(repo, local_repository_path, repo.head.commit.hexsha)
        if not compilation_return_code:
            results_subdict['compiled'] = 1
            if 'antlr4' in local_repository_path:
                failed_test, test_error = test(repo, local_repository_path, branch_name, repo.head.commit.hexsha)
                unreproduced_failed_test = ""
                new_failed_test = ""
                unreproduced_test_error = ""
                new_test_error = ""
                test_error_to_failed_test = ""
                failed_test_to_test_error = ""


                if not (failed_test == set()) :
                    unreproduced_failed_test = original_failed_test - failed_test
                    new_failed_test = failed_test - original_failed_test
                    results_subdict['failed_test'] = list(failed_test)
                    results_subdict['unreproduced_failed_test'] = list(unreproduced_failed_test)
                    results_subdict['new_failed_test'] =  list(new_failed_test)
                    if test_error == set() :
                        test_error_to_failed_test = failed_test.intersection(original_test_error)
                        results_subdict['test_error_to_failed_test'] =  list(test_error_to_failed_test)
                    else:
                        results_subdict['test_error_to_failed_test'] = []
                else:
                    results_subdict['failed_test'] = []
                    results_subdict['unreproduced_failed_test'] = []
                    results_subdict['new_failed_test'] =  []
                if not test_error == set() :
                    unreproduced_test_error = original_test_error - test_error
                    new_test_error = test_error - original_test_error
                    results_subdict['test_error'] = list(test_error)
                    results_subdict['unreproduced_test_error'] = list(unreproduced_test_error)
                    results_subdict['new_test_error'] = list(new_test_error)
                    if failed_test == set() :
                        failed_test_to_test_error = test_error.intersection(original_failed_test)
                        results_subdict['failed_test_to_test_error'] =  list(failed_test_to_test_error)
                    else:
                        results_subdict['failed_test_to_test_error'] = []
                else:
                    results_subdict['test_error'] = []
                    results_subdict['unreproduced_test_error'] = []
                    results_subdict['new_test_error'] = []
            else:
                total_test, total_failed_test, total_error_test = test(repo, local_repository_path, branch_name, repo.head.commit.hexsha)
                results_subdict['total_test'] = total_test
                results_subdict['total_failed_test'] = total_failed_test
                results_subdict['total_error_test'] = total_error_test
        else:
            results_subdict['compiled'] = 0
    else:
        if os.path.exists(before_and_after_path):
            shutil.rmtree(before_and_after_path)
        results_subdict['refactored'] = 0
        print("Refactoring failed")
    results_dictionary[branch_name] = results_subdict
    """

def modifier_processing(prompt_approach, refactorings,  main_branch_name, refactoring_id, refactoring_type,
                        initial_commit_version, repository_path, project, repo, timestamp_current_attempt, method_name,
                        local_repository_path, original_failed_test, original_test_error, results_dictionary):

    for prompt_approach_item in prompt_approach:

        #checkout on the main branch
        repo.git.checkout(main_branch_name)
        repo.git.reset(initial_commit_version, hard=True)

        prompt_approach_codes = refactorings.get(prompt_approach_item)
        method_codes, classes_code, other_code = prompt_approach_codes['methods'], prompt_approach_codes['classes'], prompt_approach_codes['others']

        if len(method_codes) == 0:
            print("continue")
            continue

        main_method_code = method_codes[0]
        other_methods_code = method_codes[1:]
        other_methods_code = "√".join(other_methods_code)
        classes_code = "√".join(classes_code)
        other_code = "√".join(other_code)

        results_subdict = dict()
        results_subdict['refactoring_id'] = refactoring_id
        results_subdict['refactoring_type'] = refactoring_type
        results_subdict['prompt_approach_item'] = prompt_approach_item

        #Checkout of the “before version” commit (git checkout hash)
        branch_name = refactoring_id + "&" + refactoring_type + "&" + prompt_approach_item + "&" + timestamp_current_attempt
        before_and_after_path = "./results/chat_gpt_4o_mini/run#1/" + project + "/" + branch_name
        before_path =  before_and_after_path + "/" + "before"
        os.makedirs(before_path, exist_ok=True)

        if os.path.exists(repository_path):
            shutil.copy(repository_path, before_path)


        repo.git.checkout('-b', branch_name, initial_commit_version)
        is_refactored = 0 # subprocess.call(['java', '-jar', jar_path, repository_path, method_name,
                          #               main_method_code, other_methods_code, classes_code, other_code])
        print("=================== is_refactored =================== ", is_refactored)

        modifier_result_processing(is_refactored, before_and_after_path, repository_path, results_subdict, repo, branch_name, local_repository_path,
                                   original_failed_test, original_test_error, results_dictionary)



def modifier_caller(repo, main_branch_name, project, local_repository_path,
                    results_dictionary, original_failed_test, original_test_error):

    with open(llm_generated_code_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)

    with open(data_collection_path, 'r') as data_collection_file:
        collected_data = json.load(data_collection_file)

    for refactoring_id, refactorings in generated_code_data.items():

        for item in collected_data:

            if item.get("\ufeffID") == refactoring_id:
                item_project = item.get("Project").split("/")[-1]

                if item_project != project:
                    continue
                
                refactoring_type = refactorings.get("RefactMethod").replace(" ", "_")
            
                timestamp_current_attempt = str(datetime.datetime.now().timestamp())
                relative_path = item.get('path_before').replace("\\", "/")
                repository_path = local_repository_path + relative_path

                end_index = item.get("name").index("(")
                method_signature = item.get('name')[0:end_index].split(" ")
                method_name = method_signature[-1]

                initial_commit_version = item.get("commitID_before")

                modifier_processing(prompt_approach, refactorings, main_branch_name, refactoring_id,
                                    refactoring_type, initial_commit_version, repository_path, project, repo,
                                    timestamp_current_attempt, method_name, local_repository_path, original_failed_test,
                                    original_test_error, results_dictionary)

if __name__ == '__main__':
    pass
