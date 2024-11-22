import os

import pandas as pd

df = pd.read_csv("emails/all_competitors_filtered.csv")

from openai import AzureOpenAI

client = AzureOpenAI(
    api_version="2024-10-21",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
    api_key=os.getenv("AZURE_OPENAI_KEY", ""),
)

n = 100

# split df into chunks of n rows
chunks = [df.iloc[i : i + n] for i in range(0, len(df), n)]
print(f"Number of chunks: {len(chunks)}")


def generate_personalized_intros(chunk):
    # drop email column
    chunk = chunk.drop(columns=["Email"])
    messages = [
        {
            "role": "system",
            "content": """
You are a professional cold email writer. Create short, friendly personalized email introductions to enrich my database. Your input is a a list with people i found on github in the format:
Login name,Name,Company,Location,Bio,repo(where i found them - they starred this repo) - some fields might be missing.
Output must be a JSON dictionary 
{
    "login name1": {"intro": "intro1", "score": 0.5},
    "login name2": {"intro": "intro2", "score": 0.3},
    ...
}
The login name is the key from the input.
The intro is the personalized message you write.
The score is how well they fit to my project. E.g. A super experienced person in web automation / scraping is 1, LLM agents is 0.9, only NLP is 0.3, no information is 0. If not advanced - deduct points. Be moderate. So that >0.8 are good leads.
The repo which they starred should not count into the score - they only starred this - this means nothing. Use only the bio and company.
My project is browser-use (no need to mention it in the intro - just for your context): We build the interface between LLMs and browsers. So that LLMs can understand the web and e.g. fix automation scripts which break otherwise when websites change.

I will continue your intro message with my own message: 
I am creator of the open-source project browser-use.
Would be cool to chat with you 15min about how we can use LLMs for web-automation.
link
Best Magnus

Rules:
- Keep each intro to 1 short sentence
- be direct
- Be professional but friendly
- Don't be salesy,
- if no information is provided, just write general short intro
- write things like Hi firstname, I saw you are working on ... on github. 
""",
        },
        {
            "role": "user",
            "content": f"""these are the people i found on github:
            {chunk.to_json(orient='records')}

""",
        },
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Parse JSON response (will be in format {username1: message1, username2: message2, ...})
        import json

        user_dict = json.loads(response.choices[0].message.content)
        # Map the messages back to the dataframe order
        intros_list = [
            user_dict.get(username, {}).get("intro", "") for username in chunk["Login"]
        ]
        scores_list = [
            user_dict.get(username, {}).get("score", 0) for username in chunk["Login"]
        ]
        actual_usernames_count = sum(1 for intro in intros_list if intro)

    except Exception as e:
        print(f"Error generating personalized intros: {e}")
        # fallback
        intros_list = []
        scores_list = [0] * len(chunk)
        actual_usernames_count = len(chunk)

        for i in range(len(chunk)):
            intros_list.append(f"Hi {chunk.iloc[i]['Name']}, I found you on GitHub.")

    print(f"Number of usernames with intros: {actual_usernames_count}/{len(chunk)}")
    return intros_list, scores_list


# Process each chunk and store results
checkpoint_file = "emails/checkpoint_intros.txt"
checkpoint_file_scores = "emails/checkpoint_scores.txt"
all_intros = []
all_scores = []
# read in files and continue
if os.path.exists(checkpoint_file):
    print(f"Resuming from checkpoint {checkpoint_file}")
    with open(checkpoint_file, "r") as f:
        all_intros = f.read().splitlines()
if os.path.exists(checkpoint_file_scores):
    print(f"Resuming from checkpoint {checkpoint_file_scores}")
    with open(checkpoint_file_scores, "r") as f:
        all_scores = f.read().splitlines()
assert len(all_intros) == len(all_scores), "Length of intros and scores must match"

l = len(all_intros)
print(f"Resuming from {l}")
for i, chunk in enumerate(chunks[l:]):
    print(f"Processing chunk {l+i+1}/{len(chunks)}")
    chunk_intros, chunk_scores = generate_personalized_intros(chunk)
    all_intros.extend(chunk_intros)
    all_scores.extend(chunk_scores)
    with open(checkpoint_file, "a") as f:
        f.write(f"{chunk_intros}\n")
    with open(checkpoint_file_scores, "a") as f:
        f.write(f"{chunk_scores}\n")


print(f"Length of all_intros: {len(all_intros)}")
print(f"Length of df: {len(df)}")
print(f"all_intros: {all_intros}")

# Ensure the length of all_intros matches the length of the dataframe
if len(all_intros) < len(df):
    all_intros.extend([""] * (len(df) - len(all_intros)))

elif len(all_intros) > len(df):
    raise ValueError(
        f"Length of values ({len(all_intros)}) exceeds length of index ({len(df)})"
    )
if len(all_scores) < len(df):
    all_scores.extend([0] * (len(df) - len(all_scores)))
elif len(all_scores) > len(df):
    raise ValueError(
        f"Length of values ({len(all_scores)}) exceeds length of index ({len(df)})"
    )
# Add intros to dataframe
df["personalized_intro"] = all_intros
df["personalized_intro_score"] = all_scores

# Save updated dataframe
df.to_csv("emails/all_competitors_with_intros.csv", index=False)
