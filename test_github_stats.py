import os
from typing import Dict, List, TypedDict

import requests
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()


class QuickStats(TypedDict):
    username: str
    contributions_last_year: int
    followers: int


class UserStats(TypedDict):
    username: str
    commit_contributions: int
    contributions_last_year: int
    all_time_contributions: int
    repository_commits: int
    public_repos: int
    followers: int
    pull_requests: int
    issues: int
    stars_received: int


def get_quick_stats(username: str) -> QuickStats:
    """Get only last year's contributions and followers count. Much faster than full stats."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # GraphQL endpoint
    url = "https://api.github.com/graphql"

    # Lightweight query for just contributions and followers
    query = """
    query($username: String!) {
      user(login: $username) {
        followers {
          totalCount
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """

    variables: Dict[str, str] = {"username": username}

    print(f"\nFetching quick stats for user: {username}", end="", flush=True)
    response = requests.post(
        url, headers=headers, json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"\nError: {data['errors']}")
            return {"username": username, "contributions_last_year": 0, "followers": 0}

        user_data = data["data"]["user"]
        if user_data:
            print(" ✓")
            return {
                "username": username,
                "contributions_last_year": user_data["contributionsCollection"][
                    "contributionCalendar"
                ]["totalContributions"],
                "followers": user_data["followers"]["totalCount"],
            }

    print(f"\nError: {response.status_code}")
    print(response.text)
    return {"username": username, "contributions_last_year": 0, "followers": 0}


def display_quick_stats_table(stats: List[QuickStats]) -> None:
    """Display the quick GitHub statistics in a table."""
    headers = ["Username", "Last Year Contrib.", "Followers"]

    table_data = [
        [stat["username"], stat["contributions_last_year"], stat["followers"]]
        for stat in stats
    ]

    print("\nGitHub Quick Statistics (Last Year):")
    print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="right"))


def get_github_user_stats(username: str) -> UserStats:
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # GraphQL endpoint
    url = "https://api.github.com/graphql"

    # GraphQL query to get contribution data
    query = """
    query($username: String!) {
      user(login: $username) {
        name
        followers {
          totalCount
        }
        pullRequests {
          totalCount
        }
        issues {
          totalCount
        }
        publicRepos: repositories(privacy: PUBLIC, ownerAffiliations: OWNER) {
          totalCount
        }
        # Get all contributions
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoryContributions
          contributionCalendar {
            totalContributions
          }
        }
        topRepositories: repositories(
          first: 1000,
          ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
          orderBy: {field: STARGAZERS, direction: DESC}
        ) {
          nodes {
            name
            stargazerCount
            defaultBranchRef {
              target {
                ... on Commit {
                  history {
                    totalCount
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    variables: Dict[str, str] = {"username": username}

    print(f"\nFetching stats for user: {username}", end="", flush=True)
    response = requests.post(
        url, headers=headers, json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"\nError: {data['errors']}")
            return {
                "username": username,
                "commit_contributions": 0,
                "contributions_last_year": 0,
                "all_time_contributions": 0,
                "repository_commits": 0,
                "public_repos": 0,
                "followers": 0,
                "pull_requests": 0,
                "issues": 0,
                "stars_received": 0,
            }

        user_data = data["data"]["user"]
        if user_data:
            contributions = user_data["contributionsCollection"]

            # Calculate total commits and stars across repositories
            total_repo_commits = 0
            total_stars = 0
            for repo in user_data["topRepositories"]["nodes"]:
                if repo["defaultBranchRef"] and repo["defaultBranchRef"]["target"]:
                    total_repo_commits += repo["defaultBranchRef"]["target"]["history"][
                        "totalCount"
                    ]
                total_stars += repo.get("stargazerCount", 0)

            # Calculate all-time contributions
            all_time_total = (
                contributions["totalCommitContributions"]
                + contributions["totalIssueContributions"]
                + contributions["totalPullRequestContributions"]
                + contributions["totalPullRequestReviewContributions"]
                + contributions["totalRepositoryContributions"]
            )

            print(" ✓")  # Checkmark to indicate successful fetch

            return {
                "username": username,
                "commit_contributions": contributions["totalCommitContributions"],
                "contributions_last_year": contributions["contributionCalendar"][
                    "totalContributions"
                ],
                "all_time_contributions": all_time_total,
                "repository_commits": total_repo_commits,
                "public_repos": user_data["publicRepos"]["totalCount"],
                "followers": user_data["followers"]["totalCount"],
                "pull_requests": user_data["pullRequests"]["totalCount"],
                "issues": user_data["issues"]["totalCount"],
                "stars_received": total_stars,
            }
    else:
        print(f"\nError: {response.status_code}")
        print(response.text)
        return {
            "username": username,
            "commit_contributions": 0,
            "contributions_last_year": 0,
            "all_time_contributions": 0,
            "repository_commits": 0,
            "public_repos": 0,
            "followers": 0,
            "pull_requests": 0,
            "issues": 0,
            "stars_received": 0,
        }


def display_stats_table(stats: List[UserStats]) -> None:
    """Display the GitHub statistics in a formatted table."""
    headers = [
        "Username",
        "Direct Commits",
        "Last Year Contrib.",
        "All Time Contrib.",
        "Repo Commits",
        "Public Repos",
        "Followers",
        "PRs",
        "Issues",
        "Stars",
    ]

    table_data = [
        [
            stat["username"],
            stat["commit_contributions"],
            stat["contributions_last_year"],
            stat["all_time_contributions"],
            stat["repository_commits"],
            stat["public_repos"],
            stat["followers"],
            stat["pull_requests"],
            stat["issues"],
            stat["stars_received"],
        ]
        for stat in stats
    ]

    print("\nGitHub User Statistics:")
    print(tabulate(table_data, headers=headers, tablefmt="grid", numalign="right"))


# Example usage
usernames = ["jnsdrssn", "gregpr07", "magmueller", "duplxey", "maticzav"]

# Quick stats only
print("\nGathering quick statistics...")
quick_stats: List[QuickStats] = []
for username in usernames:
    stats = get_quick_stats(username)
    quick_stats.append(stats)
display_quick_stats_table(quick_stats)

# Uncomment below for full detailed stats
"""
print("\nGathering detailed statistics...")
all_stats: List[UserStats] = []
for username in usernames:
    stats = get_github_user_stats(username)
    all_stats.append(stats)
display_stats_table(all_stats)
"""
