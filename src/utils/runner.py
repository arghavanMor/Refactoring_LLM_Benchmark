import subprocess
import os
from src.projects.antlr4 import antlr4_result_str_processing
from src.projects.junit4 import junit4_result_str_processing
import config

env = config.env
results_directory = os.getcwd() + "/results/"

stdout_directory = results_directory

def compile_call(repo, local_repository_path, branch_name, commit_version, llm_id):
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    subprocess.run(['mvn', '-f', local_repository_path + 'pom.xml', 'clean'], env=env, capture_output=True, text=True)
    compilation_result = subprocess.run(['mvn', '-f', local_repository_path + 'pom.xml', 'compile'], env=env, capture_output=True, text=True)

    if 'antlr4' in local_repository_path:
        compilation_stdout_file_path_dir = results_directory + llm_id + "/antlr4/compilation/stdout/"
        os.makedirs(compilation_stdout_file_path_dir, exist_ok=True)
        compilation_stdout_file_path =  compilation_stdout_file_path_dir + branch_name + "_" + commit_version + ".txt"
        compilation_result_stdout = compilation_result.stdout
        with open(compilation_stdout_file_path, 'w') as file:
            file.write(compilation_result_stdout)

        compilation_stderr_file_path_dir = results_directory + llm_id + "/antlr4/compilation/stderr/"
        os.makedirs(compilation_stderr_file_path_dir, exist_ok=True)
        compilation_stderr_file_path =  compilation_stderr_file_path_dir + branch_name + "_" + commit_version + ".txt"
        compilation_result_stderr = compilation_result.stderr
        with open(compilation_stderr_file_path, 'w') as file:
            file.write(compilation_result_stderr)

    elif 'junit4' in local_repository_path:
        compilation_stdout_file_path_dir = results_directory + llm_id + "/junit4/compilation/stdout/"
        os.makedirs(compilation_stdout_file_path_dir, exist_ok=True)
        compilation_stdout_file_path =  compilation_stdout_file_path_dir + branch_name + "_" + commit_version + ".txt"
        compilation_result_stdout = compilation_result.stdout
        with open(compilation_stdout_file_path, 'w') as file:
            file.write(compilation_result_stdout)

        compilation_stderr_file_path_dir = results_directory + llm_id + "/junit4/compilation/stderr/"
        os.makedirs(compilation_stderr_file_path_dir, exist_ok=True)
        compilation_stderr_file_path =  compilation_stderr_file_path_dir + branch_name + "_" + commit_version + ".txt"
        compilation_result_stderr = compilation_result.stderr
        with open(compilation_stderr_file_path, 'w') as file:
            file.write(compilation_result_stderr)
    return compilation_result.returncode

def test(repo, local_repository_path, branch_name, commit_version, llm_id):
    test_result = subprocess.run(['mvn', '-f', local_repository_path + 'pom.xml', 'test'], env=env, capture_output=True, text=True)

    if 'antlr4' in local_repository_path:
        test_stdout_file_path_dir = results_directory + llm_id + "/antlr4/test/stdout/"
        os.makedirs(test_stdout_file_path_dir, exist_ok=True)
        test_stdout_file_path =  test_stdout_file_path_dir + branch_name + "_" + commit_version + ".txt"
        test_result_stdout = test_result.stdout
        with open(test_stdout_file_path, 'w') as file:
            file.write(test_result_stdout)
        failed_test, test_error = antlr4_result_str_processing(test_result_stdout)

        failed_test_error_path_dir = results_directory + llm_id + "/antlr4/test/failed_test_error/"
        os.makedirs(failed_test_error_path_dir, exist_ok=True)
        failed_test_error_path =  failed_test_error_path_dir + branch_name + "_" + commit_version + ".txt"
        formatted_failed_test = "\n".join(failed_test)
        formatted_test_error = "\n".join(test_error)
        failed_test_error_content = ("Failed test: " + "\n" + formatted_failed_test + "\n\n" +  "Test error: "
                                     + "\n" + formatted_test_error)
        with open(failed_test_error_path, 'w') as file:
            file.write(failed_test_error_content)

        return failed_test, test_error
    elif 'junit4' in local_repository_path:
        test_stdout_file_path_dir = results_directory + llm_id + "/junit4/test/stdout/"
        os.makedirs(test_stdout_file_path_dir, exist_ok=True)
        test_stdout_file_path =  test_stdout_file_path_dir + branch_name + "_" + commit_version + ".txt"
        with open(test_stdout_file_path, 'w') as file:
           file.write(test_result.stdout)
        total_test, total_failed_test, total_error_test = junit4_result_str_processing(test_result.stdout)
        return total_test, total_failed_test, total_error_test


if __name__ == '__main__':
    pass