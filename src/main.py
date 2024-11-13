import git
from git import Repo
import os
import subprocess
import json
import datetime
import re

env = os.environ.copy()

with open('../input.json', 'r') as file:
    config_data = json.load(file)

prompt_approach = config_data["prompt_approach"]
target_projects = config_data["target_projects"]
initial_branch_name = config_data["initial_branch_name"]
jar_path = config_data["jar_path"]
llm_generated_code_path = config_data["llm_generated_code_path"]
data_collection_path = config_data["data_collection_path"]
head_path = 'refs/remotes/origin/HEAD'

jdk_path = '/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home'
mvn_path = '/usr/local/opt/maven@3.6'

# environment setting
env["JAVA_HOME"] = jdk_path
env["PATH"] = f"{jdk_path}/bin:" + env["PATH"]
env["PATH"] = f"{mvn_path}/bin:" + env["PATH"]


def modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository, commit_references_path):
    commit_references = []

    with open(llm_generated_code_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)

    with open(data_collection_path, 'r') as data_collection_file:
        collected_data = json.load(data_collection_file)

    refactoring_quantity = 0
    compilation_success_quantity = 0

    for refactoring_id, refactorings in generated_code_data.items():
        for item in collected_data:
            if item.get("\ufeffID") == refactoring_id:
                case_id = refactoring_id
                item_project = item.get("Project").split("/")[-1]

                if item_project != project:
                    continue

                refactoring_type = item.get("Type")
                number_of_current_attempt = str(datetime.datetime.now().timestamp())
                relative_path = item.get('path_before').replace("\\", "/")
                repository_path = local_repository + relative_path

                end_index = item.get("name").index("(")
                method_signature = item.get('name')[0:end_index].split(" ")
                method_name = method_signature[-1]

                for prompt_approach_item in prompt_approach:
                    prompt_approach_code = refactorings.get(prompt_approach_item)

                    repo.git.checkout(main_branch_name)

                    #Checkout of the “before version” commit (git checkout hash)
                    branch_name = case_id + refactoring_type + prompt_approach_item + number_of_current_attempt
                    repo.git.checkout('-b', branch_name, initial_commit_version)
                    #repo.git.checkout(branch_name)
                    result = subprocess.call(['java', '-jar', jar_path, repository_path, method_name, prompt_approach_code])

                    if result == 0:
                        repo.git.add(all=True)
                        repo.index.commit(branch_name)
                        commit_reference = repo.active_branch.name, repo.head.commit.hexsha
                        commit_references.append(commit_reference)

                        compilation_return_code = compile(repo, local_repository, branch_name, repo.head.commit.hexsha)
                        test(repo, local_repository, branch_name, repo.head.commit.hexsha)

                        refactoring_quantity += 1
                        if not compilation_return_code:
                            compilation_success_quantity += 1

                        print(refactoring_quantity, " refactoring(s), ", compilation_success_quantity, " successfully compilation(s), ", (compilation_success_quantity/refactoring_quantity), "%")
                        with open(commit_references_path, 'a') as commit_references_file:
                            commit_references_file.write(str(commit_reference) + "\n")
                    else:
                        print("Refactoring failed")

                    #checkout on the main branch
                    repo.git.checkout(main_branch_name)
                    repo.git.reset(initial_commit_version, hard=True)


def compile(repo, local_repository_path, branch_name, commit_version):
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    clean_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'clean'], env=env, capture_output=True, text=True)
    compile_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'compile'], env=env, capture_output=True, text=True)
    return compile_result.returncode


def test(repo, local_repository_path, branch_name, commit_version):
    failed_test = None
    test_error = None
    compilation_return_code = compile(repo, local_repository_path, branch_name, commit_version)
    if not compilation_return_code:
        print("Oh yes! The test is working!")
        test_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'test'], env=env, capture_output=True, text=True)

        test_result_stdout = test_result.stdout
        test_result_summary_start = test_result_stdout.find("Results :")
        test_result_summary_end = test_result_stdout.rfind("Skipped")+12
        test_result_summary = test_result_stdout[test_result_summary_start:test_result_summary_end]

        print("*"*200)
        print("*"*200)
        #print(test_result_stdout)
        print("*"*100)
        print(test_result_summary)
        print("*"*100)
        failed_test_temp = test_result_summary.split("Failed tests:")[1]
        failed_test = failed_test_temp.split("Tests in error:")[0]
        failed_test = set([item.strip() for item in failed_test.split("\n") if 'test' in item])
        #print(failed_test)
        print("*"*100)
        test_error_temp = test_result_summary.split("Tests in error:")[1]
        test_error = test_error_temp.split("Tests run:")[0]
        test_error = set([item.strip() for item in test_error.split("\n") if 'test' in item])
        #print(test_error)
        print("*"*200)
        print("*"*200)
    else:
        print("unfortunately, the test doesn't work!")

    return failed_test, test_error

def main():
    for project, project_info in target_projects.items():
        remote_repository_url = project_info['remote_repository_url']
        local_repository_path = project_info['local_repository_path']
        initial_commit_version = project_info['initial_commit_version']
        commit_references_path = project_info['commit_references_path']

        if os.path.exists(local_repository_path):
            repo = Repo(local_repository_path)
        else:
            repo = Repo.clone_from(remote_repository_url, local_repository_path)

        main_branch_name = repo.git.symbolic_ref(head_path).split('/')[-1]
        repo.git.checkout(main_branch_name)
        repo.git.reset(initial_commit_version, hard=True)

        with open(commit_references_path, 'a') as commit_references_file:
            initial_branch_commit = (main_branch_name, initial_commit_version)
            commit_references_file.write(str(initial_branch_commit) + "\n")

        if project == 'antlr4':
            compile(repo, local_repository_path, main_branch_name, initial_commit_version)
            failed_test, test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            print(failed_test)
            print(test_error)

        modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository_path, commit_references_path)

if __name__ == "__main__":
    main()

