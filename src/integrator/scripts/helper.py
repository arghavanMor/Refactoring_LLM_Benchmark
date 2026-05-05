import os
import json
import re
import statistics
from pprint import pprint
from itertools import groupby
from collections import Counter

llm_list = ["deep_seek",]

def print_tree(startpath, prefix=''):
    items = os.listdir(startpath)
    for index, item in enumerate(items):
        path = os.path.join(startpath, item)
        #print((os.path.basename(path)))
        if ((os.path.basename(path)=="RefactoringApplier_jar") or (os.path.basename(path)=="META-INF")
            or ((os.path.basename(path)=="llm_generated_code") or (os.path.basename(path)=="chat_gpt_4o_mini")
            or (os.path.basename(path)=="deep_seek") or (os.path.basename(path)=="utils")
            or (os.path.basename(path)=="refactoring")) or (os.path.basename(path)=="Data")):
            pass
        else:
            if ((not os.path.isdir(path)) or item.startswith('.') or item.startswith('run#') or item.startswith('_')
                or (item=="build")):
                continue
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, prefix + extension)
"""
startpath = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/"
print_tree(startpath)
"""

def refactoring_parsing_error_processing(path):
    files_path = os.listdir(path)
    results_dictionary = dict()
    for file_name in files_path:
        if "summary" in file_name:
            continue
        file_path = os.path.join(path, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

            file_content = file_content.split("Problem stacktrace :")[0]
            results_dictionary[file_name] = [file_content,]

    json_object = json.dumps(results_dictionary, indent=4)
    results_path = os.path.join(path, "parsing_stderr_summary.json")
    with open(results_path, 'w') as results_file:
        results_file.write(json_object)

llm_list = ["review-gpt-4o-mini",]

"""
for llm_id in (llm_list):
    for project in ("antlr4",):
        for item in range(1,6):
            which_run = "/compilation_run#" + str(item)
            stderr_path = "results/" +  llm_id + which_run + "/" + project + "/refactoring_parsing/stderr"
            refactoring_parsing_error_processing(stderr_path)
"""


def compilation_error_processing(path):
    files_path = os.listdir(path)
    results_dictionary = dict()
    k = 0
    for file_name in files_path:
        #print(file_name)
        file_path = os.path.join(path, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()

            clean_log = re.sub(r"\x1b\[[0-9;]*m", "", file_content)
            #print(file_content)
            #print(clean_log)

            if ("antlr4" in path) and "COMPILATION ERROR" in file_content:
                match = re.search(r"COMPILATION ERROR\s*:\s*(.*?)\b\d+\s+error", clean_log, re.DOTALL)
                #print(match)
                if match:
                    first_result = match.group(1).strip()


                    splitter1 = "[ERROR]"
                    first_result = first_result.split(splitter1)

                    first_result_list = first_result[1:]
                    #print(first_result_list)
                    ###################
                    splitter2 = ".java:"
                    splitter3 = "\n"
                    temp_list = []
                    for item in first_result_list:
                        #print(item)
                        item = item.split(splitter2)[1]
                        item = item.replace("   ", " ")
                        item = item.replace("  ", " ")
                        if "cannot find symbol" in item:
                            temp_list.append(item.split(splitter3)[0] + item.split(splitter3)[1])
                        else:
                            temp_list.append(item.split(splitter3)[0])

                    last_results = temp_list
                    results_dictionary[file_name] = last_results
                    #print(results_dictionary)

            if ("junit4" in path) and "error" in file_content:
                match = re.search(r'error: (.*?)\[', file_content, re.DOTALL)
                if match:
                    first_result = "match.group(1).strip()"
                    #print(first_result)

                    #last_results = temp_list
                    ###################
                    results_dictionary[file_name] = first_result
                else:
                    pass
                    print("No match found.")
    error_counter(path, results_dictionary)


def error_counter(path, results_dictionary):
    temp_dict = dict()
    error_quantity = 0
    substring_list = ["cannot find symbol symbol: variable",
                      "is already defined in class",
                      "cannot be applied to given types",
                      "incompatible types",
                      "cannot find symbol symbol: method",
                      "cannot be referenced from a static context",
                      "is not abstract and does not override abstract method",
                      "Illegal static declaration in inner class",
                      "illegal parenthesized expression",
                      "cannot be accessed from outside package",
                      "diamond operator is not supported in -source 6",
                      "cannot assign a value to final variable",
                      "missing return statement",
                      'modifier static not allowed here',
                      'method does not override or implement a method from a supertype'
                      ]
    for substring in substring_list:
        temp_dict[substring] = 0
    for k, v in results_dictionary.items():
        if "summary" in k:
            continue
        if isinstance(v, list):
            error_quantity = error_quantity + len(v)
            for error_msg in v:
                substring_presence = False
                for substring in substring_list:
                    if substring in error_msg:
                        substring_presence = True
                        temp_dict[substring] = temp_dict[substring] + 1
                if not substring_presence:
                    #pass
                    print(error_msg)
        else:
            for substring in substring_list:
                if substring in v:
                    temp_dict[substring] = temp_dict[substring] + 1
    temp_dict["error_quantity"] = error_quantity
    results_dictionary["Error_summary"] = temp_dict


    temp_sum = 0
    for k,v in temp_dict.items():
        if not "error_quantity" in k:
            temp_sum = temp_sum + v
    temp_dict["error_quantity"] = temp_sum

    #print(results_dictionary)


    json_object = json.dumps(results_dictionary, indent=4)
    results_path = os.path.join(path, "compilation_error_summary.json")

    with open(results_path, 'w') as results_file:
        results_file.write(json_object)



"""
for llm_id in (llm_list):
    for item in range(1,6):
        for project in (["/antlr4",]): # "/junit4"):
            which_run = "/parsing_run#" + str(item)
            compilation_stdout_path = "results/" +  llm_id + which_run + project + "/compilation/stdout"
            compilation_error_processing(compilation_stdout_path)

##############################################

Another helper function
def clean_log(file_path):
    #file_path = os.path.join(path, file_name)
    with open(file_path, 'r') as file:
        file_content = file.read()

    clean_log = re.sub(r"\x1b\\[[0-9;]*m", "", file_content) ###### Must the \\[ escape warning

    with open(file_path, 'w') as file:
        file.write(clean_log)

for llm_id in ("chat_gpt_4o_mini", "deep_seek"):
    for item in range(1,6):
        for project in (["/antlr4",]): # "/junit4"):
            which_run = "/run#" + str(item)
            compilation_stdout_path = "results/" +  llm_id + which_run + project + "/compilation/stdout"
            files_path = os.listdir(compilation_stdout_path)
            files_path = [item for item in files_path if "summary" not in item]
            for file_name in files_path:
                file_path = os.path.join(compilation_stdout_path, file_name)
                #print(file_path)
                clean_log(file_path)
"""

def deduplicate_results(compilation_stdout_path):
    file_name = "compilation_error_summary.json"
    file_path = os.path.join(compilation_stdout_path, file_name)
    with open(file_path, 'r') as file:
        data = json.load(file)

    for key, value in data.items():
        if "summary" not in key:
            temp_list = data[key]
            #for item in data[key]:
             #   item = item.split("] ")[1]
              #  temp_list.append(item)
            temp_list = list(set(temp_list))
            data[key] = temp_list

    error_counter(compilation_stdout_path, data)

"""
for llm_id in ("chat_gpt_4o_mini", "deep_seek"):
    for item in range(1,6):
        for project in (["/antlr4",]): # "/junit4"):
            which_run = "/run#" + str(item)
            compilation_stdout_path = "results/" +  llm_id + which_run + project + "/compilation/stdout"
            #files_path = os.listdir(compilation_stdout_path)
            #files_path = [item for item in files_path if "summary" in item]
            #for file_name in files_path:
             #   file_path = os.path.join(compilation_stdout_path, file_name)
            deduplicate_results(compilation_stdout_path)
"""

"""
for llm_id in ("chat_gpt_4o_mini", "deep_seek"):

    print("*"*80, llm_id, "*"*80)
    for project in ("/antlr4" ,"/junit4"):
        results_list = []
        print("="*80, project, "="*80)
        for item in range(1,6):
            which_run = "/run#" + str(item)
            print("-"*80, which_run, "-"*80)
            path_suffix = "compilation_error_summary.json"
            parsing_stderr_path = "results/" +  llm_id + which_run + project + "/compilation/stdout/" + path_suffix

            #print(parsing_stderr_path)
            with open(parsing_stderr_path, 'r') as file:
                data = json.load(file)
            #print(data)
            results_list.append(data["Error_summary"])
            pprint(data["Error_summary"])
        #pprint(results_list)
        #print("Error_summary: ", results_list)
        print("="*180)
"""

"""generated_code_path_ref = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/llm_generated_code/deep_seek/run#_processed.json"

data_runs = dict()

for item in range(1,6):
    run = "run#" + str(item)
    generated_code_path = generated_code_path_ref.replace("#", "#" + str(item))
    with open(generated_code_path, 'r') as file:
        data = json.load(file)
    data_runs[run] = data

id_list = ['L10937', 'L5343', 'L3671', 'L3692', 'L7413', 'L10037', 'L1927', 'L540', 'L561', 'L5431', 'L3844', 'L3168', 'L10263', 'L102630', 'L15668', 'L156680', 'L3347', 'L2755', 'L13228', 'L8024', 'L9806', 'L1506', 'L1991', 'L19910', 'L2113', 'L2427', 'L9795', 'L9861', 'L2093', 'L2083', 'L2079', 'L2075', 'L1276', 'L7856', 'L3524', 'L2447', 'L24470', 'L2288', 'L2588', 'L3072', 'L5418', 'L3446', 'L3949', 'L8052', 'L4884', 'L5882', 'L5880', 'L4889', 'L7126', 'L126']

for run in data_runs.keys():
    print("="*80, run, "="*80)
    for gen_code in data_runs[run].keys():
        print(gen_code)

prompting_approaches = ['ZeroShotCode', 'InstrucCode', 'FewShotCode', 'ContextCode', 'RulesCode']
generated_code_members = ['methods', 'classes'] #, 'others']

for id in id_list:
    for prompting_approach in prompting_approaches:
        for generated_code_member in generated_code_members:
            if data_runs["run#2"][id][prompting_approach][generated_code_member] == data_runs["run#3"][id][prompting_approach][generated_code_member]:
                pass
            else:
                print("run#2", id, prompting_approach, generated_code_member)
            if data_runs["run#3"][id][prompting_approach][generated_code_member] == data_runs["run#4"][id][prompting_approach][generated_code_member]:
                pass
            else:
                print("run#3", id, prompting_approach, generated_code_member)
            if data_runs["run#4"][id][prompting_approach][generated_code_member] == data_runs["run#5"][id][prompting_approach][generated_code_member]:
                pass
            else:
                print("run#4", id, prompting_approach, generated_code_member)"""



"""


compilation_error_path_ref = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results/chat_gpt_4o_mini/run#/antlr4/compilation/stdout/compilation_error_summary.json"
data_runs = dict()

for item in range(1,6):
    run = "run#" + str(item)
    compilation_error_path = compilation_error_path_ref.replace("#", "#" + str(item))
    with open(compilation_error_path, 'r') as file:
        data = json.load(file)
    data_runs[run] = data

generated_code_path_ref = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/llm_generated_code/deep_seek/run#_processed.json"

generated_data_runs = dict()

for item in range(1,6):
    run = "run#" + str(item)
    generated_code_path = generated_code_path_ref.replace("#", "#" + str(item))
    with open(generated_code_path, 'r') as file:
        generated_data = json.load(file)
    generated_data_runs[run] = generated_data


for cmp_err_key, cmp_err_val in data_runs["run#2"].items():
    if cmp_err_key=="Error_summary":
        continue
    shared_cmp_err_key = cmp_err_key[:-63]
    print("="*200)
    print(shared_cmp_err_key)
    for k, v in data_runs["run#3"].items():
        shared_cmp_err_key_exist = shared_cmp_err_key in k
        if shared_cmp_err_key_exist:
            value_different = cmp_err_val!=v
            if value_different:
                print("OK!")
            else:
                id, _, prompting_approach = shared_cmp_err_key.split("&")
                if prompting_approach[-1] != "e":
                    prompting_approach = prompting_approach + "e"
                print(generated_data_runs["run#2"][id][prompting_approach]['classes'])
                print(generated_data_runs["run#3"][id][prompting_approach]['classes'])
    print("="*200)

"""
######## Sonar Helper Code

def issue_analyzer():
    issue_report_path = "src/results/deep_seek/run#5/before_and_after/sonar-report.json"
    output_path = "src/results/deep_seek/run#5/before_and_after/filtered_sonar-report.json"
    with open(issue_report_path, 'r') as file:
        issue_report_data = json.load(file)

    keys_to_keep = {"key", "rule", "component", "message", "impacts"}
    filtered_issues = [
        {k: v for k, v in issue.items() if k in keys_to_keep}
        for issue in issue_report_data
    ]

    filtered_issues_dict = {}

    prompt_strategy_list = ['ZeroShotCode', 'FewShotCode', 'InstrucCode', 'RulesCode', 'ContextCode']
    for prompt_strategy in prompt_strategy_list:
        filtered_issues_dict[prompt_strategy] = [item for item in filtered_issues if prompt_strategy in item['component']]
    with open(output_path, "w") as f:
        json.dump(filtered_issues_dict, f, indent=4)

    #with open(output_path, "w") as f:
     #   json.dump(filtered_issues, f, indent=4)
    print(f"\n✅ Done! {len(filtered_issues)} issues exported to '{output_path}'")

def sonar_file_processing():
    sonar_file_path = "src/results/deep_seek/run#1/before_and_after/filtered_sonar-report.json"
    new_issues_path = "src/results/deep_seek/run#1/before_and_after/new_issues.json"
    removed_issues_path = "src/results/deep_seek/run#1/before_and_after/removed_issues.json"

    with open(sonar_file_path, 'r') as file:
        issue_report_data = json.load(file)

    prompt_strategy_list = ['ZeroShotCode', 'FewShotCode', 'InstrucCode', 'RulesCode', 'ContextCode']
    new_issues_dict = dict()
    removed_issues_dict = dict()

    for prompt_strategy in prompt_strategy_list:
        new_issues_dict[prompt_strategy] = []
        removed_issues_dict[prompt_strategy] = []
        issue_report_data_item = issue_report_data[prompt_strategy]
        data_sorted = sorted(issue_report_data_item, key=lambda x: x['component'])  # must sort first!
        grouped = {k: list(v) for k, v in groupby(data_sorted, key=lambda x: x['component'])}
        new_issues_dict_item = dict()
        removed_issues_dict_item = dict()
        for k, v in grouped.items():
            if "before/" in k:
                continue
            swapping_key = k.replace("/after", "/before")
            before_messages = {issue["message"] for issue in grouped.get(swapping_key, [])}
            new_issues = [issue for issue in v if issue["message"] not in before_messages]

            if new_issues:
                #new_issues_dict_item[k] = new_issues
                new_issues_dict[prompt_strategy].extend(new_issues)
        #new_issues_dict[prompt_strategy] = new_issues_dict_item

        with open(new_issues_path, "w") as f:
            json.dump(new_issues_dict, f, indent=4)


        for k, v in grouped.items():
            if "/after" in k:
                continue
            swapping_key = k.replace("before/", "after/")
            after_messages = {issue["message"] for issue in grouped.get(swapping_key, [])}
            removed_issues = [issue for issue in v if issue["message"] not in after_messages]

            if removed_issues:
                #removed_issues_dict_item[k] = removed_issues
                removed_issues_dict[prompt_strategy].extend(removed_issues)
        #removed_issues_dict[prompt_strategy] = removed_issues_dict_item

        with open(removed_issues_path, "w") as f:
            json.dump(removed_issues_dict, f, indent=4)

def issue_counter(llm, iteration):
    sonar_file_path = "src/results/chat_gpt_4o_mini/run#1/before_and_after/filtered_sonar-report.json"
    new_issues_path = "src/results/chat_gpt_4o_mini/run#1/before_and_after/new_issues.json"
    removed_issues_path = "src/results/chat_gpt_4o_mini/run#1/before_and_after/removed_issues.json"

    sonar_file_path = sonar_file_path.replace("chat_gpt_4o_mini", llm).replace("1", str(iteration))
    #print(sonar_file_path)
    new_issues_path = new_issues_path.replace("chat_gpt_4o_mini", llm).replace("1", str(iteration))
    #print(new_issues_path)
    removed_issues_path = removed_issues_path.replace("chat_gpt_4o_mini", llm).replace("1", str(iteration))
    #print(removed_issues_path)

    total_issues_dict = dict()

    with open(removed_issues_path, 'r') as file:
        issue_report_data = json.load(file)

    issue_total_number = 0
    for prompt_strategy, issues in issue_report_data.items():
        #print("="*200)
        #print(prompt_strategy)
        #print("Total issues for", prompt_strategy, ": ",  len(issues))
        issue_total_number += len(issues)

        maintainability_issues = [item for item in issues if "MAINTAINABILITY" in item['impacts'][0]['softwareQuality']]
        reliability_issues = [item for item in issues if "RELIABILITY" in item['impacts'][0]['softwareQuality']]

        b_maintainability_issues = [item for item in maintainability_issues if "BLOCKER" in item['impacts'][0]['severity']]
        b_reliability_issues = [item for item in reliability_issues if "BLOCKER" in item['impacts'][0]['severity']]

        h_maintainability_issues = [item for item in maintainability_issues if "HIGH" in item['impacts'][0]['severity']]
        h_reliability_issues = [item for item in reliability_issues if "HIGH" in item['impacts'][0]['severity']]

        m_maintainability_issues = [item for item in maintainability_issues if "MEDIUM" in item['impacts'][0]['severity']]
        m_reliability_issues = [item for item in reliability_issues if "MEDIUM" in item['impacts'][0]['severity']]

        l_maintainability_issues = [item for item in maintainability_issues if "LOW" in item['impacts'][0]['severity']]
        l_reliability_issues = [item for item in reliability_issues if "LOW" in item['impacts'][0]['severity']]

        i_maintainability_issues = [item for item in maintainability_issues if "INFO" in item['impacts'][0]['severity']]
        i_reliability_issues = [item for item in reliability_issues if "INFO" in item['impacts'][0]['severity']]

        maintainability_issues_number = len(maintainability_issues)
        reliability_issues_number = len(reliability_issues)
        b_maintainability_issues_number = len(b_maintainability_issues)
        b_reliability_issues_number = len(b_reliability_issues)
        h_maintainability_issues_number = len(h_maintainability_issues)
        h_reliability_issues_number = len(h_reliability_issues)
        m_maintainability_issues_number = len(m_maintainability_issues)
        m_reliability_issues_number = len(m_reliability_issues)
        l_maintainability_issues_number = len(l_maintainability_issues)
        l_reliability_issues_number = len(l_reliability_issues)
        i_maintainability_issues_number = len(i_maintainability_issues)
        i_reliability_issues_number = len(i_reliability_issues)


        """print("-"*200)
        print('maintainability_issues_number', maintainability_issues_number)
        print('reliability_issues_number', reliability_issues_number)
        print('blocker_maintainability_issues_number', b_maintainability_issues_number)
        print('blocker_reliability_issues_number', b_reliability_issues_number)
        print('high_maintainability_issues_number', h_maintainability_issues_number)
        print('high_reliability_issues_number', h_reliability_issues_number)
        print('medium_maintainability_issues_number', m_maintainability_issues_number)
        print('medium_reliability_issues_number', m_reliability_issues_number)
        print('low_maintainability_issues_number', l_maintainability_issues_number)
        print('low_reliability_issues_number', l_reliability_issues_number)
        print('info_maintainability_issues_number', i_maintainability_issues_number)
        print('info_reliability_issues_number', i_reliability_issues_number)"""
        total_issues_dict.setdefault(prompt_strategy, {})['maintainability_issues_number'] = maintainability_issues_number
        total_issues_dict[prompt_strategy]['reliability_issues_number'] = reliability_issues_number
        total_issues_dict[prompt_strategy]['blocker_maintainability_issues_number'] = b_maintainability_issues_number
        total_issues_dict[prompt_strategy]['blocker_reliability_issues_number'] = b_reliability_issues_number
        total_issues_dict[prompt_strategy]['high_maintainability_issues_number'] = h_maintainability_issues_number
        total_issues_dict[prompt_strategy]['high_reliability_issues_number'] = h_reliability_issues_number
        total_issues_dict[prompt_strategy]['medium_maintainability_issues_number'] = m_maintainability_issues_number
        total_issues_dict[prompt_strategy]['medium_reliability_issues_number'] = m_reliability_issues_number
        total_issues_dict[prompt_strategy]['low_maintainability_issues_number'] = l_maintainability_issues_number
        total_issues_dict[prompt_strategy]['low_reliability_issues_number'] = l_reliability_issues_number
        total_issues_dict[prompt_strategy]['info_maintainability_issues_number'] = i_maintainability_issues_number
        total_issues_dict[prompt_strategy]['info_reliability_issues_number'] = i_reliability_issues_number
    #print('Run#', iteration, " : ", prompt_strategy, 'issues.')
    #print("="*200)
    return total_issues_dict

def issue_counter_caller():
    filtered_sonar_result_path = "src/results/removed_issues_result.json"
    results = {}
    llms = ["chat_gpt_4o_mini", "deep_seek"]
    for llm in llms:

        for iteration in range(1,6):
            #print(llm, iteration)
            total_issues_dict = issue_counter(llm, iteration)
            #print("total_issues_dict", total_issues_dict)
            results.setdefault(llm, {})[str(iteration)] = total_issues_dict

    #print("results", results)
    with open(filtered_sonar_result_path, "w") as f:
        json.dump(results, f, indent=4)


def compute_mean_across_iterations(total_issues_dict_path):
    with open(total_issues_dict_path, 'r') as file:
        total_issues_dict = json.load(file)

    mean_dict = {}

    for model, iterations in total_issues_dict.items():
        mean_dict[model] = {}

        # Collect all prompt strategies
        prompt_strategies = set(
            strategy
            for iter_data in iterations.values()
            for strategy in iter_data.keys()
        )

        for strategy in prompt_strategies:
            # Collect all metrics for this strategy across iterations
            all_metrics = [
                iter_data[strategy]
                for iter_data in iterations.values()
                if strategy in iter_data  # safe if a strategy is missing in some iteration
            ]

            # Average each metric
            metric_keys = all_metrics[0].keys()
            mean_dict[model][strategy] = {
                metric: sum(d[metric] for d in all_metrics) / len(all_metrics)
                for metric in metric_keys
            }

    return mean_dict

def compute_mean_across_iterations_caller():
    total_issues_dict_path = "src/results/removed_issues_result.json"
    statistic_issues_dict_path = "src/results/removed_issues_statistic_issues.json"
    mean_results = compute_mean_across_iterations(total_issues_dict_path)
    pprint(mean_results)

    with open(statistic_issues_dict_path, "w") as f:
        json.dump(mean_results, f, indent=4)


if __name__ == "__main__":
    pass
