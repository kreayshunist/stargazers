import pandas as pd

df = pd.read_csv("emails/all_competitors_filtered.csv")

# get the total number of tokens in the dataframe for gpt-4o
import tiktoken


def count_tokens(df: pd.DataFrame):
    encoding = tiktoken.encoding_for_model("gpt-4o")

    total_tokens = df.apply(
        lambda row: sum(len(encoding.encode(str(cell))) for cell in row)
    ).sum()  # type: ignore
    return total_tokens


print(f"Total number of tokens: {count_tokens(df)}")
