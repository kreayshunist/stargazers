# ⭐️ Stargazer Analytics

> Transform your GitHub stars into meaningful connections. Analyze, understand, and engage with your repository's stargazers.

## 🎯 What is this?

Stargazer Analytics helps you understand and connect with the developers who star your GitHub repositories. Instead of treating stars as just numbers, we help you discover the developers behind them.

## ✨ Features

- 🔍 **Deep Analysis**: Understand who's interested in your project
- 🎯 **Interest Discovery**: Find what other repos your stargazers love
- 📧 **Email Discovery**: Get emails of around 20% of your stargazers 
- 📊 **Smart Scoring**: Auto-score how well each stargazer fits your project
- 💌 **AI-Powered Intros**: Generate personalized outreach messages

## 🚀 Quick Start

### 1. Setup
In this repo search and replace `github.com/kreayshunist/stargazers` and `github.com/YOUR_USERNAME/stargazers` with your username.

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/stargazers.git
cd stargazers


# Initialize Go module
rm -rf go.mod go.sum
go mod init github.com/YOUR_USERNAME/stargazers && go mod tidy
go build
```


### 2. Configure GitHub Token
1. Visit GitHub.com → Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic)
3. Select scopes: `public_repo`, `read:user`
4. Copy your token

### 3. Choose Analysis Mode

You can run the tool in two modes:

#### Basic Mode -Information about your stargazers (Email Collection) 
```bash
# Only collect stargazer profiles and emails
./stargazers fetch --repo=OWNER/REPO --token=YOUR_TOKEN --mode=basic
```
- **Basic Mode** (--mode=basic):
  - Collects only stargazer profiles and emails
  - Faster execution
  - Lower API usage
  - Outputs to `emails/OWNER_REPO_emails.csv`
  - To scrap many repos, you can use [`competition_scraping.py`](competition_scraping.py) with a csv file containing the repo names.

#### Full Analysis Mode - Repository Correlation
```bash
# Full analysis including starred repos and contributions
./stargazers fetch --repo=OWNER/REPO --token=YOUR_TOKEN --mode=full
```

The modes automatically set the appropriate parameters:


- **Full Analysis Mode** (--mode=full):
  - Analyzes correlated repositories
  - Collects stargazer interests
  - Maps contribution patterns
  - Higher API usage
  - Provides complete analysis data
  

## 🛠 Advanced Options

```bash
Options:
  -r, --repo string        GitHub repository (format: owner/repo)
  -t, --token string       GitHub access token
  -c, --cache string       Cache directory (default: "./stargazer_cache")
  -m, --mode string        Analysis mode (default: "basic")
      --verbosity          Log level for verbose output
      --no-color          Disable colored output
```

### 5. Changing the code
If you change Go code, you need to recompile the program to make the changes effective. To do this do the initialization from above again:
```bash
go build
```

### 6. Analysis Tools

Run this to get csv from your cached profiles:
```bash
./stargazers analyze --repo=OWNER/REPO
````

Then you find the csvs in `./stargazer_cache/OWNER_REPO/`.


I drafted some scripts to analyze the data - but depending on your use case I advise you to just generate your own.
- **Data Visualization**: Plotting scripts in [`/utils`](utils)
- **Data cleaning**: In  `emails/OWNER_REPO_emails.csv` are all your stargazers. Around 20% should have emails. Filter them our.
- **Email Generation**: AI-powered personalized intro generator in [`/emails`](emails). Rank your leads by the score. I also recommend to filter by region (just add to the system prompt).

### 7. Email Sending Recommendations

For sending emails, I used Instantly. Do not send more than 30 emails per email address per day to avoid being flagged as spam.
1 email address cost there around 5 USD per month + 15 USD per year for the domain + 90 USD per month for the tool.

## 📊 Stats

- Scraped over 2 days 140k stargazers of related repos
- Got 20k unique email addresses with profiles
- Scored them between 0 and 1
- Started sending for top 1k emails
- 6% booked a 15 min call for user interviews

## 📝 Python Scripts

Several Python scripts are provided to enhance the functionality of Stargazer Analytics:

### Data Collection
- [`competition_scraping.py`](competition_scraping.py): Batch process multiple repositories listed in a CSV file.
  ```bash
  # Requirements: pandas
  # Usage: Provide GitHub token and path to CSV file containing repositories
  python competition_scraping.py --token=YOUR_GITHUB_TOKEN --repos-csv=repos.csv
  
  # The CSV file should have a "Repository" column with entries like "owner/repo"
  # Example repos.csv format:
  # Repository
  # openai/codex
  # bytedance/deer-flow
  # apple/ml-fastvlm
  ```

### Data Analysis and Visualization
- [`test_github_stats.py`](test_github_stats.py): Retrieve GitHub user statistics.
  ```bash
  # Requirements: requests, python-dotenv, tabulate
  # Setup: Create a .env file with GITHUB_TOKEN=your_token
  # Usage: Edit the usernames list in the script or use as a module
  python test_github_stats.py
  ```

- [`utils/competitor_plotting.py`](utils/competitor_plotting.py): Create visualizations for repository data.
  ```bash
  # Requirements: matplotlib, pandas
  # Usage: Edit cache_dir variable to point to your repository data
  python utils/competitor_plotting.py
  ```

- [`utils/get_stars.py`](utils/get_stars.py): Fetch current star counts and calculate correlation scores.
  ```bash
  # Requirements: requests, pandas, matplotlib, seaborn, python-dotenv
  # Setup: Create a .env file with GITHUB_TOKEN=your_token
  # Input: Reads from stargazer_cache/[owner]/[repo]/correlated_starred_repos.csv
  # Output: Creates output/repo_analysis.csv and output/repo_analysis.png
  python utils/get_stars.py
  ```

- [`utils/visulize_topics.py`](utils/visulize_topics.py): Generate network visualizations of repository tags/topics.
  ```bash
  # Requirements: matplotlib, seaborn, networkx
  # Input: Reads from output/repo-tags-all.json
  # Output: Creates various visualizations in the output/ directory
  python utils/visulize_topics.py
  ```

- [`utils/filter_data.py`](utils/filter_data.py): Clean and filter data from committer information.
  ```bash
  # Requirements: pandas
  # Usage: Edit input_file and output_file variables to point to your data
  python utils/filter_data.py
  ```

### Usage Workflow
1. First collect stargazer data using the Go tool:
   ```bash
   ./stargazers fetch --repo=OWNER/REPO --token=YOUR_TOKEN --mode=full
   ./stargazers analyze --repo=OWNER/REPO
   ```

2. For analyzing multiple repositories at once:
   ```bash
   # Create a CSV file with a "Repository" column
   python competition_scraping.py --token=YOUR_GITHUB_TOKEN --repos-csv=repos.csv
   ```

3. For repository correlation analysis:
   ```bash
   python utils/get_stars.py
   ```

4. For tag/topic network visualization:
   ```bash
   # First prepare the repo-tags-all.json file
   python utils/visulize_topics.py
   ```

5. For filtering committer data to extract emails:
   ```bash
   # Edit paths in the script first
   python utils/filter_data.py
   ```

## 📜 License

Big thanks to [spencerkimball](https://github.com/spencerkimball) for the initial implementation from 2019. 
I updated the code for the current api - and integrated everything around emails. 

Apache License 2.0 - See [LICENSE](LICENSE) for details

---

<p align="center">
Made with ❤️ for the open source community
</p>