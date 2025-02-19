import json
from deepdiff import DeepDiff
import subprocess

def llm_generated_code_enhancer():
    data_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/llm_generated_code1.json"
    results_path = "/src/run#9_processed.json"
    with open(data_path, 'r') as llm_generated_code_file:
        generated_code_data = json.load(llm_generated_code_file)


    prompt_approach =  ["ZeroShotCode", "InstrucCode", "FewShotCode"]
    for generated_code_item in generated_code_data.values():
        for prompt_type in prompt_approach:
            generated_code_item[prompt_type] = {'methods': [generated_code_item[prompt_type], ], 'classes':[], 'others':[]}

    json_object = json.dumps(generated_code_data, indent=4)

    with open(results_path, 'w') as results_file:
        results_file.write(json_object)

def results_comparator(result1_path, result2_path):
    with open(result1_path, 'r') as result1_file:
        result1_path_dict = json.load(result1_file)

    with open(result2_path, 'r') as result2_file:
        result2_path_dict = json.load(result2_file)

    diff = DeepDiff(result1_path_dict, result2_path_dict)
    print(diff)

if __name__ == "__main__":
    #result1_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results_summary.json"
    #result2_path = "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/src/results_summary_run#1.json"
    #results_comparator(result1_path, result2_path)
    #llm_generated_code_enhancer()

    #print("public List<SrcOp> set(GrammarAST setAST, GrammarAST labelAST, boolean invert) {\n    MatchSet matchOp = createMatchSet(setAST, invert);\n    if (labelAST != null) {\n        handleLabelAST(labelAST, matchOp, setAST);\n    }\n    if (controller.needsImplicitLabel(setAST, matchOp)) {\n        defineImplicitLabel(setAST, matchOp);\n    }\n    AddToLabelList listLabelOp = getAddToListOpIfListLabelPresent(matchOp, labelAST);\n return list(matchOp, listLabelOp);\n}")
    #print("private MatchSet createMatchSet(GrammarAST setAST, boolean invert) {\n    return invert ? new MatchNotSet(this, setAST) : new MatchSet(this, setAST);\n}")
    #print("private void handleLabelAST(GrammarAST labelAST, MatchSet matchOp, GrammarAST setAST) {\n    String label = labelAST.getText();\n    Decl d = getTokenLabelDecl(label);\n    matchOp.labels.add(d);\n    getCurrentRuleFunction().addContextDecl(setAST.getAltLabel(), d);\n    if (labelAST.parent.getType() == ANTLRParser.PLUS_ASSIGN) {\n        TokenListDecl l = getTokenListLabelDecl(label);\n getCurrentRuleFunction().addContextDecl(setAST.getAltLabel(), l);\n    }\n}")


    mainMethodCode = "mainMethodCode"
    otherMethodsCode = ["otherMethodCode", "otherMethodCode", "otherMethodCode", "otherMethodCode"]
    classesCode = ["classes", "classes", "classes", "classes"]
    otherCode = ["otherCode", "otherCode", "otherCode", "otherCode"]

    otherMethodsCode = "/* */".join(otherMethodsCode)
    classesCode = "/* */".join(classesCode)
    otherCode = "/* */".join(otherCode)

    subprocess.call(['java', '-jar', "/Users/jeancarlorspaul/IdeaProjects/Refactoring_LLM_Benchmark/out/artifacts/Refactoring_LLM_Benchmark_main_jar/Refactoring_LLM_Benchmark.main.jar", "repository_path", "mainMethodName", mainMethodCode, otherMethodsCode, classesCode, otherCode])




