import tiktoken
from pathlib import Path
import json
import statistics
from collections import Counter
import lizard
import tempfile
import os

def count_tokens_from_json(file_path: Path, model: str = "gpt-4o") -> int:
    """Count tokens in a JSON file using tiktoken"""
    # Read with utf-8, ignore bad characters
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(content))

def count_token(file_path, model: str = "gpt-4o"):
    with open(file_path, 'r') as file:
        code_data = json.load(file)
    token_length_list = []
    for code_value in code_data:
        method_code = code_value['BeforeRefact']
        enc = tiktoken.encoding_for_model(model)
        clean = method_code.encode("utf-8", errors="ignore").decode("utf-8")
        print(code_value["\ufeffID"])
        print(len(enc.encode(clean)))
    #print(statistics.mean(token_length_list))

def get_complexity(method_code: str) -> dict:
    """
    Compute cyclomatic complexity and other metrics for a Java method.
    """
    # Wrap in class so lizard can parse it
    wrapped = f"public class Tmp {{\n{method_code}\n}}"

    # Write to temp file
    tmp = tempfile.NamedTemporaryFile(
        suffix=".java", mode="w",
        delete=False, encoding="utf-8"
    )
    tmp.write(wrapped)
    tmp.close()

    try:
        result = lizard.analyze_file(tmp.name)

        if result.function_list:
            fn = result.function_list[0]
            return {
                "cyclomatic_complexity": fn.cyclomatic_complexity,
                #"lines_of_code"        : fn.nloc,
                "token_count"          : fn.token_count,
            }
        else:
            return {"error": "No method found"}

    finally:
        os.unlink(tmp.name)


# ── Usage ─────────────────────────────────────────────────────────────────────

def get_info_from_original_method_code():
    file_path = Path("src/Data/Data_collection.json")
    complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    with open(file_path, 'r') as file:
        code_data = json.load(file)
    code_info_dict = {}
    for code_value in code_data:
        method_code = code_value['BeforeRefact']
        metrics = get_complexity(method_code)
        code_info_dict[code_value["\ufeffID"]] = metrics

    with open(complexity_file_path, "w") as f:
        json.dump(code_info_dict, f, indent=4)
    print(code_info_dict)

def get_successful_refactoring_rate_by_ID(llm, iteration):
    iteration = "run#" +  str(iteration)
    file_path = "src/results/" + llm + "/" + iteration + "/before_and_after"
    complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    with open(complexity_file_path, 'r') as file:
        complexity_data = json.load(file)
    dir_list = []
    ID_dict = {}
    for dir in ['antlr4', 'junit4']:
        file_path_item = os.path.join(file_path, dir)

        for dir_inner in os.listdir(file_path_item):
            dir_list.append(dir_inner.split("&")[0])
    counts = Counter(dir_list)
    for item, count in counts.most_common():
        ID_dict[item] = count

    for id_key, complexity_value in complexity_data.items():
        complexity_value.setdefault(llm, {})[iteration] = ID_dict.get(id_key, 0)


    with open(complexity_file_path, "w") as f:
        json.dump(complexity_data, f, indent=4)

def min_max_counter():
    complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    with open(complexity_file_path, 'r') as file:
        code_data = json.load(file)
    code_data_cc =  [val['cyclomatic_complexity'] for val in code_data.values()]
    code_data_token = [val['token_count'] for val in code_data.values()]

    print(min(code_data_cc), max(code_data_cc))
    print(min(code_data_token), max(code_data_token))
    print(code_data_cc)

