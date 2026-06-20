from scipy.stats import mannwhitneyu, shapiro, ttest_ind
import pandas as pd
import csv


# df = pd.read_csv("./src/analysis/final_ds_results.csv")

# print(df.head())

def get_data_source_from_path(filepath):
    if filepath == "./src/analysis/raw_data_ds_fowler.csv":
        return "DeepSeek Fowler"
    if filepath == "./src/analysis/raw_data_gpt_fowler.csv":
        return "GPT Fowler"
    if filepath == "./src/analysis/raw_data_ds.csv":
        return "DeepSeek Ref-Finder"
    if filepath == "./src/analysis/raw_data_gpt.csv":
        return "GPT Ref-Finder"

# DO NOT USE. This function is not as complete as show_p_value with more complex comparisons 
def record_p_value(filepath1, filepath2, category, subcategory):
    with open(filepath1, "r") as csv_file_1, open(filepath2, "r") as csv_file_2:
        ds_reader = csv.DictReader(csv_file_1)
        reader = csv.DictReader(csv_file_2)
        
        data1 = []
        data2 = []
        
        # We always compare the the before refactoring ground truth here
        if filepath1 == filepath2:
            for row in reader:
                if row["Prompt"] == "AfterRefact" and row["Metric"] == subcategory:
                    if row["Value"]:
                        data1.append(float(row["Value"]))
                if row["Prompt"] == category and row["Metric"] == subcategory:
                    if row["Value"]:
                        data2.append(float(row["Value"]))
        
        else:
            for row in reader:
                if row[category] == subcategory:
                    if row["Value"]:
                        data1.append(float(row["Value"]))

            for row in ds_reader:
                if row[category] == subcategory:
                    if row["Value"]:
                        data2.append(float(row["Value"]))

        
        stat, p_value_shapiro = shapiro(data2)

        print(len(data1))
        
        # Mann Whitney
        if p_value_shapiro < 0.05:
            stat_test = "Mann-Whitney"
            statistic, p_value = mannwhitneyu(data1, data2)
            print(f'Mann-Whitney U statistic: {statistic}')
            print(f'p-value: {p_value}')
        # T-test
        else:
            stat_test = "T-test"
            t_stat, p_value = ttest_ind(data1, data2)
            print("T-statistic:", t_stat)
            print("P-value:", p_value)

    # Record value
    with open("./src/analysis/statistics.csv", mode="a", newline='') as stat_csv:
        data_source1 = get_data_source_from_path(filepath1)
        data_source2 = get_data_source_from_path(filepath2)

        new_row = [data_source1, data_source2, category, subcategory, stat_test,p_value]
        writer = csv.writer(stat_csv)
        stat_csv.seek(0, 2)
        writer.writerow(new_row)

# This function is used for statistical analysis for significance. The points of comparison need to be changed below
def show_p_value(filepath1, filepath2):
    with open(filepath1, "r") as csv_file_1, open(filepath2, "r") as csv_file_2:
        reader_1 = csv.DictReader(csv_file_1)
        reader_2 = csv.DictReader(csv_file_2)
        
        data1 = []
        data2 = []
        
        for row in reader_1:
            if row["Prompt"] == "FewShotCode" and row["Metric"] == "CodeBleu":
                if row["Value"]:
                    data1.append(float(row["Value"]))
        
        for row in reader_2:
            if row["Prompt"] == "ContextCode" and row["Metric"] == "CodeBleu":
                if row["Value"]:
                    data2.append(float(row["Value"]))

        stat, p_value_shapiro = shapiro(data2)

        print(len(data1))
        
        # Mann Whitney
        if p_value_shapiro < 0.05:
            stat_test = "Mann-Whitney"
            statistic, p_value = mannwhitneyu(data1, data2)
            print(f'Mann-Whitney U statistic: {statistic}')
            print(f'p-value: {p_value}')
        # T-test
        else:
            stat_test = "T-test"
            t_stat, p_value = ttest_ind(data1, data2)
            print("T-statistic:", t_stat)
            print("P-value:", p_value)


# Category should be either "Metric" or "Prompt" or "Refactoring method"
# If "Metric", subcategory can be: CodeBleu, Total CC, Total method calls or Total lines of code
# If "Prompt", subcategory can be: ZeroShotCode, FewShotCode, InstrucCode, ContextCode or RulesCode, BeforeRefact, AfterRefact
show_p_value(filepath1="./src/analysis/raw_data_gpt.csv",
               filepath2="./src/analysis/raw_data_gpt.csv",
               )