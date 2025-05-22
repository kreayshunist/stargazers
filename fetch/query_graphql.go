// Copyright 2016 The Cockroach Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
// implied. See the License for the specific language governing
// permissions and limitations under the License.

package fetch

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// QueryAllGraphQL recursively fetches GitHub data using GraphQL API
func QueryAllGraphQL(c *Context) error {
	// Set the thresholds based on mode
	if c.Mode == "basic" {
		maxStarredVal = 0
		maxSubscribedVal = 0
		minStargazersVal = 0
		minForksVal = 0
		minOpenIssuesVal = 0
	} else {
		maxStarredVal = 100
		maxSubscribedVal = 100
		minStargazersVal = 300
		minForksVal = 30
		minOpenIssuesVal = 3
	}

	client := NewGraphQLClientWithCache(c.Token, c)

	// Query all stargazers for the repo
	sg, err := QueryStargazersGraphQL(c, client)
	if err != nil {
		return err
	}

	// Save user info to CSV (already collected in stargazers query)
	if err = SaveUserInfoCSV(c, sg); err != nil {
		return err
	}

	// Unique map of repos by repo full name
	rs := map[string]*Repo{}

	// Only run these queries in full mode
	if c.Mode == "full" {
		if err = QueryFollowersGraphQL(c, client, sg); err != nil {
			return err
		}
		if err = QueryUserRepositoriesGraphQL(c, client, sg, rs); err != nil {
			return err
		}
		if err = QueryContributionsGraphQL(c, client, sg, rs); err != nil {
			return err
		}
		return SaveState(c, sg, rs)
	}

	// For basic mode, just save what we have
	return SaveState(c, sg, map[string]*Repo{})
}

// QueryStargazersGraphQL queries the repo's stargazers using GraphQL
func QueryStargazersGraphQL(c *Context, client *GraphQLClientWithCache) ([]*Stargazer, error) {
	fmt.Printf("DEBUG: QueryStargazersGraphQL\n")
	log.Printf("querying stargazers of repository %s using GraphQL", c.Repo)

	parts := strings.Split(c.Repo, "/")
	if len(parts) != 2 {
		return nil, fmt.Errorf("invalid repository format: %s", c.Repo)
	}
	owner, name := parts[0], parts[1]

	stargazers := []*Stargazer{}
	cursor := ""
	pageSize := 100

	fmt.Printf("*** 0 stargazers")

	for {
		variables := map[string]interface{}{
			"owner": owner,
			"name":  name,
			"first": pageSize,
		}
		if cursor != "" {
			variables["cursor"] = cursor
		}

		var response StargazersResponse
		err := client.ExecuteWithCache(StargazersQuery, variables, &response)
		if err != nil {
			return nil, fmt.Errorf("failed to execute stargazers query: %w", err)
		}

		// Convert GraphQL response to Stargazer structs
		for _, edge := range response.Repository.Stargazers.Edges {
			user := User{
				Login:       edge.Node.Login,
				Name:        edge.Node.Name,
				Email:       edge.Node.Email,
				Company:     edge.Node.Company,
				Location:    edge.Node.Location,
				Bio:         edge.Node.Bio,
				AvatarURL:   edge.Node.AvatarURL,
				URL:         edge.Node.URL,
				Followers:   edge.Node.Followers.TotalCount,
				Following:   edge.Node.Following.TotalCount,
				CreatedAt:   edge.Node.CreatedAt,
				UpdatedAt:   edge.Node.UpdatedAt,
			}

			stargazer := &Stargazer{
				User:      user,
				StarredAt: edge.StarredAt,
			}
			stargazers = append(stargazers, stargazer)
		}

		fmt.Printf("\r*** %d stargazers", len(stargazers))

		if !response.Repository.Stargazers.PageInfo.HasNextPage {
			break
		}
		cursor = response.Repository.Stargazers.PageInfo.EndCursor
	}

	fmt.Printf("\n")
	return stargazers, nil
}

