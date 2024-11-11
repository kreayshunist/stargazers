## stargazers

Analyze your GitHub repository's stargazers.

### Quick Start

1. **Fork & Clone**
   ```bash
   # Fork https://github.com/spencerkimball/stargazers first, then:
   git clone https://github.com/YOUR_USERNAME/stargazers.git
   cd stargazers
   ```


GitHub allows visitors to star a repo to bookmark it for later
perusal. Stars represent a casual interest in a repo, and when enough
of them accumulate, it's natural to wonder what's driving interest.
Stargazers attempts to get a handle on who these users are by finding
out what else they've starred, which other repositories they've
contributed to, and who's following them on GitHub.

Basic starting point:

1. List all stargazers
2. Fetch user info for each stargazer
3. For each stargazer, get list of starred repos & subscriptions
4. For each stargazer subscription, query the repo statistics to
   get additions / deletions & commit counts for that stargazer
5. Run analyses on stargazer data


2. **Initialize Module**
   ```bash
   rm -f go.mod go.sum
   go mod init github.com/YOUR_USERNAME/stargazers
   go mod tidy
   ```

3. **Get GitHub Token**
   - GitHub.com → Settings → Developer Settings → Personal Access Tokens
   - Generate new token (classic)
   - Select: `public_repo`, `read:user`
   - Copy token

4. Replace import in main.go
   In `main.go`, replace `YOUR_USERNAME` with your GitHub username.

   ```go
   import "github.com/YOUR_USERNAME/stargazers/cmd"
   ```


5. **Run**
   ```bash
   go build
   ./stargazers fetch --repo=OWNER/REPO --token=YOUR_TOKEN
   ```

### Options

```
      --alsologtostderr    logs at or above this threshold go to stderr (default NONE)
  -c, --cache string       directory for storing cached GitHub API responses (default "./stargazer_cache")
      --log-backtrace-at   when logging hits line file:N, emit a stack trace (default :0)
      --log-dir            if non-empty, write log files in this directory (default /var/folders/83/r_nmcwd969g5qc0b7my9wl900000gn/T/)
      --logtostderr        log to standard error instead of files (default true)
      --no-color           disable standard error log colorization
  -r, --repo string        GitHub owner and repository, formatted as :owner/:repo
  -t, --token string       GitHub access token for authorized rate limits
      --verbosity          log level for V logs
      --vmodule            comma-separated list of pattern=N settings for file-filtered logging
```
