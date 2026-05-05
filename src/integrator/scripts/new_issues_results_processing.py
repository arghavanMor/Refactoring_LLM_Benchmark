import json
import statistics


def main(issues_path):
    with open(issues_path, 'r') as file:
        issues_dict = json.load(file)

    for llm, llm_result_value in issues_dict.items():
        maint_prompt_strategy_dict = {'ZeroShotCode': [],
                                      'FewShotCode': [],
                                      'InstrucCode': [],
                                      'RulesCode': [],
                                      'ContextCode': [],
                                      }

        reliab_prompt_strategy_dict = {'ZeroShotCode': [],
                                       'FewShotCode': [],
                                       'InstrucCode': [],
                                       'RulesCode': [],
                                       'ContextCode': [],
                                       }
        print(llm)
        for iteration, results_by_prompt_strategy in llm_result_value.items():
            for prompt_strategy, issue_results in  results_by_prompt_strategy.items():
                maint_prompt_strategy_dict[prompt_strategy].append(issue_results['maintainability_issues_number'])
                reliab_prompt_strategy_dict[prompt_strategy].append(issue_results['reliability_issues_number'])

        #print("-"*200)
        print("Maintainability issues")
        for prompt_strategy, maint_issue_results in maint_prompt_strategy_dict.items():
            print(prompt_strategy, ": Mean: ", statistics.mean(maint_issue_results), ", STD: ", statistics.stdev(maint_issue_results))
        print("Reliability issues")
        for prompt_strategy, reliab_issue_results in reliab_prompt_strategy_dict.items():
            print(prompt_strategy, ": Mean: ", statistics.mean(reliab_issue_results), ", STD: ", statistics.stdev(reliab_issue_results))


if __name__ == "__main__":
    print('Removed quality code issues')
    issues_path = "src/results/removed_issues_result.json"
    main(issues_path)
    print('New quality code issues')
    issues_path = "src/results/new_issues_result.json"
    main(issues_path)