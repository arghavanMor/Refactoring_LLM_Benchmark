import git
from git import Repo
import os
import subprocess
import json
import datetime
import shutil
from config import target_projects, initial_branch_name, jar_path, head_path, args_dict, env
from runner import compile_call, test
from refactoring_applier import modifier_caller

def main():

    remote_repository_url_key = "remote_repository_url"
    local_repository_path_key = "local_repository_path"
    initial_commit_version_key = "initial_commit_version"
    results_path_key = "results_path"
    original_failed_test_key = "original_failed_test"
    original_test_error_key = "original_test_error"
    original_total_test_key = "original_total_test"
    original_total_failed_test_key = "original_total_failed_test"
    original_total_test_error_key = "original_total_test_error"
    refactored_key = "refactored"
    refactoring_status_list_key = "refactoring_status_list"
    refactoring_status_list_length_key = "refactoring_status_list_length"
    refactoring_ratio_key = "refactoring_ratio"
    compiled_key = "compiled"
    compilation_status_list_key = "compilation_status_list"
    compilation_status_list_length_key = "compilation_status_list_length"
    compilation_ratio_key = "compilation_ratio"


    for project, project_info in target_projects.items():

        remote_repository_url = project_info[remote_repository_url_key]
        local_repository_path = project_info[local_repository_path_key]

        # Must make it more dynamic
        initial_commit_version = project_info[initial_commit_version_key]
        results_path =  project_info[results_path_key]
        results_dictionary = dict()

        print("="*80, project, "="*80)

        if os.path.exists(local_repository_path):
            repo = Repo(local_repository_path)
        else:
            repo = Repo.clone_from(remote_repository_url, local_repository_path)

        main_branch_name = repo.git.symbolic_ref(head_path).split('/')[-1]

        repo.git.checkout(main_branch_name)
        repo.git.reset(initial_commit_version, hard=True)

        original_failed_test = None
        original_test_error = None

        compile_call(repo, local_repository_path, initial_commit_version)

        if 'antlr4' in local_repository_path:
            original_failed_test, original_test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            if(original_failed_test and original_test_error):
                results_dictionary[original_failed_test_key] = list(original_failed_test)
                results_dictionary[original_test_error_key] =  list(original_test_error)
        elif 'junit4' in local_repository_path:
            original_total_test, original_total_failed_test, original_total_test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            results_dictionary[original_total_test_key] = original_total_test
            results_dictionary[original_total_failed_test_key] =  original_total_failed_test
            results_dictionary[original_total_test_error_key] = original_total_test_error

        modifier_caller(repo, main_branch_name, project, local_repository_path,
                        results_dictionary, original_failed_test, original_test_error)


        refactoring_status = [results_dictionary[item][refactored_key] for item in results_dictionary.keys() if isinstance(results_dictionary[item], dict)]
        results_dictionary[refactoring_status_list_key] = sum(refactoring_status)
        results_dictionary[refactoring_status_list_length_key] = len(refactoring_status)

        if int(results_dictionary[refactoring_status_list_length_key]) != 0:
            results_dictionary[refactoring_ratio_key] = int(results_dictionary[refactoring_status_list_key])/int(results_dictionary[refactoring_status_list_length_key])

        compilation_status = [results_dictionary[item][compiled_key] for item in results_dictionary.keys() if (isinstance(results_dictionary[item], dict) and compiled_key in results_dictionary[item].keys())]
        results_dictionary[compilation_status_list_key] = sum(compilation_status)
        results_dictionary[compilation_status_list_length_key] = len(compilation_status)
        if int(results_dictionary[compilation_status_list_length_key]) != 0:
            results_dictionary[compilation_ratio_key] = int(results_dictionary[compilation_status_list_key])/int(results_dictionary[compilation_status_list_length_key])


        print("="*80, "\n", results_dictionary, "\n", "="*80)
        # Serializing json
        json_object = json.dumps(results_dictionary, indent=4)

        with open(results_path, 'w') as results_file:
            results_file.write(json_object)

if __name__ == "__main__":
    pass

