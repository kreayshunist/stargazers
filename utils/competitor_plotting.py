import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Create plots directory
plots_dir = "stargazer_analysis"
os.makedirs(plots_dir, exist_ok=True)

# Read CSV files
cache_dir = "stargazer_cache/gregpr07/browser-use"
files = {
    "committers": pd.read_csv(f"{cache_dir}/committers.csv"),
    "followers": pd.read_csv(f"{cache_dir}/followers.csv"),
    "cumulative_stars": pd.read_csv(f"{cache_dir}/cumulative_stars.csv"),
    "correlated_starred": pd.read_csv(f"{cache_dir}/correlated_starred_repos.csv"),
    "correlated_starred_hist": pd.read_csv(
        f"{cache_dir}/correlated_starred_repos_hist.csv"
    ),
}

# Debug: Print available columns
print("\nAvailable columns in cumulative_stars.csv:")
print(files["cumulative_stars"].columns)

# Set global plot style
plt.style.use("default")
plt.rcParams["figure.figsize"] = [12, 6]
plt.rcParams["font.size"] = 10


def save_plot(name):
    plt.tight_layout()
    plt.savefig(f"{plots_dir}/{name}.png", dpi=300, bbox_inches="tight")
    plt.close()


# 1. Committer Analysis
print("\n=== Committer Analysis ===")
committers = files["committers"]
committers_with_email = committers[["Login", "Email"]].dropna()
print(f"Committers with email ({len(committers_with_email)}):")
print(committers_with_email)

# Plot top committers
plt.figure()
commit_data = committers.sort_values("Commits", ascending=True).tail(10)
plt.barh(commit_data["Login"], commit_data["Commits"])
plt.title("Top 10 Contributors by Commit Count")
plt.xlabel("Number of Commits")
save_plot("top_contributors")

# Plot commits vs additions
plt.figure()
plt.scatter(committers["Commits"], committers["Additions"], alpha=0.5)
plt.xlabel("Number of Commits")
plt.ylabel("Number of Additions")
plt.title("Commits vs Additions")
save_plot("commits_vs_additions")

# 2. Follower Analysis
followers = files["followers"]
plt.figure()
follower_counts = followers["Followers"].value_counts().sort_index()
plt.plot(follower_counts.index, follower_counts.values, marker="o")
plt.title("Distribution of Follower Counts")
plt.xlabel("Number of Followers")
plt.ylabel("Frequency")
save_plot("follower_distribution")

# 3. Stars Analysis
stars_data = files["cumulative_stars"]
# Assuming the column might be named differently
star_column = "stars" if "stars" in stars_data.columns else "Stars"
date_column = "date" if "date" in stars_data.columns else "Date"

if star_column in stars_data.columns and date_column in stars_data.columns:
    plt.figure()
    plt.plot(
        pd.to_datetime(stars_data[date_column]), stars_data[star_column], marker="."
    )
    plt.title("Cumulative Stars Over Time")
    plt.xlabel("Date")
    plt.ylabel("Total Stars")
    plt.xticks(rotation=45)
    save_plot("stars_growth")

    # Calculate star growth rate
    stars_data["StarGrowth"] = stars_data[star_column].diff()
    plt.figure()
    plt.plot(
        pd.to_datetime(stars_data[date_column]), stars_data["StarGrowth"], marker="."
    )
    plt.title("Star Growth Rate")
    plt.xlabel("Date")
    plt.ylabel("New Stars per Day")
    plt.xticks(rotation=45)
    save_plot("star_growth_rate")

# 4. Repository Correlations
# Repositories to ignore
ignore_repos = ["browser-use", "magmueller/stargazers"]

# Filter out ignored repositories
correlated = files["correlated_starred"]
correlated = correlated[
    ~correlated["Repository"].str.contains("|".join(ignore_repos), case=False)
]

# Plot top 20 correlated repositories
plt.figure(figsize=(15, 8))
top_20_repos = correlated.sort_values("Count", ascending=True).tail(20)
plt.barh(top_20_repos["Repository"], top_20_repos["Count"])
plt.title("Top 20 Correlated Repositories (Excluding Self)")
plt.xlabel("Count")
save_plot("top_correlated_repos")

# Print top correlations
print("\n=== Top 10 Correlated Repositories ===")
print(top_20_repos[["Repository", "Count"]].tail(10).to_string())

# Save summary
with open(f"{plots_dir}/repo_correlations.txt", "w") as f:
    f.write("=== Repository Correlation Analysis ===\n\n")
    f.write("Top 20 Correlated Repositories:\n")
    for _, repo in top_20_repos.iterrows():
        f.write(f"{repo['Repository']}: {repo['Count']} shared stars\n")

print(f"\nAnalysis complete! Check the '{plots_dir}' directory for results.")
