import json
import os

env = os.environ.copy()

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'config.json')

with open(file_path, 'r') as file:
    config_data = json.load(file)

prompt_approach = config_data["prompt_approach"]
target_projects = config_data["target_projects"]
initial_branch_name = config_data["initial_branch_name"]
jar_path = config_data["jar_path"]
llm_generated_code_path = config_data["llm_generated_code_path"]
before_and_after_path_prefix = config_data["before_and_after_path_prefix"]
data_collection_path = config_data["data_collection_path"]
antlr4_project = config_data["target_projects"]["antlr4"]
junit4_project = config_data["target_projects"]["junit4"]
head_path = config_data["head_path"]
args_dict = config_data["args_dict"]

# environment setting
jdk_path = config_data["jdk_path"]
mvn_path = config_data["mvn_path"]
env["JAVA_HOME"] = jdk_path
env["PATH"] = f"{jdk_path}/bin:" + env["PATH"]
env["PATH"] = f"{mvn_path}/bin:" + env["PATH"]

if __name__ == "__main__":
    pass

#ed47b7f487bafa48cff47f051af81a004cd36049
#L7126&INTRODUCE_ASSERTION&ContextCode
#Exception in thread "main" java.io.FileNotFoundException: /Users/jeancarlorspaul/IdeaProjects/junit4/src/test/java/org/junit/tests/experimental/categories/CategoryTest.java (No such file or directory)

#9c02e68e611524f9c4cc60b6cbc2970e196f30bc
