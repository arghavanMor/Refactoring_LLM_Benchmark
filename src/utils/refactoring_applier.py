import git
from git import Repo
import os
import subprocess
import json
import datetime
import shutil
import config
from runner import compile_call, test
from config import jar_path

llm_generated_code_path = config.llm_generated_code_path
data_collection_path = config.data_collection_path
prompt_approach = config.prompt_approach
results_directory = os.getcwd() + "/results/"
initial_commit_version_key = "initial_commit_version"


def modifier_result_processing(is_refactored, before_and_after_path, repository_path, results_subdict, repo,
                               branch_name, local_repository_path, original_failed_test, original_test_error,
                               results_dictionary, llm_id, which_run):

    after = "after"
    refactored_key = "refactored"
    compiled_key = "compiled"
    commit_hash_key = "commit_hash"
    failed_test_key = "failed_test"
    unreproduced_failed_test_key = "unreproduced_failed_test"
    new_failed_test_key = "new_failed_test"
    test_error_to_failed_test_key = "test_error_to_failed_test"
    test_error_key = "test_error"
    unreproduced_test_error_key = "unreproduced_test_error"
    new_test_error_key = "new_test_error"
    failed_test_to_test_error_key = "failed_test_to_test_error"
    total_test_key = "total_test"
    total_failed_test_key = "total_failed_test"
    total_error_test_key = "total_error_test"

    if is_refactored == 0:
        after_path = before_and_after_path + "/" + after
        os.makedirs(after_path, exist_ok=True)
        if os.path.exists(repository_path):
            shutil.copy(repository_path, after_path)

        results_subdict[refactored_key] = 1
        repo.git.add(all=True)
        repo.index.commit(branch_name)
        commit_hash = repo.head.commit.hexsha
        results_subdict[commit_hash_key] = commit_hash

        compilation_return_code = compile_call(repo, local_repository_path, branch_name, repo.head.commit.hexsha, llm_id, which_run)
        if not compilation_return_code:
            results_subdict[compiled_key] = 1
            if 'antlr4' in local_repository_path:
                failed_test, test_error = test(repo, local_repository_path, branch_name, repo.head.commit.hexsha, llm_id, which_run)
                if not (failed_test == set()) :
                    unreproduced_failed_test = original_failed_test - failed_test
                    new_failed_test = failed_test - original_failed_test
                    results_subdict[failed_test_key] = list(failed_test)
                    results_subdict[unreproduced_failed_test_key] = list(unreproduced_failed_test)
                    results_subdict[new_failed_test_key] =  list(new_failed_test)
                    if test_error == set() :
                        test_error_to_failed_test = failed_test.intersection(original_test_error)
                        results_subdict[test_error_to_failed_test_key] =  list(test_error_to_failed_test)
                        results_subdict[unreproduced_test_error_key] = list(original_test_error)
                    else:
                        results_subdict[test_error_to_failed_test_key] = []
                else:
                    results_subdict[failed_test_key] = []
                    results_subdict[unreproduced_failed_test_key] = []
                    results_subdict[new_failed_test_key] =  []
                if not test_error == set() :
                    unreproduced_test_error = original_test_error - test_error
                    new_test_error = test_error - original_test_error
                    results_subdict[test_error_key] = list(test_error)
                    results_subdict[unreproduced_test_error_key] = list(unreproduced_test_error)
                    results_subdict[new_test_error_key] = list(new_test_error)
                    if failed_test == set() :
                        failed_test_to_test_error = test_error.intersection(original_failed_test)
                        results_subdict[failed_test_to_test_error_key] =  list(failed_test_to_test_error)
                    else:
                        results_subdict[failed_test_to_test_error_key] = []
                else:
                    results_subdict[test_error_key] = []
                    results_subdict[unreproduced_test_error_key] = list(original_test_error)
                    results_subdict[new_test_error_key] = []
            elif 'junit4' in local_repository_path:
                total_test, total_failed_test, total_error_test = test(repo, local_repository_path, branch_name, repo.head.commit.hexsha, llm_id, which_run)
                results_subdict[total_test_key] = total_test
                results_subdict[total_failed_test_key] = total_failed_test
                results_subdict[total_error_test_key] = total_error_test
        else:
            results_subdict[compiled_key] = 0
    else:
        if os.path.exists(before_and_after_path):
            shutil.rmtree(before_and_after_path)
        results_subdict[refactored_key] = 0
        print("-"*80, " Refactoring failed ", "-"*80)
    results_dictionary[branch_name] = results_subdict



