import os
import subprocess
import argparse
from pathlib import Path

import pandas as pd


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape GitHub repository data.')
    parser.add_argument('--token', required=True, help='GitHub API token')
    parser.add_argument('--repos-csv', required=True, help='Path to CSV file containing repositories to scrape')
    args = parser.parse_args()
    
    github_token = args.token

    # Read the repos CSV
    df = pd.read_csv(args.repos_csv)

    # Create cache directory if it doesn't exist
    Path("stargazer_cache").mkdir(exist_ok=True)
    Path("email_reachout").mkdir(exist_ok=True)

    # First build the stargazers binary
    build_cmd = ["go", "build"]
    subprocess.run(build_cmd, check=True)

    # Process each repository
    for _, row in df.iterrows():
        repo = row["Repository"]
        print(f"\nProcessing {repo}...")

        try:
            # Run the stargazers command using the built binary
            cmd = [
                "./stargazers",
                "fetch",
                f"--repo={repo}",
                f"--token={github_token}",
                "--cache=./stargazer_cache",
                "--mode=basic",
            ]

            print(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )

            if result.returncode != 0:
                print(f"Error processing {repo} (exit code {result.returncode})")
            else:
                print(f"Successfully processed {repo}")

        except Exception as e:
            print(f"Failed to process {repo}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
