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
In this repo search and replace `github.com/magmueller/stargazers` and `github.com/YOUR_USERNAME/stargazers` with your username.

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

## 📜 License

Big thanks to [spencerkimball](https://github.com/spencerkimball) for the initial implementation from 2019. 
I updated the code for the current api - and integrated everything around emails. 

Apache License 2.0 - See [LICENSE](LICENSE) for details

---

<p align="center">
Made with ❤️ for the open source community
</p>
