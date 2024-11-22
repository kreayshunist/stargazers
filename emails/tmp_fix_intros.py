# %%
import ast

import pandas as pd

folder = ""
data = pd.read_csv(f"{folder}all_competitors_with_intros.csv")

intro_file = f"{folder}checkpoint_intros.txt"
scores_file = f"{folder}checkpoint_scores.txt"

# Read and parse intros
with open(intro_file, "r") as f:
    intro_chunks = f.read().splitlines()

# Combine all intro chunks
all_intros = []
for chunk in intro_chunks:
    try:
        # Remove truncation and parse using ast.literal_eval
        clean_chunk = chunk.split("...(line too long")[0]
        intro_list = ast.literal_eval(clean_chunk)
        all_intros.extend(intro_list)
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing intro chunk: {e}")
        continue

# Read and parse scores
with open(scores_file, "r") as f:
    score_chunks = f.read().splitlines()

# Combine all score chunks
all_scores = []
for chunk in score_chunks:
    try:
        # Remove truncation and parse using ast.literal_eval
        clean_chunk = chunk.split("...(line too long")[0]
        score_list = ast.literal_eval(clean_chunk)
        all_scores.extend(score_list)
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing score chunk: {e}")
        continue

# Verify lengths
print(f"Total intros: {len(all_intros)}")
print(f"Total scores: {len(all_scores)}")
assert len(all_intros) == len(
    all_scores
), f"Length mismatch: intros ({len(all_intros)}) vs scores ({len(all_scores)})"
assert len(all_intros) == len(
    data
), f"Data length mismatch: items ({len(all_intros)}) vs DataFrame ({len(data)})"

# Update DataFrame
data["personalized_intro"] = all_intros
data["personalized_intro_score"] = all_scores

# %%
data.head()

# %% sort by score
data = data.sort_values(by="personalized_intro_score", ascending=False)

# %%
data.head()

# split everything above 0.5 score and save into 2 files
threshold = 0.35
data_high = data[data["personalized_intro_score"] > threshold]
data_low = data[data["personalized_intro_score"] <= threshold]
print(f"Length of high: {len(data_high)}")
print(f"Length of low: {len(data_low)}")
# %%
data_high.to_csv(f"{folder}all_competitors_with_intros_high.csv", index=False)
data_low.to_csv(f"{folder}all_competitors_with_intros_low.csv", index=False)

# %%