def modifier_processing(prompt_approach, refactorings,  main_branch_name, refactoring_id, refactoring_type,
                        initial_commit_version, repository_path, project, repo, timestamp_current_attempt, method_name,
                        local_repository_path, original_failed_test, original_test_error, results_dictionary, llm_id, which_run):
    methods_key = "methods"
    classes_key = "classes"
    others_key = "others"
    code_seperator = "√"
    refactoring_id_key = "refactoring_id"
    refactoring_type_key = "refactoring_type"
    prompt_approach_item_key = "prompt_approach_item"
    branch_name_separator = "&"
    before_key = "before"

    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'config.json')

    with open(file_path, 'r') as file:
        config_data = json.load(file)

    before_and_after_path_prefix = config_data["before_and_after_path_prefix"]

    for prompt_approach_item in prompt_approach:

        #checkout on the main branch
        repo.git.checkout(main_branch_name)
        repo.git.reset(initial_commit_version, hard=True)

        prompt_approach_codes = refactorings.get(prompt_approach_item)
        method_codes, classes_code, other_code = (prompt_approach_codes[methods_key], prompt_approach_codes[classes_key],
                                                  prompt_approach_codes[others_key])

        if len(method_codes) == 0:
            continue

        main_method_code = method_codes[0]
        other_methods_code = method_codes[1:]
        other_methods_code = code_seperator.join(other_methods_code)
        classes_code = code_seperator.join(classes_code)
        other_code = code_seperator.join(other_code)


        results_subdict = dict()
        results_subdict[refactoring_id_key] = refactoring_id
        results_subdict[refactoring_type_key] = refactoring_type
        results_subdict[prompt_approach_item_key] = prompt_approach_item

        #Checkout of the “before version” commit (git checkout hash)
        branch_name = (refactoring_id + branch_name_separator + refactoring_type + branch_name_separator + prompt_approach_item
                       + branch_name_separator + timestamp_current_attempt)
        before_and_after_path = before_and_after_path_prefix + project + "/" + branch_name
        before_path =  before_and_after_path + "/" + before_key
        os.makedirs(before_path, exist_ok=True)

        if os.path.exists(repository_path):
            shutil.copy(repository_path, before_path)


        repo.git.checkout('-b', branch_name, initial_commit_version)
        result = subprocess.run(['java', '-jar', jar_path, repository_path, method_name,
                                         main_method_code, other_methods_code, classes_code, other_code], capture_output=True, text=True)

        is_refactored = result.returncode
        stderr = result.stderr

        if not is_refactored:
            print("="*80, " Class refactored ", "="*80)
        else:
            print("="*80, " Class not refactored ", "="*80)
            if 'antlr4' in local_repository_path:
                refactoring_parsing_stderr_path_dir = results_directory + llm_id + which_run + "/antlr4/refactoring_parsing/stderr/"
                os.makedirs(refactoring_parsing_stderr_path_dir, exist_ok=True)
                refactoring_parsing_stderr_path =  refactoring_parsing_stderr_path_dir + branch_name + "_" + repo.head.commit.hexsha + ".txt"
                with open(refactoring_parsing_stderr_path, 'w') as file:
                    file.write(stderr)
            elif 'junit4' in local_repository_path:
                refactoring_parsing_stderr_path_dir = results_directory + llm_id + which_run + "/junit4/refactoring_parsing/stderr/"
                os.makedirs(refactoring_parsing_stderr_path_dir, exist_ok=True)
                refactoring_parsing_stderr_path =  refactoring_parsing_stderr_path_dir + branch_name + "_" + repo.head.commit.hexsha + ".txt"
                with open(refactoring_parsing_stderr_path, 'w') as file:
                    file.write(stderr)

        modifier_result_processing(is_refactored, before_and_after_path, repository_path, results_subdict, repo, branch_name,
                                   local_repository_path, original_failed_test, original_test_error, results_dictionary, llm_id, which_run)



def modifier_caller(repo, main_branch_name, project, local_repository_path,
                    results_dictionary, original_failed_test, original_test_error, llm_id, which_run):
    id_key = "\ufeffID"
    project_key = "Project"
    refact_method_key = "RefactMethod"
    path_before_key = "path_before"
    name_key = "name"
    commit_id_before_key = "commitID_before"


    with open(llm_generated_code_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)

    with open(data_collection_path, 'r') as data_collection_file:
        collected_data = json.load(data_collection_file)

    for refactoring_id, refactorings in generated_code_data.items():

        for item in collected_data:

            if item.get(id_key) == refactoring_id:
                item_project = item.get(project_key).split("/")[-1]

                if item_project != project:
                    continue
                
                refactoring_type = refactorings.get(refact_method_key).replace(" ", "_")
            
                timestamp_current_attempt = str(datetime.datetime.now().timestamp())
                relative_path = item.get(path_before_key).replace("\\", "/")
                repository_path = local_repository_path + relative_path

                end_index = item.get(name_key).index("(")
                method_signature = item.get(name_key)[0:end_index].split(" ")
                method_name = method_signature[-1]

                initial_commit_version = item.get(commit_id_before_key)
                modifier_processing(prompt_approach, refactorings, main_branch_name, refactoring_id,
                                    refactoring_type, initial_commit_version, repository_path, project, repo,
                                    timestamp_current_attempt, method_name, local_repository_path, original_failed_test,
                                    original_test_error, results_dictionary, llm_id, which_run)

if __name__ == '__main__':
    pass
