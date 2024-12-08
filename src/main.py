import git
from git import Repo
import os
import subprocess
import json
import datetime

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


def modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository, commit_references_path, results_path, results_dictionary, original_failed_test, original_test_error):

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
                    print("="*200)
                    prompt_approach_code = refactorings.get(prompt_approach_item)

                    repo.git.checkout(main_branch_name)

                    #Checkout of the “before version” commit (git checkout hash)
                    branch_name = case_id + refactoring_type + prompt_approach_item + number_of_current_attempt
                    repo.git.checkout('-b', branch_name, initial_commit_version)
                    result = subprocess.call(['java', '-jar', jar_path, repository_path, method_name, prompt_approach_code])

                    if result == 0:
                        repo.git.add(all=True)
                        repo.index.commit(branch_name)
                        commit_hash = repo.head.commit.hexsha
                        #commit_references.append(commit_reference)

                        compilation_return_code = compile_call(repo, local_repository, repo.head.commit.hexsha)
                        failed_test, test_error = test(repo, local_repository, branch_name, repo.head.commit.hexsha)

                        refactoring_quantity += 1
                        if not compilation_return_code:
                            compilation_success_quantity += 1

                        print(refactoring_quantity, " refactoring(s), ", compilation_success_quantity, " successfully compilation(s), ", (compilation_success_quantity/refactoring_quantity), "%")
                        unreproduced_failed_test = ""
                        new_failed_test = ""
                        unreproduced_test_error = ""
                        new_test_error = ""
                        test_error_to_failed_test = ""
                        failed_test_to_test_error = ""

                        results_subdict = dict()
                        results_subdict['commit_hash'] = commit_hash
                        results_subdict['refactoring_id'] = refactoring_id
                        results_subdict['refactoring_type'] = refactoring_type
                        results_subdict['prompt_approach_item'] = prompt_approach_item

                        if failed_test :
                            unreproduced_failed_test = original_failed_test - failed_test
                            new_failed_test = failed_test - original_failed_test


                            results_subdict['failed_test'] = list(failed_test)
                            results_subdict['failed_test_length'] = len(failed_test)

                            results_subdict['unreproduced_failed_test'] = list(unreproduced_failed_test)
                            results_subdict['unreproduced_failed_test_length'] = len(unreproduced_failed_test)

                            results_subdict['new_failed_test'] =  list(new_failed_test)
                            results_subdict['new_failed_test_length'] =  len(new_failed_test)

                            if test_error :
                                test_error_to_failed_test = failed_test.intersection(original_test_error)
                                results_subdict['test_error_to_failed_test'] =  list(test_error_to_failed_test)
                                results_subdict['test_error_to_failed_test_length'] =  len(test_error_to_failed_test)
                            else:
                                results_subdict['test_error_to_failed_test'] = []
                                results_subdict['test_error_to_failed_test_length'] = 0

                        else:
                            results_subdict['failed_test'] = []
                            results_subdict['failed_test_length'] = 0

                            results_subdict['unreproduced_failed_test'] = []
                            results_subdict['unreproduced_failed_test_length'] = 0

                            results_subdict['new_failed_test'] =  []
                            results_subdict['new_failed_test_length'] =  0


                        if test_error :
                            unreproduced_test_error = original_test_error - test_error
                            new_test_error = test_error - original_test_error

                            results_subdict['test_error'] = list(test_error)
                            results_subdict['test_error_length'] = len(test_error)

                            results_subdict['unreproduced_test_error'] = list(unreproduced_test_error)
                            results_subdict['unreproduced_test_error_length'] = len(unreproduced_test_error)

                            results_subdict['new_test_error'] = list(new_test_error)
                            results_subdict['new_test_error_length'] = len(new_test_error)

                            if failed_test :
                                failed_test_to_test_error = test_error.intersection(original_failed_test)
                                results_subdict['failed_test_to_test_error'] =  list(failed_test_to_test_error)
                                results_subdict['failed_test_to_test_error_length'] =  len(failed_test_to_test_error)
                            else:
                                results_subdict['failed_test_to_test_error'] = []
                                results_subdict['failed_test_to_test_error_length'] = 0
                        else:
                            results_subdict['test_error'] = []
                            results_subdict['test_error_length'] = 0

                            results_subdict['unreproduced_test_error'] = []
                            results_subdict['unreproduced_test_error_length'] = 0

                            results_subdict['new_test_error'] = []
                            results_subdict['new_test_error_length'] = 0

                        results_dictionary[branch_name] = results_subdict

                    else:
                        print("Refactoring failed")

                    #checkout on the main branch
                    repo.git.checkout(main_branch_name)
                    repo.git.reset(initial_commit_version, hard=True)

def compile_call(repo, local_repository_path, commit_version):
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'clean'], env=env, capture_output=True, text=True)
    compile_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'compile'], env=env, capture_output=True, text=True)
    return compile_result.returncode


def test(repo, local_repository_path, branch_name, commit_version):
    failed_test = None
    test_error = None
    compilation_return_code = compile_call(repo, local_repository_path, commit_version)

    if not compilation_return_code:
        print("Oh yes! The test is working!")
        test_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'test'], env=env, capture_output=True, text=True)
        failed_test, test_error = result_str_processing(test_result.stdout)
    else:
        print("unfortunately, the test doesn't work!")

    return failed_test, test_error

def result_str_processing(test_result_stdout):
    failed_test = None
    test_error = None
    test_result_summary_start = test_result_stdout.find("Results :")
    test_result_summary_end = test_result_stdout.rfind("Skipped")+12
    test_result_summary = test_result_stdout[test_result_summary_start:test_result_summary_end]

    failed_test_temp = test_result_summary.split("Failed tests:")[1]
    failed_test = failed_test_temp.split("Tests in error:")[0]
    failed_test_list = [item.strip().split(")")[0]+")" for item in failed_test.split("\n") if 'test' in item]
    failed_test = set(failed_test_list)
    print("*"*100)
    test_error_temp = test_result_summary.split("Tests in error:")[1]
    test_error = test_error_temp.split("Tests run:")[0]
    test_error = set([item.strip().split(")")[0]+")" for item in test_error.split("\n") if 'test' in item])
    print(test_error)
    print("*"*200)
    return failed_test, test_error





def main():
    for project, project_info in target_projects.items():
        remote_repository_url = project_info['remote_repository_url']
        local_repository_path = project_info['local_repository_path']
        initial_commit_version = project_info['initial_commit_version']
        commit_references_path = project_info['commit_references_path']
        results_path =  project_info['results_path']
        results_dictionary = dict()


        if os.path.exists(local_repository_path):
            repo = Repo(local_repository_path)
        else:
            repo = Repo.clone_from(remote_repository_url, local_repository_path)

        main_branch_name = repo.git.symbolic_ref(head_path).split('/')[-1]
        repo.git.checkout(main_branch_name)
        repo.git.reset(initial_commit_version, hard=True)

        original_failed_test = None
        original_test_error = None
        if project == 'antlr4':
            compile_call(repo, local_repository_path, initial_commit_version)
            original_failed_test, original_test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            if( original_failed_test and  original_test_error):
                results_dictionary['original_failed_test'] = list(original_failed_test)
                results_dictionary['original_test_error'] =  list(original_test_error)

        modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository_path, commit_references_path, results_path, results_dictionary, original_failed_test, original_test_error)

        # Serializing json
        json_object = json.dumps(results_dictionary, indent=4)

        with open(results_path, 'w') as results_file:
            results_file.write(json_object)
if __name__ == "__main__":
    main()
