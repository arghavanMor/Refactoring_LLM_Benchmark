import git
from git import Repo
import os
import subprocess
import json
import datetime
import shutil
from utils.config import target_projects, initial_branch_name, jar_path, head_path, args_dict, env
from utils.runner import compile_call, test
from utils.refactoring_applier import modifier_caller

def main():
    for project, project_info in target_projects.items():

        remote_repository_url = project_info['remote_repository_url']
        local_repository_path = project_info['local_repository_path']

        # Must make it more dynamic
        initial_commit_version = project_info['initial_commit_version']
        results_path =  project_info['results_path']
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
            if(original_failed_test and  original_test_error):
                results_dictionary['original_failed_test'] = list(original_failed_test)
                results_dictionary['original_test_error'] =  list(original_test_error)
        elif 'junit4' in local_repository_path:
            original_total_test, original_total_failed_test, original_total_test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            results_dictionary['original_total_test'] = original_total_test
            results_dictionary['original_total_failed_test'] =  original_total_failed_test
            results_dictionary['original_total_test_error'] = original_total_test_error

        modifier_caller(repo, main_branch_name, project, local_repository_path,
                        results_dictionary, original_failed_test, original_test_error)
        """
        refactoring_status = [results_dictionary[item]['refactored'] for item in results_dictionary.keys() if isinstance(results_dictionary[item], dict)]
        results_dictionary['refactoring_status_list'] = sum(refactoring_status)
        results_dictionary['refactoring_status_list_length'] = len(refactoring_status)
        if int(results_dictionary['refactoring_status_list_length']) != 0:
            results_dictionary['refactoring_ratio'] = int(results_dictionary['refactoring_status_list'])/int(results_dictionary['refactoring_status_list_length'])

        compilation_status = [results_dictionary[item]['compiled'] for item in results_dictionary.keys() if (isinstance(results_dictionary[item], dict) and 'compiled' in results_dictionary[item].keys())]
        results_dictionary['compilation_status_list'] = sum(compilation_status)
        results_dictionary['compilation_status_list_length'] = len(compilation_status)
        if int(results_dictionary['compilation_status_list_length']) != 0:
            results_dictionary['compilation_ratio'] = int(results_dictionary['compilation_status_list'])/int(results_dictionary['compilation_status_list_length'])


        # Serializing json
        json_object = json.dumps(results_dictionary, indent=4)

        with open(results_path, 'w') as results_file:
            results_file.write(json_object)

        """


if __name__ == "__main__":
    main()
    #, "ContextCode", "RulesCode"]
    #"L2093" "L19910"