// SaveUserInfoCSV saves user information to CSV (data already collected from stargazers query)
func SaveUserInfoCSV(c *Context, sg []*Stargazer) error {
	log.Printf("saving user info for %s stargazers to CSV...", format(len(sg)))

	// Create CSV file with repo name
	repoName := strings.Replace(c.Repo, "/", "_", -1)
	csvPath := filepath.Join("emails", repoName+"_emails.csv")

	// Create emails directory if it doesn't exist
	if err := os.MkdirAll("emails", 0755); err != nil {
		return err
	}

	file, err := os.Create(csvPath)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	// Write header
	header := []string{"Login", "Email", "Name", "Company", "Location", "Bio", "Followers", "Following"}
	if err := writer.Write(header); err != nil {
		return err
	}

	for _, s := range sg {
		row := []string{
			s.User.Login,
			s.User.Email,
			s.User.Name,
			s.User.Company,
			s.User.Location,
			s.User.Bio,
			strconv.Itoa(s.User.Followers),
			strconv.Itoa(s.User.Following),
		}
		if err := writer.Write(row); err != nil {
			return err
		}
	}

	fmt.Printf("*** saved user info for %s stargazers to %s\n", format(len(sg)), csvPath)
	return nil
}

// QueryFollowersGraphQL queries followers for each stargazer using GraphQL
func QueryFollowersGraphQL(c *Context, client *GraphQLClientWithCache, sg []*Stargazer) error {
	log.Printf("querying followers for each of %s stargazers using GraphQL...", format(len(sg)))
	total := 0
	fmt.Printf("*** 0 followers for 0 stargazers")
	uniqueFollowers := map[string]struct{}{}

	for i, s := range sg {
		cursor := ""
		pageSize := 100

		for {
			variables := map[string]interface{}{
				"login": s.Login,
				"first": pageSize,
			}
			if cursor != "" {
				variables["cursor"] = cursor
			}

			var response FollowersResponse
			err := client.ExecuteWithCache(FollowersQuery, variables, &response)
			if err != nil {
				log.Printf("failed to fetch followers for %s: %v", s.Login, err)
				break // Continue to next user if one fails
			}

			// Convert to User structs
			for _, node := range response.User.Followers.Nodes {
				user := &User{
					Login:     node.Login,
					Name:      node.Name,
					Email:     node.Email,
					AvatarURL: node.AvatarURL,
					URL:       node.URL,
				}
				uniqueFollowers[user.Login] = struct{}{}
				s.Followers = append(s.Followers, user)
				total++
			}

			fmt.Printf("\r*** %s followers (%s unique) for %s stargazers",
				format(total), format(len(uniqueFollowers)), format(i+1))

			if !response.User.Followers.PageInfo.HasNextPage {
				break
			}
			cursor = response.User.Followers.PageInfo.EndCursor
		}
	}
	fmt.Printf("\n")
	return nil
}

// QueryUserRepositoriesGraphQL queries starred and watched repos for each stargazer
func QueryUserRepositoriesGraphQL(c *Context, client *GraphQLClientWithCache, sg []*Stargazer, rs map[string]*Repo) error {
	log.Printf("querying starred and watched repos for %s stargazers using GraphQL...", format(len(sg)))

	// Process users in batches to optimize API calls
	batchSize := 50
	for i := 0; i < len(sg); i += batchSize {
		end := i + batchSize
		if end > len(sg) {
			end = len(sg)
		}

		batch := sg[i:end]
		logins := make([]string, len(batch))
		for j, s := range batch {
			logins[j] = s.Login
		}

		variables := map[string]interface{}{
			"logins": logins,
		}

		var response UsersDetailResponse
		err := client.ExecuteWithCache(UsersDetailQuery, variables, &response)
		if err != nil {
			log.Printf("failed to fetch user details for batch %d: %v", i/batchSize, err)
			continue
		}

		// Map responses back to stargazers
		for _, node := range response.Nodes {
			// Find the corresponding stargazer
			var stargazer *Stargazer
			for _, s := range batch {
				if s.Login == node.Login {
					stargazer = s
					break
				}
			}
			if stargazer == nil {
				continue
			}

			// Process starred repositories
			for _, repo := range node.StarredRepositories.Nodes {
				if len(stargazer.Starred) >= maxStarred {
					break
				}
				stargazer.Starred = append(stargazer.Starred, repo.NameWithOwner)
				
				if _, ok := rs[repo.NameWithOwner]; !ok {
					rs[repo.NameWithOwner] = &Repo{
						FullName:        repo.NameWithOwner,
						StargazersCount: repo.StargazerCount,
						ForksCount:      repo.ForkCount,
						OpenIssues:      repo.Issues.TotalCount,
					}
				}
			}

			// Process watched repositories (subscriptions)
			for _, repo := range node.Watching.Nodes {
				if len(stargazer.Subscribed) >= maxSubscribed {
					break
				}
				stargazer.Subscribed = append(stargazer.Subscribed, repo.NameWithOwner)
				
				if _, ok := rs[repo.NameWithOwner]; !ok {
					rs[repo.NameWithOwner] = &Repo{
						FullName:        repo.NameWithOwner,
						StargazersCount: repo.StargazerCount,
						ForksCount:      repo.ForkCount,
						OpenIssues:      repo.Issues.TotalCount,
					}
				}
			}
		}

		fmt.Printf("\r*** processed repositories for %d/%d stargazers", end, len(sg))
	}
	fmt.Printf("\n")
	return nil
}

