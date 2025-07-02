This is a benchmark for different types of recatorings collected from Martin Fowler Catalog. We leverage different LLMs to conduct each refactoring by using different types of prompts.

The framework structure:
├── out
│   ├── artifacts
│   │   └── RefactoringApplier_jar
│   └── production
│       └── resources
│           └── META-INF
├── Data
└── src
    ├── llm_generated_code
    │   ├── chat_gpt_4o_mini
    │   └── deep_seek
    ├── projects
    │   ├── stdout
    │   │   ├── antlr4
    │   │   └── junit4
    │   ├── stderr
    │   │   ├── antlr4
    │   │   └── junit4
    │   ├── failed_test_error
    │   │   └── antlr4
    ├── utils
    ├── results
    │   ├── chat_gpt_4o_mini
    │   │   ├── antlr4_results
    │   │   └── junit4_results
    │   └── deep_seek
    │       ├── antlr4_results
    │       └── junit4_results
    ├── main
    │   ├── resources
    │   │   └── META-INF
    │   └── java
    │       └── org
    │           └── refactoring
    └── Data
