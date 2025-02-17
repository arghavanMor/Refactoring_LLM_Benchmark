import matplotlib.pyplot as plt
import numpy as np

# Data points for the histograms
data = [
    (6, 6),
    (3, 3),
    (0, 3),
    (9, 15),
    (9, 21),
    (9, 9),
    (3, 3)
]

# Custom labels for each histogram
labels = [
    'INTRODUCE_EXPLAINING_VARIABLE',
    'INTRODUCE_ASSERTION',
    'ADD_PARAMETER',
    'CONSOLIDATE_COND_EXPRESSION',
    'CONSOLIDATE_DUPLICATE_COND_FRAGMENTS',
    'REPLACE_NESTED_COND_WITH_GUARD_CLAUSES',
    'INTRODUCE_NULL_OBJECT'
]

# Flatten the data to find the global min and max values
flat_data = [value for pair in data for value in pair]
min_value = min(flat_data)
max_value = max(flat_data)

# Normalize the data to range [0, 1]
normalized_data = [
    ((x - min_value) / (max_value - min_value), (y - min_value) / (max_value - min_value))
    for x, y in data
]

# Create a figure with subplots (7 histograms, arranged in 7 rows and 1 column)
fig, axes = plt.subplots(7, 1, figsize=(6, 12))  # 7 rows, 1 column

# Iterate through each normalized data point and create a histogram
for i, (x, y) in enumerate(normalized_data):
    axes[i].hist([x, y], bins=5, color='skyblue', edgecolor='black')  # You can adjust bins if needed
    axes[i].set_title(f"{labels[i]}")  # Use the custom label for the title
    axes[i].set_xlabel("Normalized Values")
    axes[i].set_ylabel("Frequency")

# Adjust layout to avoid overlap of titles/labels
plt.tight_layout()
plt.show()
