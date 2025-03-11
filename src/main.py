import git
from git import Repo
import os
import subprocess
import json
import datetime
import shutil

env = os.environ.copy()


with open('input.json', 'r') as file:
    config_data = json.load(file)

prompt_approach = config_data["prompt_approach"]
target_projects = config_data["target_projects"]
initial_branch_name = config_data["initial_branch_name"]
jar_path = config_data["jar_path"]
llm_generated_code_path = config_data["llm_generated_code_path"]
data_collection_path = config_data["data_collection_path"]
head_path = 'refs/remotes/origin/HEAD'
args_dict = {"methods": "", "classes": "", "others": ""}

jdk_path = '/Library/Java/JavaVirtualMachines/jdk-11.jdk/Contents/Home'
mvn_path = '/usr/local/opt/maven@3.6'

# environment setting
env["JAVA_HOME"] = jdk_path
env["PATH"] = f"{jdk_path}/bin:" + env["PATH"]
env["PATH"] = f"{mvn_path}/bin:" + env["PATH"]


def antlr4_result_str_processing(test_result_stdout):
    failed_test = None
    test_error = None
    test_result_summary_start = test_result_stdout.find("Results :")
    test_result_summary_end = test_result_stdout.rfind("Skipped")+12
    test_result_summary = test_result_stdout[test_result_summary_start:test_result_summary_end]

    if test_result_summary == '':
        failed_test, test_error = set(), set()
        return failed_test, test_error

    failed_test_temp = test_result_summary.split("Failed tests:")[1]
    failed_test = failed_test_temp.split("Tests in error:")[0]
    failed_test_list = [item.strip().split(")")[0]+")" for item in failed_test.split("\n") if 'test' in item]
    failed_test = set(failed_test_list)

    test_error_temp = test_result_summary.split("Tests in error:")[1]
    test_error = test_error_temp.split("Tests run:")[0]
    test_error = set([item.strip().split(")")[0]+")" for item in test_error.split("\n") if 'test' in item])
    return failed_test, test_error

def junit4_result_str_processing(test_result_stdout):
    test_result_summary_start = test_result_stdout.find("Results :\n")
    #test_result_summary_end = test_result_summary_start[test_result_summary_start]
    test_result_summary = test_result_stdout[test_result_summary_start:]

    total_test = test_result_summary[test_result_summary.find('run: ') + 5:test_result_summary.find(', Failures')]
    failed_test = test_result_summary[test_result_summary.find('Failures: ') + 10:test_result_summary.find(', Errors')]
    error_test = test_result_summary[test_result_summary.find('Errors: ') + 8:test_result_summary.find(', Skipped')]
    print(test_result_summary)
    total_test = int(total_test)
    total_failed_test = int(failed_test)
    total_error_test = int(error_test)
    return total_test, total_failed_test, total_error_test

def compile_call(repo, local_repository_path, commit_version):
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'clean'], env=env, capture_output=True, text=True)
    compile_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'compile'], env=env, capture_output=True, text=True)
    return compile_result.returncode


def test(repo, local_repository_path, branch_name, commit_version):
    test_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'test'], env=env, capture_output=True, text=True)
    if 'antlr4' in local_repository_path:
        failed_test, test_error = antlr4_result_str_processing(test_result.stdout)
        return failed_test, test_error
    else:
        total_test, total_failed_test, total_error_test = junit4_result_str_processing(test_result.stdout)
        return total_test, total_failed_test, total_error_test



def modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository, results_dictionary, original_failed_test, original_test_error):

    with open(llm_generated_code_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)

    with open(data_collection_path, 'r') as data_collection_file:
        collected_data = json.load(data_collection_file)

    for refactoring_id, refactorings in generated_code_data.items():
        counter = 0
        for item in collected_data:

            if item.get("\ufeffID") == refactoring_id:
                case_id = refactoring_id
                item_project = item.get("Project").split("/")[-1]

                if item_project != project:
                    continue

                refactoring_type = item.get("Fowler_type").replace(" ", "_")
                number_of_current_attempt = str(datetime.datetime.now().timestamp())
                relative_path = item.get('path_before').replace("\\", "/")
                repository_path = local_repository + relative_path

                end_index = item.get("name").index("(")
                method_signature = item.get('name')[0:end_index].split(" ")
                method_name = method_signature[-1]

                for prompt_approach_item in prompt_approach:
                    prompt_approach_codes = refactorings.get(prompt_approach_item)
                    method_codes, classes_code, other_code = prompt_approach_codes['methods'], prompt_approach_codes['classes'], prompt_approach_codes['others']

                    if len(method_codes) == 0:
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

                    repo.git.checkout(main_branch_name)
                    #Checkout of the “before version” commit (git checkout hash)
                    branch_name = case_id + "&" + refactoring_type + "&" + prompt_approach_item + "&" + number_of_current_attempt
                    before_and_after_path = "./results/deep_seek/run#2/" + project + "/" + branch_name
                    before_path =  before_and_after_path + "/" + "before"
                    os.makedirs(before_path, exist_ok=True)

                    if os.path.exists(repository_path):
                        shutil.copy(repository_path, before_path)


                    repo.git.checkout('-b', branch_name, initial_commit_version)
                    is_refactored = subprocess.call(['java', '-jar', jar_path, repository_path, method_name,
                                                         main_method_code, other_methods_code, classes_code, other_code])
                    print("=================== is_refactored =================== ", is_refactored)


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

                        compilation_return_code = compile_call(repo, local_repository, repo.head.commit.hexsha)
                        if not compilation_return_code:
                            results_subdict['compiled'] = 1
                            if 'antlr4' in local_repository:
                                failed_test, test_error = test(repo, local_repository, branch_name, repo.head.commit.hexsha)
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
                                total_test, total_failed_test, total_error_test = test(repo, local_repository, branch_name, repo.head.commit.hexsha)
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

                    #checkout on the main branch
                    repo.git.checkout(main_branch_name)
                    repo.git.reset(initial_commit_version, hard=True)





def main():
    for project, project_info in target_projects.items():
        remote_repository_url = project_info['remote_repository_url']
        local_repository_path = project_info['local_repository_path']
        initial_commit_version = project_info['initial_commit_version']
        results_path =  project_info['results_path']
        results_dictionary = dict()


        print(project)
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
        else:
            original_total_test, original_total_failed_test, original_total_test_error = test(repo, local_repository_path, main_branch_name, initial_commit_version)
            results_dictionary['original_total_test'] = original_total_test
            results_dictionary['original_total_failed_test'] =  original_total_failed_test
            results_dictionary['original_total_test_error'] = original_total_test_error


        modifier_caller(repo, main_branch_name, initial_commit_version, project, local_repository_path, results_dictionary, original_failed_test, original_test_error)


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




if __name__ == "__main__":
    main()
    #, "ContextCode", "RulesCode"]
    #"L2093" "L19910"
