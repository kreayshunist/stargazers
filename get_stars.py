# %%
# %% Imports and Setup
import os
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from dotenv import load_dotenv

# %%
# Either set this in your environment or replace with your token
# load from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_github_stars(repo):
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    # Only add token if it exists
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{repo}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()["stargazers_count"]
        elif response.status_code == 403:
            # Rate limit hit - print remaining time
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            current_time = int(time.time())
            wait_time = max(reset_time - current_time, 0)
            print(f"Rate limit exceeded for {repo}. Resets in {wait_time} seconds")
            # Return None or a default value
            return None
        elif response.status_code == 401:
            print(f"Authentication failed for {repo}. Check your token.")
            return None
        else:
            print(f"Error {response.status_code} for {repo}: {response.text}")
            return None

    except Exception as e:
        print(f"Exception for {repo}: {str(e)}")
        return None

    # Add delay between requests
    time.sleep(2)  # 2 second delay between requests


# %%
df = pd.read_csv("stargazer_cache/gregpr07/browser-use/correlated_starred_repos.csv")
# exlude browser-use
df = df[df["Repository"] != "gregpr07/browser-use"]
print(f"Analyzing {len(df)} repos")
# Get current stars for each repo
# %%
stars_list = []
for repo in df["Repository"]:
    stars = get_github_stars(repo)

    print(repo, stars)
    stars_list.append(stars if stars else 0)
    time.sleep(1)  # Respect GitHub API rate limits


# %%
# Add stars and calculate score
df["Current_Stars"] = stars_list
df["Score"] = (df["Count"] / df["Current_Stars"] * 100).round(2)

# Sort by score
df_sorted = df.sort_values("Score", ascending=False)

# Save to CSV

output_folder = "output"
Path(output_folder).mkdir(exist_ok=True)
output_file = f"{output_folder}/repo_analysis.csv"
df_sorted.to_csv(output_file, index=False)


# %% Visualization
# Set the style
plt.style.use("seaborn-v0_8-darkgrid")

sns.set_palette("husl")

# Create figure with higher DPI and better size ratio
fig = plt.figure(figsize=(20, 16), dpi=300)

# Scatter plot with enhanced styling
ax1 = plt.subplot(2, 1, 1)
scatter = plt.scatter(
    df_sorted["Current_Stars"],
    df_sorted["Count"],
    c=df_sorted["Score"],
    cmap="viridis",
    alpha=0.7,
    s=100,
    edgecolor="white",
    linewidth=0.5,
)

# Add colorbar with better formatting
cbar = plt.colorbar(scatter)
cbar.set_label(
    "Score how much (%) of their users starred us", fontsize=18, fontweight="bold"
)

# Enhance axes and title
plt.xlabel("Repository Stars", fontsize=18, fontweight="bold")
plt.ylabel("Users who starred both", fontsize=18, fontweight="bold")
plt.title(
    "Repository Analysis: Stars vs Related Count",
    fontsize=18,
    fontweight="bold",
    pad=20,
)

# Set scales and grid
plt.xscale("log")
plt.xticks([3e3, 5e3, 1e4, 25e3, 50e3, 1e5], ["3k", "5k", "10k", "25k", "50k", "100k"])
plt.grid(True, alpha=0.3)

# Add annotations for top 5 repositories
top_5 = df_sorted.head(10)
for _, repo in top_5.iterrows():
    plt.annotate(
        repo["Repository"].split("/")[-1],
        (repo["Current_Stars"], repo["Count"]),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=14,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7),
    )

# %% Bar Plot

# Increase the figure size for better readability
fig, ax2 = plt.subplots(figsize=(24, 18))
top_20 = df_sorted.head(20)

# Create barplot with custom colors
bars = sns.barplot(
    data=top_20, x="Score", y="Repository", palette="viridis", alpha=0.8, ax=ax2
)

# Enhance bar plot
plt.title("Top 20 Repositories by Score", fontsize=18, fontweight="bold", pad=20)
plt.xlabel(
    "Score how much (%) of their users starred us", fontsize=16, fontweight="bold"
)
plt.ylabel("Repository", fontsize=16, fontweight="bold")

# Add value labels on bars with number of correlated users and total stars
for i, (v, count, stars) in enumerate(
    zip(top_20["Score"], top_20["Count"], top_20["Current_Stars"])
):
    ax2.text(
        v + 0.1,
        i,
        f"{v:.1f}% ({count} / {stars})",
        va="center",
        fontsize=20,
        fontweight="bold",
    )

# Clean up repository names
ax2.set_yticklabels([repo.split("/")[-1] for repo in top_20["Repository"]], fontsize=20)

# Adjust layout and save
plt.tight_layout(pad=3.0)
plt.savefig(
    f"{output_folder}/repo_analysis.png",
    bbox_inches="tight",
    facecolor="white",
    edgecolor="none",
)

# %% Summary Statistics
print("\n" + "=" * 50)
print("Summary Statistics".center(50))
print("=" * 50 + "\n")

print(f"Total repositories analyzed: {len(df):,}")
print(f"Average correlation score: {df['Score'].mean():.2f}%")
print(f"Median correlation score: {df['Score'].median():.2f}%")
print(f"Standard deviation: {df['Score'].std():.2f}%")

print("\n" + "=" * 50)
print("Top 10 Repositories".center(50))
# %%
