import subprocess
import json
import tempfile
import os
import statistics

GUMTREE_CMD = [
    "java", "-cp",
    "/gumtree/dist/build/install/gumtree/lib/*",
    "com.github.gumtreediff.client.Run"
]

def wrap_and_write(method_code: str) -> str:
    wrapped = f"class Tmp {{\n{method_code}\n}}"
    tmp = tempfile.NamedTemporaryFile(suffix=".java", mode="w", delete=False)
    tmp.write(wrapped)
    tmp.close()
    return tmp.name


def parse_textdiff(output: str) -> dict:
    """Parse GumTree textdiff output into action counts"""
    actions = {
        "insert": 0,
        "delete": 0,
        "move": 0,
        "update": 0
    }

    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("insert-node"):
            actions["insert"] += 1
        elif line.startswith("delete-node"):
            actions["delete"] += 1
        elif line.startswith("move-tree"):
            actions["move"] += 1
        elif line.startswith("update-node"):
            actions["update"] += 1

    return actions

def classify(actions: dict) -> str:
    """Classify refactoring as structural or superficial"""
    if all(v == 0 for v in actions.values()):
        return "no_change"
    elif actions["insert"] > 0 or actions["delete"] > 0 or actions["move"] > 0:
        return "structural"
    else:
        return "superficial"  # only updates (renames)

def gumtree_textdiff(method1: str, method2: str) -> str:
    f1 = wrap_and_write(method1)
    f2 = wrap_and_write(method2)
    try:
        result = subprocess.run(
            GUMTREE_CMD + ["textdiff", f1, f2],
            capture_output=True, text=True
        )
        return result.stdout
    finally:
        os.unlink(f1)
        os.unlink(f2)

def analyze_pair(method1: str, method2: str) -> dict:
    output = gumtree_textdiff(method1, method2)
    actions = parse_textdiff(output)
    label = classify(actions)
    return {"actions": actions, "classification": label}

def diff_assessment(pairs):
    structural  = 0
    superficial = 0
    no_change   = 0

    for original, refactored in pairs:
        result = analyze_pair(original, refactored)
        print("   ", result["classification"])

def diff_assessment_caller():
    methods_path = "src/llm_generated_code/chat_gpt_4o_mini/run#1_processed.json"
    with open(methods_path, 'r') as file:
        method_data = json.load(file)
    for case_key, case_value in method_data.items():
        original_method = case_value["BeforeRefact"]
        superficial = 0
        for prompt_strategy, method_code in case_value.items():
            if type(method_code)==str:
                continue
            print(prompt_strategy)
            if len(method_code['methods']) == 1 and len(method_code['classes']) == 0:
                refactored_method = method_code["methods"][0]
                pairs = [(original_method, refactored_method),]
                diff_assessment(pairs)
            else:
                print("    structural")

        print("="*200)



if __name__ == "__main__":
    pass


