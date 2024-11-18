import pandas as pd


def clean_committers_data(input_file, output_file):
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Remove rows where Email is empty or null
    df_clean = df.dropna(subset=["Email"])

    # Remove rows where Email is an empty string
    df_clean = df_clean[df_clean["Email"] != ""]

    # Keep only Login and Email columns
    df_clean = df_clean[["Login", "Email"]]

    # Save to new CSV file
    df_clean.to_csv(output_file, index=False)

    print(f"Original rows: {len(df)}")
    print(f"Rows after cleaning: {len(df_clean)}")


if __name__ == "__main__":
    input_file = "/Users/magnus/Developer/stargazers/stargazer_cache/gregpr07/browser-use/committers_clean.csv"
    output_file = "/Users/magnus/Developer/stargazers/stargazer_cache/gregpr07/browser-use/committers_clean_filtered.csv"

    clean_committers_data(input_file, output_file)
