from pathlib import Path
#rom collections import OrderedDict

import PyTokenCounter as tc
#import tiktoken

# Count tokens in a string for an LLM model
#numTokens = tc.GetNumTokenStr(
 #   string="This is a test string.", model="gpt-4o"
#)
#print(f"Number of tokens: {numTokens}")

# Count tokens in a file intended for LLM processing
filePath = Path("Data/fowler_run#5.csv")
numTokensFile = tc.GetNumTokenFile(filePath=filePath, model="gpt-4o")
print(f"Number of tokens in file: {numTokensFile}")