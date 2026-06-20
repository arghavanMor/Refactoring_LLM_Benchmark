package org.refactoring;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class jsonUtils {
    public static void main(String[] args) {
        /*

        JSONParser parser = new JSONParser();
        try {
                JSONObject refactorings = (JSONObject) parser.parse(new FileReader("src/llm_generated_code.json"));
                JSONArray examples = (JSONArray) parser.parse(new FileReader("src/examples.json"));
                String refactoringID = "";

                for (Object key : refactorings.keySet()) {
                    JSONObject value = (JSONObject) refactorings.get(key);
                    refactoringID = "" + value.get("ID");

                    for (Object example : examples)
                    {
                        JSONObject exampleItem = (JSONObject) example;
                        String exampleID = (String) exampleItem.get("\ufeffID");
                        if (exampleID.equals(refactoringID)) {
                            System.out.println("Example : " + exampleID + " and " + exampleItem.get("path_before"));
                        }

                    }
                }
                //System.out.println(refactoringItem.get("FewShotCode"));
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (ParseException e) {
            e.printStackTrace();
        } */
        String test =  "void reportAmbiguity(@NotNull Parser recognizer, \n                          AmbiguityReport ambiguityReport);\n\n// Introduce Parameter Object\nclass AmbiguityReport {\n    private final DFA dfa;\n    private final int startIndex;\n    private final int stopIndex;\n    private final BitSet ambigAlts;\n    private final ATNConfigSet configs;\n\n    public AmbiguityReport(DFA dfa, int startIndex, int stopIndex, BitSet ambigAlts, ATNConfigSet configs) {\n        this.dfa = dfa;\n        this.startIndex = startIndex;\n        this.stopIndex = stopIndex;\n        this.ambigAlts = ambigAlts;\n        this.configs = configs;\n    }\n\n    public DFA getDfa() {\n        return dfa;\n    }\n\n    public int getStartIndex() {\n        return startIndex;\n    }\n\n    public int getStopIndex() {\n        return stopIndex;\n    }\n\n    public BitSet getAmbigAlts() {\n        return ambigAlts;\n    }\n\n    public ATNConfigSet getConfigs() {\n        return configs;\n    }\n}";
        System.out.println(test);
    }
}