// QueryContributionsGraphQL queries contributions to subscribed repos using GraphQL
func QueryContributionsGraphQL(c *Context, client *GraphQLClientWithCache, sg []*Stargazer, rs map[string]*Repo) error {
	log.Printf("querying contributions to subscribed repos for %s stargazers using GraphQL...", format(len(sg)))

	authors := map[string]struct{}{}
	for _, s := range sg {
		authors[s.Login] = struct{}{}
	}

	commits := 0
	subscribed := 0
	qualifying := 0
	uniqueRepos := map[string]struct{}{}
	fmt.Printf("*** 0 commits from 0 repos (0 qual, 0 total) for 0 stargazers")

	for i, s := range sg {
		for _, rName := range s.Subscribed {
			r, ok := rs[rName]
			if !ok {
				log.Printf("missing %s repo", rName)
				continue
			}
			subscribed++
			if !r.meetsThresholds() {
				continue
			}
			
			if _, ok := uniqueRepos[r.FullName]; !ok {
				uniqueRepos[r.FullName] = struct{}{}
			}
			qualifying++

			if r.Statistics == nil {
				if err := QueryStatisticsGraphQL(c, client, r, authors); err != nil {
					log.Printf("failed to query statistics for %s: %v", r.FullName, err)
					continue
				}
			}

			if contrib, ok := r.Statistics[s.Login]; ok {
				commits += int(contrib.Commits)
				if s.Contributions == nil {
					s.Contributions = map[string]*Contribution{}
				}
				s.Contributions[r.FullName] = contrib
			}
			fmt.Printf("\r*** %s commits from %s repos (%s qual, %s total) for %s stargazers",
				format(commits), format(len(uniqueRepos)), format(qualifying), format(subscribed), format(i+1))
		}
	}
	fmt.Printf("\n")
	return nil
}

// QueryStatisticsGraphQL queries contributor stats for the specified repo using GraphQL
func QueryStatisticsGraphQL(c *Context, client *GraphQLClientWithCache, r *Repo, authors map[string]struct{}) error {
	r.Statistics = map[string]*Contribution{}

	parts := strings.Split(r.FullName, "/")
	if len(parts) != 2 {
		return fmt.Errorf("invalid repository format: %s", r.FullName)
	}
	owner, name := parts[0], parts[1]

	variables := map[string]interface{}{
		"owner": owner,
		"name":  name,
	}

	var response ContributionsResponse
	err := client.ExecuteWithCache(ContributionsQuery, variables, &response)
	if err != nil {
		return fmt.Errorf("failed to execute contributions query: %w", err)
	}

	// Process collaborators
	for _, collab := range response.Repository.Collaborators.Nodes {
		if _, ok := authors[collab.Login]; ok {
			r.Statistics[collab.Login] = &Contribution{
				Login:   collab.Login,
				Commits: collab.ContributionsCollection.TotalCommitContributions,
				// Note: GraphQL doesn't provide line-level additions/deletions easily
				// We'd need a more complex query or accept this limitation
				Additions: 0,
				Deletions: 0,
			}
		}
	}

	// Process commit history for more detailed stats (this is a simplified approach)
	commitAuthors := map[string]*Contribution{}
	for _, edge := range response.Repository.DefaultBranchRef.Target.History.Edges {
		if edge.Node.Author.User.Login != "" {
			login := edge.Node.Author.User.Login
			if _, ok := authors[login]; ok {
				if _, exists := commitAuthors[login]; !exists {
					commitAuthors[login] = &Contribution{
						Login:     login,
						Commits:   0,
						Additions: 0,
						Deletions: 0,
					}
				}
				commitAuthors[login].Commits++
				commitAuthors[login].Additions += edge.Node.Additions
				commitAuthors[login].Deletions += edge.Node.Deletions
			}
		}
	}

	// Merge the two sources of data, preferring the more detailed commit history
	for login, contrib := range commitAuthors {
		r.Statistics[login] = contrib
	}

	return nil
}