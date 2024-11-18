# %% Category Analysis
import json
from collections import defaultdict

import numpy as np
import seaborn as sns

# Read the repo tags
with open("output/repo-tags-all.json", "r") as f:
    # with open("output/repo-tags-cleaned.json", "r") as f:
    content = f.read()
    # Convert Python dict syntax to JSON-compatible
    content = content.replace("'", '"').replace("#", "//")
    repos_data = eval(content)

# %% Prepare category data
categories = defaultdict(list)
all_tags = set()

for repo, data in repos_data.items():
    repo_name = repo.split("/")[-1]
    for tag in data["tags"]:
        categories[tag].append((repo_name, data["score"]))
        all_tags.add(tag)

# %% Tag Network Visualization

import matplotlib.pyplot as plt
import networkx as nx

# Create graph
G = nx.Graph()
output_folder = "output"

# Add nodes for repos and tags
for repo, data in repos_data.items():
    repo_name = repo.split("/")[-1]
    G.add_node(repo_name, type="repo", score=data["score"])
    for tag in data["tags"]:
        G.add_node(tag, type="tag")
        G.add_edge(repo_name, tag)

# Plot network
plt.figure(figsize=(20, 20))
pos = nx.spring_layout(G, k=1, iterations=50)

# Draw nodes
repo_nodes = [node for node, attr in G.nodes(data=True) if attr["type"] == "repo"]
tag_nodes = [node for node, attr in G.nodes(data=True) if attr["type"] == "tag"]

# Draw repos (size based on score)
scores = [
    G.nodes[node]["score"] if "score" in G.nodes[node] else 1 for node in repo_nodes
]
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=repo_nodes,
    node_color="lightblue",
    node_size=[s * 100 for s in scores],
    alpha=0.7,
)

# Draw tags
nx.draw_networkx_nodes(
    G, pos, nodelist=tag_nodes, node_color="lightgreen", node_size=2000, alpha=0.5
)

# Draw edges
nx.draw_networkx_edges(G, pos, alpha=0.2)

# Add labels
nx.draw_networkx_labels(G, pos, font_size=8)

plt.title("Repository and Tag Network", fontsize=16, pad=20)
plt.axis("off")
plt.savefig(f"{output_folder}/repo_network.png", bbox_inches="tight", dpi=300)

# %% Category Distribution
plt.figure(figsize=(15, 8))
category_counts = {cat: len(repos) for cat, repos in categories.items()}
sorted_categories = dict(
    sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
)

plt.bar(range(len(sorted_categories)), sorted_categories.values())
plt.xticks(
    range(len(sorted_categories)), sorted_categories.keys(), rotation=45, ha="right"
)
plt.title("Distribution of Repository Tags", fontsize=14, pad=20)
plt.xlabel("Tags")
plt.ylabel("Number of Repositories")
plt.tight_layout()
plt.savefig(f"{output_folder}/category_distribution.png", bbox_inches="tight", dpi=300)

# %% Score by Category
plt.figure(figsize=(15, 8))
category_scores = defaultdict(list)
for cat, repos in categories.items():
    category_scores[cat] = [score for _, score in repos]

# Create box plot
plt.boxplot(
    [scores for scores in category_scores.values()], labels=category_scores.keys()
)
plt.xticks(rotation=45, ha="right")
plt.title("Score Distribution by Tag", fontsize=14, pad=20)
plt.ylabel("Score")
plt.tight_layout()
plt.savefig(f"{output_folder}/category_scores.png", bbox_inches="tight", dpi=300)

# %% Heatmap of Tag Co-occurrence
# Create co-occurrence matrix
tags = list(all_tags)
cooccurrence = np.zeros((len(tags), len(tags)))

for repo, data in repos_data.items():
    repo_tags = data["tags"]
    for i, tag1 in enumerate(tags):
        for j, tag2 in enumerate(tags):
            if tag1 in repo_tags and tag2 in repo_tags:
                cooccurrence[i, j] += 1

plt.figure(figsize=(15, 15))
sns.heatmap(cooccurrence, xticklabels=tags, yticklabels=tags, cmap="viridis")
plt.title("Tag Co-occurrence Matrix", fontsize=14, pad=20)
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{output_folder}/tag_cooccurrence.png", bbox_inches="tight", dpi=300)

# %% Summary Statistics for Categories
print("\nCategory Analysis:")
print("=" * 50)
for category, repos in sorted(
    categories.items(), key=lambda x: len(x[1]), reverse=True
):
    scores = [score for _, score in repos]
    print(f"\n{category}:")
    print(f"Number of repos: {len(repos)}")
    print(f"Average score: {np.mean(scores):.2f}%")
    print(
        f"Top repos: {', '.join([repo for repo, _ in sorted(repos, key=lambda x: x[1], reverse=True)[:3]])}"
    )

# %%


# %% Category Analysis Setup
import json
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import LinearSegmentedColormap

# Custom color schemes
COLORS = {
    "background": "#ffffff",
    "text": "#2c3e50",
    "primary": "#3498db",
    "secondary": "#2ecc71",
    "accent": "#e74c3c",
    "grid": "#ecf0f1",
}

# Custom color map
custom_cmap = LinearSegmentedColormap.from_list(
    "custom", ["#3498db", "#2ecc71", "#e74c3c", "#f1c40f", "#9b59b6"]
)

# %% Load and prepare data
with open("output/repo-tags-all.json", "r") as f:
    content = f.read()
    content = content.replace("'", '"').replace("#", "//")
    repos_data = eval(content)

# Prepare category data
categories = defaultdict(list)
all_tags = set()