if __name__ == "__main__":
    run_1 = {'L2113': 10, 'L3168': 5, 'L2588': 5, 'L5418': 5, 'L3347': 5, 'L2427': 5, 'L5431': 5, 'L10937': 5, 'L9806': 5, 'L3446': 5, 'L3844': 5, 'L5343': 5, 'L3671': 5, 'L2755': 5, 'L156680': 5, 'L2288': 5, 'L15668': 5, 'L3692': 5, 'L3072': 5, 'L4884': 5, 'L5880': 5, 'L5882': 5, 'L7126': 5, 'L4889': 5, 'L7856': 4, 'L2075': 4, 'L1276': 4, 'L2079': 4, 'L2093': 3, 'L2083': 2, 'L2447': 1, 'L24470': 1, 'L126': 1}
    run_2 = {'L2113': 20, 'L3671': 10, 'L2075': 10, 'L3844': 10, 'L2093': 10, 'L2755': 10, 'L2079': 10, 'L15668': 10, 'L1276': 10, 'L5343': 10, 'L3446': 10, 'L3347': 10, 'L2427': 10, 'L2588': 10, 'L9806': 10, 'L3692': 10, 'L2083': 10, 'L5431': 10, 'L2288': 10, 'L3072': 10, 'L10937': 10, 'L156680': 10, 'L5418': 10, 'L3168': 10, 'L7856': 8, 'L9795': 6, 'L4889': 5, 'L5880': 5, 'L5882': 5, 'L7126': 5, 'L4884': 5, 'L13228': 4, 'L9861': 4, 'L24470': 2, 'L1506': 2, 'L1927': 2, 'L126': 1}
    run_3 = {'L2113': 20, 'L2288': 10, 'L3072': 10, 'L5418': 10, 'L156680': 10, 'L3347': 10, 'L9806': 10, 'L3168': 10, 'L5431': 10, 'L3692': 10, 'L10937': 10, 'L3671': 10, 'L3844': 10, 'L5343': 10, 'L15668': 10, 'L2427': 10, 'L2079': 10, 'L2083': 10, 'L3446': 10, 'L2755': 10, 'L2075': 10, 'L1276': 10, 'L2093': 10, 'L2588': 10, 'L7856': 8, 'L9795': 6, 'L4884': 5, 'L4889': 5, 'L7126': 5, 'L5880': 5, 'L5882': 5, 'L9861': 4, 'L13228': 4, 'L1927': 2, 'L24470': 2, 'L1506': 2, 'L126': 1}
    run_4 = {'L2113': 10, 'L2588': 5, 'L2075': 5, 'L15668': 5, 'L2083': 5, 'L3844': 5, 'L3168': 5, 'L3446': 5, 'L3692': 5, 'L10937': 5, 'L5343': 5, 'L156680': 5, 'L2288': 5, 'L3671': 5, 'L2755': 5, 'L2427': 5, 'L3072': 5, 'L2079': 5, 'L9806': 5, 'L3347': 5, 'L5418': 5, 'L5431': 5, 'L5882': 5, 'L5880': 5, 'L4884': 5, 'L4889': 5, 'L7126': 5, 'L7856': 4, 'L1276': 4, 'L2093': 3, 'L24470': 1, 'L2447': 1, 'L126': 1}
    run_5 = {'L2113': 10, 'L2427': 5, 'L3671': 5, 'L2755': 5, 'L2588': 5, 'L5343': 5, 'L2079': 5, 'L156680': 5, 'L3168': 5, 'L3072': 5, 'L3347': 5, 'L2075': 5, 'L3446': 5, 'L9806': 5, 'L5431': 5, 'L15668': 5, 'L2288': 5, 'L10937': 5, 'L3844': 5, 'L5418': 5, 'L2083': 5, 'L3692': 5, 'L4889': 5, 'L5880': 5, 'L7126': 5, 'L5882': 5, 'L4884': 5, 'L7856': 4, 'L1276': 4, 'L2093': 3, 'L2447': 1, 'L24470': 1, 'L126': 1}

    # Usage — drop-in replacement for your original code
    filePath = Path("src/llm_generated_code/deep_seek/run#5_processed.json")
    numTokensFile = count_tokens_from_json(filePath, model="gpt-4o")
    print(f"Number of tokens in file: {numTokensFile}")


