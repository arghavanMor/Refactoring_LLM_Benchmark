import git
from git import Repo
import os
import subprocess
import json
import datetime


ZERO_SHOT_CODE= "ZeroShotCode"
INSTRUC_CODE= "InstrucCode"
FEW_SHOT_CODE= "FewShotCode"

ANTLR4_REPOSITORY = "https://github.com/antlr/antlr4"
ANTLR4_LOCAL_REPOSITORY = "/Users/jeancarlorspaul/IdeaProjects/antlr4/" # to change regarding to your own local repository
ANTLR4_BEFORE_COMMIT_VERSION = "ad9bac95199736c270940c4037b7ee7174bacca6"
INITIAL_BRANCH_NAME = "Initial"
JAR_FILE_PATH = "./Refactoring_AST.main.jar" #to change 

if os.path.exists(ANTLR4_LOCAL_REPOSITORY):
    repo = Repo(ANTLR4_LOCAL_REPOSITORY)
    repo.git.checkout(ANTLR4_BEFORE_COMMIT_VERSION)
else:
    repo = Repo.clone_from(ANTLR4_REPOSITORY, ANTLR4_LOCAL_REPOSITORY)
    repo.git.checkout(ANTLR4_BEFORE_COMMIT_VERSION)

def refact_versioning_init():
    # print(" ============= INITIAL COMMIT ==============")
    if not INITIAL_BRANCH_NAME in repo.branches:
       initial_branch = repo.create_head(INITIAL_BRANCH_NAME)
       repo.head.reference = initial_branch
       initial_branch.checkout()
       repo.index.commit(INITIAL_BRANCH_NAME)
    else:
       initial_branch = repo.heads[INITIAL_BRANCH_NAME]
       repo.head.reference = initial_branch

    return repo.active_branch.name, repo.head.commit.hexsha

def modifier_caller():
    commit_references = []
    prompt_approach = [ZERO_SHOT_CODE, INSTRUC_CODE, FEW_SHOT_CODE]
    with open('../llm_generated_code.json', 'r') as file:
       generated_code_data = json.load(file)

    with open('../examples.json', 'r') as file:
        collected_data = json.load(file)

    for refactorings in generated_code_data.values():
        refactoring_id = refactorings.get("ID")
        for item in collected_data:
            if item.get("\ufeffID") == refactoring_id:
                case_id = refactoring_id
                #project =  item.get('Project') #refactorings.get("RefactMethod")
                refactoring_type = item.get('Type')
                number_of_current_attempt = str(datetime.datetime.now().timestamp())
                relative_path = item.get('path_before').replace("\\", "/")
                repository_path = ANTLR4_LOCAL_REPOSITORY + relative_path

                endIndex = item.get("name").index("(")
                method_signature = item.get('name')[0:endIndex].split(" ")
                method_name = method_signature[-1]

                for prompt_approach_item in prompt_approach:
                    prompt_approach_code = refactorings.get(prompt_approach_item)

                    refact_versioning_init()
                    branch_name = case_id + refactoring_type + prompt_approach_item + number_of_current_attempt
                    new_refactoring_branch = repo.create_head(branch_name)
                    repo.head.reference = new_refactoring_branch
                    new_refactoring_branch.checkout()
                    repo.index.commit(branch_name)

                    subprocess.run(['java', '-jar', JAR_FILE_PATH, repository_path, method_name, prompt_approach_code])

                    repo.git.add(all=True)

                    #repo.index.commit(branch_name)
                    commit_reference = repo.active_branch.name, repo.head.commit.hexsha
                    commit_references.append(commit_reference)

                    with open('commit_references.txt', 'a') as file:
                        file.write(str(commit_reference) + "\n")



if __name__ == "__main__":
    refact_versioning_init()
    modifier_caller()