for repo, data in repos_data.items():
    repo_name = repo.split("/")[-1]
    for tag in data["tags"]:
        categories[tag].append((repo_name, data["score"]))
        all_tags.add(tag)

# %% Network Visualization
plt.style.use("seaborn-v0_8-whitegrid")
plt.figure(figsize=(24, 24), facecolor=COLORS["background"])

# Create and customize graph
G = nx.Graph()
for repo, data in repos_data.items():
    repo_name = repo.split("/")[-1]
    G.add_node(repo_name, type="repo", score=data["score"])
    for tag in data["tags"]:
        G.add_node(tag, type="tag")
        G.add_edge(repo_name, tag)

# Improved layout
pos = nx.spring_layout(G, k=2, iterations=50)

# Separate nodes by type
repo_nodes = [node for node, attr in G.nodes(data=True) if attr["type"] == "repo"]
tag_nodes = [node for node, attr in G.nodes(data=True) if attr["type"] == "tag"]

# Draw repos with improved visibility
scores = [
    G.nodes[node]["score"] * 200 if "score" in G.nodes[node] else 100
    for node in repo_nodes
]
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=repo_nodes,
    node_color="#3498db",
    node_size=scores,
    alpha=0.7,
    edgecolors="white",
    linewidths=2,
)

# Draw tags with better visibility
nx.draw_networkx_nodes(
    G,
    pos,
    nodelist=tag_nodes,
    node_color="#2ecc71",
    node_size=3000,
    alpha=0.5,
    edgecolors="white",
    linewidths=2,
)

# Draw edges with better styling
nx.draw_networkx_edges(G, pos, alpha=0.3, edge_color="#95a5a6", width=2)

# Improved labels
repo_labels = {node: node for node in repo_nodes}
tag_labels = {node: node for node in tag_nodes}

# Draw repo labels
nx.draw_networkx_labels(
    G, pos, repo_labels, font_size=10, font_weight="bold", font_color=COLORS["text"]
)

# Draw tag labels
nx.draw_networkx_labels(
    G, pos, tag_labels, font_size=12, font_weight="bold", font_color="#27ae60"
)

plt.title(
    "Repository and Tag Network",
    fontsize=20,
    pad=20,
    color=COLORS["text"],
    fontweight="bold",
)
plt.axis("off")
plt.savefig(
    f"{output_folder}/repo_network.png",
    bbox_inches="tight",
    dpi=300,
    facecolor=COLORS["background"],
)

# %% Category Distribution with improved styling
plt.figure(figsize=(20, 10), facecolor=COLORS["background"])
category_counts = {cat: len(repos) for cat, repos in categories.items()}
sorted_categories = dict(
    sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
)

# Create bars with custom styling
bars = plt.bar(
    range(len(sorted_categories)),
    sorted_categories.values(),
    color=custom_cmap(np.linspace(0, 1, len(sorted_categories))),
)

# Customize appearance
plt.xticks(
    range(len(sorted_categories)),
    sorted_categories.keys(),
    rotation=45,
    ha="right",
    fontsize=12,
)
plt.title(
    "Distribution of Repository Tags",
    fontsize=18,
    pad=20,
    color=COLORS["text"],
    fontweight="bold",
)
plt.xlabel("Tags", fontsize=14, color=COLORS["text"])
plt.ylabel("Number of Repositories", fontsize=14, color=COLORS["text"])

# Add value labels on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{int(height)}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    f"{output_folder}/category_distribution.png",
    bbox_inches="tight",
    dpi=300,
    facecolor=COLORS["background"],
)

# %% Tag Co-occurrence Heatmap with improved visibility
tags = list(all_tags)
cooccurrence = np.zeros((len(tags), len(tags)))

for repo, data in repos_data.items():
    repo_tags = data["tags"]
    for i, tag1 in enumerate(tags):
        for j, tag2 in enumerate(tags):
            if tag1 in repo_tags and tag2 in repo_tags:
                cooccurrence[i, j] += 1

plt.figure(figsize=(20, 16), facecolor=COLORS["background"])
mask = np.triu(np.ones_like(cooccurrence, dtype=bool))
sns.heatmap(
    cooccurrence,
    xticklabels=tags,
    yticklabels=tags,
    cmap="viridis",
    mask=mask,
    annot=True,
    fmt="g",
    cbar_kws={"label": "Number of Co-occurrences"},
    square=True,
)

plt.title(
    "Tag Co-occurrence Matrix",
    fontsize=18,
    pad=20,
    color=COLORS["text"],
    fontweight="bold",
)
plt.xticks(rotation=45, ha="right", fontsize=12)
plt.yticks(rotation=0, fontsize=12)
plt.tight_layout()
plt.savefig(
    f"{output_folder}/tag_cooccurrence.png",
    bbox_inches="tight",
    dpi=300,
    facecolor=COLORS["background"],
)

# %% Print Category Analysis with improved formatting
print("\n" + "=" * 80)
print("Category Analysis Summary".center(80))
print("=" * 80 + "\n")

for category, repos in sorted(
    categories.items(), key=lambda x: len(x[1]), reverse=True
):
    scores = [score for _, score in repos]
    print(f"\n🏷️  {category}")
    print("-" * 40)
    print(f"📊 Number of repos: {len(repos)}")
    print(f"⭐ Average score: {np.mean(scores):.2f}%")
    top_repos = sorted(repos, key=lambda x: x[1], reverse=True)[:3]
    print(f"🏆 Top repos:")
    for repo, score in top_repos:
        print(f"   • {repo} ({score:.2f}%)")
