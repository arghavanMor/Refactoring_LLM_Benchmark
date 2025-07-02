import subprocess
import os
from src.projects.antlr4 import antlr4_result_str_processing
from src.projects.junit4 import junit4_result_str_processing
import config

env = config.env
stdout_directory = os.getcwd() + "/projects/stdout/"

def compile_call(repo, local_repository_path, commit_version):
    subprocess.run(['git', '-C', local_repository_path, 'reset', '--hard', commit_version], env=env)
    subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'clean'], env=env, capture_output=True, text=True)
    compile_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'compile'], env=env, capture_output=True, text=True)
    return compile_result.returncode

def test(repo, local_repository_path, branch_name, commit_version):
    test_result = subprocess.run(['mvn', '-f', local_repository_path + '/pom.xml', 'test'], env=env, capture_output=True, text=True)

    if 'antlr4' in local_repository_path:
        stdout_file_path = stdout_directory + "antlr4/" + branch_name + "_" + commit_version + ".txt"
        failed_test, test_error = antlr4_result_str_processing(test_result.stdout)
        with open(stdout_file_path, 'w') as file:
            file.write(test_result.stdout)
        return failed_test, test_error
    elif 'junit4' in local_repository_path:
        stdout_file_path = stdout_directory + "junit4/" + branch_name + "_" + commit_version + ".txt"
        with open(stdout_file_path, 'w') as file:
           file.write(test_result.stdout)
        total_test, total_failed_test, total_error_test = junit4_result_str_processing(test_result.stdout)
        return total_test, total_failed_test, total_error_test


if __name__ == '__main__':
    pass