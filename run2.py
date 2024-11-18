import pandas as pd

# Read followers data
followers_df = pd.read_csv("stargazer_cache/gregpr07/browser-use/followers.csv")

# Create clean one-line format for each profile
with open("stargazers_list.txt", "w", encoding="utf-8") as f:
    f.write("USERNAME - COMPANY - LOCATION - FOLLOWERS\n")
    f.write("-" * 60 + "\n")

    for _, p in followers_df.iterrows():
        line = (
            f"{p['Login']} - "
            f"{p['Company'] if pd.notna(p['Company']) else 'N/A'} - "
            f"{p['Location'] if pd.notna(p['Location']) else 'N/A'} - "
            f"{p['Followers']}\n"
        )
        f.write(line)

print("Saved to stargazers_list.txt")
