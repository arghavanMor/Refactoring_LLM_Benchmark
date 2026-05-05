import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import json
from pathlib import Path
from scipy.stats import spearmanr

def corr_calculation():
    data_gpt = {
    "CodeBLEU": [0.558, 0.597, 0.589, 0.597, 0.521],
    "CC":        [5.986, 6.120, 6.008, 6.032, 5.825],
    "LOC":       [28.050, 26.981, 27.445, 25.163, 31.359],
    "FOUT":      [11.455, 10.753, 11.124, 10.599, 12.193],
    "Maint_new": [167.4, 149.0, 157.6, 158.6, 168.0],
    "Reliab_new":[3.6, 4.2, 9.0, 6.8, 5.6],
    "Maint_rem": [163.2, 151.2, 161.2, 164.8, 178.4],
    "Reliab_rem":[4.2, 8.4, 8.0, 7.4, 4.8],
    }

    """data_deep_seek = {
    "CodeBLEU":  [0.541, 0.534, 0.530, 0.534, 0.539],
    "CC":        [5.880, 6.115, 6.253, 6.009, 6.052],
    "LOC":       [31.803, 31.909, 32.018, 32.144, 27.957],
    "FOUT":      [11.370, 10.854, 11.217, 11.101, 11.544],
    "Maint_new": [98.4, 87.8, 84.0, 99.6, 91.0],
    "Reliab_new":[2.6, 2.8, 3.6, 4.0, 3.2],
    "Maint_rem": [93.4, 90.6, 82.2, 84.6, 94.8],
    "Reliab_rem":[3.6, 2.6, 2.2, 3.0, 3.0],
    }"""

    index = ["Zero-Shot", "Two-Shot", "Step-by-Step", "Rule-based", "Objective"]

    df = pd.DataFrame(data_gpt, index=index)

    corr = df.corr(method="pearson")

    print("Pearson Correlation Matrix:")
    print(corr.round(2).to_string())


    plt.figure(figsize=(9, 7))
    mask = np.zeros_like(corr, dtype=bool)

    sns.heatmap(corr,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    linewidths=0.5,
    linecolor="white",
    square=True,
    cbar_kws={"shrink": 0.8, "label": "Pearson r"},
    )

    plt.title("Feature Correlation Matrix", fontsize=13, pad=14)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.tight_layout()
    plt.savefig("correlation_heatmap_deep_seek.png", dpi=150)
    plt.show()

def complexity_tokens_corr():
    complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    with open(complexity_file_path, 'r') as file:
        data = json.load(file)

    # Build DataFrame, dropping entries with errors
    df = pd.DataFrame.from_dict({k: v for k, v in data.items() if 'error' not in v}, orient='index')

    print(f"\nShape: {df.shape}")

    # Pearson correlation
    pearson_r, pearson_p = stats.pearsonr(df['cyclomatic_complexity'], df['token_count'])
    print(f"\nPearson  r = {pearson_r:.4f}, p-value = {pearson_p:.4f}")

    # Spearman correlation (more robust to outliers)
    spearman_r, spearman_p = stats.spearmanr(df['cyclomatic_complexity'], df['token_count'])
    print(f"Spearman r = {spearman_r:.4f}, p-value = {spearman_p:.4f}")

def data_preprocessing(complexity_file_path):

    #complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    with open(complexity_file_path, 'r') as file:
        data = json.load(file)

    records = []
    for key, val in data.items():
        if 'error' in val:
            continue
        record = {
            'id': key,
            'cyclomatic_complexity': val['cyclomatic_complexity'],
            'token_count': val['token_count'],
        }
        # Flatten run scores for each model
        for model in ['chat_gpt_4o_mini', 'deep_seek']:
            if model in val:
                for run, score in val[model].items():
                    record[f'{model}_{run}'] = score
        records.append(record)

    df = pd.DataFrame(records).set_index('id')
    return df

def correlate(df, col_a, col_b):
    """Pearson and Spearman correlation between two columns, dropping NaNs."""
    temp = df[[col_a, col_b]].dropna()
    if len(temp) < 3:
        return None
    pearson_r,  pearson_p  = stats.pearsonr(temp[col_a], temp[col_b])
    spearman_r, spearman_p = stats.spearmanr(temp[col_a], temp[col_b])
    return {
        'col_a': col_a, 'col_b': col_b, 'n': len(temp),
        'pearson_r': round(pearson_r, 4),   'pearson_p': round(pearson_p, 4),
        'spearman_r': round(spearman_r, 4), 'spearman_p': round(spearman_p, 4),
    }

def correlation_caller():
    complexity_file_path = Path("src/Data/Data_collection_with_complexity_value.json")
    data = {
        "CodeBLEU":  [0.541, 0.534, 0.530, 0.534, 0.539],
        "CC":        [5.880, 6.115, 6.253, 6.009, 6.052],
        "LOC":       [31.803, 31.909, 32.018, 32.144, 27.957],
        "FOUT":      [11.370, 10.854, 11.217, 11.101, 11.544],
        "Maint_new": [98.4, 87.8, 84.0, 99.6, 91.0],
        "Reliab_new":[2.6, 2.8, 3.6, 4.0, 3.2],
        "Maint_rem": [93.4, 90.6, 82.2, 84.6, 94.8],
        "Reliab_rem":[3.6, 2.6, 2.2, 3.0, 3.0],
    }

    df = pd.DataFrame(data)

    corr, pvals = spearmanr(df)

    corr_df = pd.DataFrame(corr, index=df.columns, columns=df.columns)
    pval_df = pd.DataFrame(pvals, index=df.columns, columns=df.columns)

    print(corr_df.to_string())
    print(pval_df.to_string())

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Spearman Correlation Heatmap")
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    plt.show()

    return None

"""
# ── 6. Aggregated view: correlations with mean score per model ────────────────
for model in ['chat_gpt_4o_mini', 'deep_seek']:
    model_runs = [c for c in run_cols if model in c]
    if model_runs:
        df[f'{model}_mean'] = df[model_runs].mean(axis=1)

for mean_col in ['chat_gpt_4o_mini_mean', 'deep_seek_mean']:
    if mean_col in df.columns:
        results.append(correlate(df, 'cyclomatic_complexity', mean_col))
        results.append(correlate(df, 'token_count', mean_col))

mean_results = pd.DataFrame([r for r in results[-4:] if r is not None])
print("\nCorrelations with mean score per model:")
print(mean_results.to_string(index=False))
"""


if __name__ == '__main__':
    correlation_caller()