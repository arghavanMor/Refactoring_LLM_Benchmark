import pandas as pd

file_path = "./final_results_fowler.csv"
df = pd.read_csv(file_path)

pivot_df = df.pivot_table(index=["Refactoring method", "Prompt"], 
                          columns="Metric", 
                          values="Average Value").reset_index()

# Rename columns
pivot_df.columns.name = None
pivot_df = pivot_df.rename(columns={
    "Refactoring method": "Refactoring Method",
    "Prompt": "Prompt",
    "CodeBleu": "CodeBleu",
    "Total CC": "Total CC",
    "Total method calls": "Total Method Calls",
    "Total lines of code": "Total Lines of Code"
})

pivot_df["Refactoring Method"] = pivot_df["Refactoring Method"].mask(pivot_df["Refactoring Method"].duplicated(), "")


latex_file_path = "final_results_fowler.tex"
with open(latex_file_path, "w") as f:
    latex_table = pivot_df.to_latex(index=False, column_format="|l|l|c|c|c|c|", escape=False)
    
    # Insert \midrule after every new refactoring method
    lines = latex_table.splitlines()
    new_lines = []
    prev_method = None
    for line in lines:
        columns = line.split("&")
        method = columns[0].strip()
        if prev_method and method and method != prev_method:
            new_lines.append("\\midrule")
        new_lines.append(line)
        prev_method = method if method else prev_method
    
    f.write("\n".join(new_lines))

print(f"LaTeX table saved to {latex_file_path}")
