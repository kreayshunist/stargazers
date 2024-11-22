data_dir = "email_reachout"


# read all csv files in data_dir and combine them into a single dataframe each gets a column for the repo name and ownder (seperated by _) without the _emails.csv suffix
import os
import re

import pandas as pd


def combine_csv_files(data_dir: str, output_file: str):
    # List to hold dataframes
    dfs = []

    # Iterate over all files in the data directory
    for filename in os.listdir(data_dir):
        if filename.endswith("_emails.csv"):
            # Read the CSV file into a dataframe
            df = pd.read_csv(os.path.join(data_dir, filename))

            # Extract repo name and owner from the filename
            repo_owner = filename.replace("_emails.csv", "")

            owner, repo = repo_owner.split("_")
            # Add a new column for repo name and owner
            df["repo"] = repo
            df["owner"] = owner

            # Append the dataframe to the list
            dfs.append(df)

    # Combine all dataframes into a single dataframe
    combined_df = pd.concat(dfs, ignore_index=True)

    # Save to csv
    combined_df.to_csv(output_file, index=False)
    return combined_df


def clean_text(text: str):
    if pd.isna(text) or not isinstance(text, str):
        return text
    # Replace newlines with spaces and collapse multiple spaces into one
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned


def filter_data(df: pd.DataFrame, output_file: str):
    # Clean all string columns
    for column in df.columns:
        df[column] = df[column].apply(clean_text)

    # Filter out empty emails and duplicates
    df = df[df["Email"].notna()]
    df = df[df["Email"] != ""]
    df = df.drop_duplicates()

    # remove duplicate emails
    df = df.drop_duplicates(subset=["Email"])
    # remove columns Following and Followers and owner
    df = df.drop(columns=["Following", "Followers", "owner"])

    # Save to CSV with proper line endings
    df.to_csv(output_file, index=False, lineterminator="\n")
    return df


def count_duplicate_emails(df: pd.DataFrame):
    return df.duplicated(subset=["Email"]).sum()


data_dir = "email_reachout"
output_dir = "emails"
combined_df = combine_csv_files(data_dir, os.path.join(output_dir, "all.csv"))
df = filter_data(combined_df, os.path.join(output_dir, "all_competitors_filtered.csv"))
print(count_duplicate_emails(df))
