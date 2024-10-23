import git
from git import Repo
import os
import subprocess
import json
import datetime

from sympy import pretty_print

with open('../input.json', 'r') as file:
    config_data = json.load(file)

prompt_approach = config_data["prompt_approach"]
target_projects = config_data["target_projects"]
initial_branch_name = config_data["initial_branch_name"]
jar_path = config_data["jar_path"]
llm_generated_code_path = config_data["llm_generated_code_path"]
data_collection_path = config_data["data_collection_path"]


def refact_versioning_init(repo):
    if not initial_branch_name in repo.branches:
       initial_branch = repo.create_head(initial_branch_name)
       repo.head.reference = initial_branch
       initial_branch.checkout()
       repo.index.commit(initial_branch_name)
    else:
       initial_branch = repo.heads[initial_branch_name]
       repo.head.reference = initial_branch

    return repo.head.commit.hexsha

def modifier_caller(repo, project, local_repository, commit_references_path):
    initial_commit_hash = refact_versioning_init(repo)
    commit_references = []

    with open(llm_generated_code_path, 'r') as llm_generated_code_file:
       generated_code_data = json.load(llm_generated_code_file)

    with open(data_collection_path, 'r') as data_collection_file:
        collected_data = json.load(data_collection_file)

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

                    initial_branch = repo.heads[initial_branch_name]
                    repo.head.reference = initial_branch

                    branch_name = case_id + refactoring_type + prompt_approach_item + number_of_current_attempt
                    new_refactoring_branch = repo.create_head(branch_name)
                    repo.head.reference = new_refactoring_branch
                    new_refactoring_branch.checkout()
                    repo.index.commit(branch_name)

                    subprocess.run(['java', '-jar', jar_path, repository_path, method_name, prompt_approach_code])

                    #repo.git.add(all=True)

                    repo.index.commit(branch_name)
                    commit_reference = repo.active_branch.name, repo.head.commit.hexsha
                    commit_references.append(commit_reference)


                    with open(commit_references_path, 'a') as commit_references_file:
                        commit_references_file.write(str(commit_reference) + "\n")

    with open(commit_references_path, 'a') as commit_references_file:
        initial_branch_commit = (initial_branch_name, initial_commit_hash)
        commit_references_file.write(str(initial_branch_commit) + "\n")



def main():
    for project, project_info in target_projects.items():
        remote_repository = project_info['remote_repository']
        local_repository = project_info['local_repository']
        initial_commit_version = project_info['initial_commit_version']
        commit_references_path = project_info['commit_references_path']

        if os.path.exists(local_repository):
            repo = Repo(local_repository)
            repo.git.checkout(initial_commit_version)
        else:
            repo = Repo.clone_from(remote_repository, local_repository)
            repo.git.checkout(initial_commit_version)

        refact_versioning_init(repo)
        modifier_caller(repo, project, local_repository, commit_references_path)

if __name__ == "__main__":
    main()

