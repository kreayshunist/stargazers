import os
import subprocess
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise ValueError("GITHUB_TOKEN not found in .env file")

    # Read the repos CSV
    df = pd.read_csv("output/repo_to_scrap.csv")

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
            ]

            print(f"Running command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )

            # Print output in real-time
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)

            if result.returncode != 0:
                print(f"Error processing {repo} (exit code {result.returncode})")
            else:
                print(f"Successfully processed {repo}")

        except Exception as e:
            print(f"Failed to process {repo}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
