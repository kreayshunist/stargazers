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
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

const (
	graphqlEndpoint = "https://api.github.com/graphql"
)

// GraphQLClient handles GraphQL requests to GitHub API
type GraphQLClient struct {
	token  string
	client *http.Client
}

// NewGraphQLClient creates a new GraphQL client
func NewGraphQLClient(token string) *GraphQLClient {
	return &GraphQLClient{
		token:  token,
		client: &http.Client{Timeout: 30 * time.Second},
	}
}

// GraphQLRequest represents a GraphQL request
type GraphQLRequest struct {
	Query     string                 `json:"query"`
	Variables map[string]interface{} `json:"variables,omitempty"`
}

// GraphQLResponse represents a GraphQL response
type GraphQLResponse struct {
	Data   json.RawMessage `json:"data"`
	Errors []GraphQLError  `json:"errors,omitempty"`
}

// GraphQLError represents a GraphQL error
type GraphQLError struct {
	Message   string                 `json:"message"`
	Type      string                 `json:"type,omitempty"`
	Path      []interface{}          `json:"path,omitempty"`
	Locations []GraphQLErrorLocation `json:"locations,omitempty"`
}

// GraphQLErrorLocation represents the location of a GraphQL error
type GraphQLErrorLocation struct {
	Line   int `json:"line"`
	Column int `json:"column"`
}

// Execute executes a GraphQL query
func (c *GraphQLClient) Execute(query string, variables map[string]interface{}, result interface{}) error {
	reqBody := GraphQLRequest{
		Query:     query,
		Variables: variables,
	}

	jsonBody, err := json.Marshal(reqBody)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequest("POST", graphqlEndpoint, bytes.NewBuffer(jsonBody))
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.token)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "Cockroach Labs Stargazers App GraphQL")

	resp, err := c.client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to execute request: %w", err)
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != 200 {
		return fmt.Errorf("GraphQL request failed with status %d: %s", resp.StatusCode, string(body))
	}

	var graphqlResp GraphQLResponse
	if err := json.Unmarshal(body, &graphqlResp); err != nil {
		return fmt.Errorf("failed to unmarshal response: %w", err)
	}

	if len(graphqlResp.Errors) > 0 {
		log.Printf("GraphQL errors: %+v", graphqlResp.Errors)
		return fmt.Errorf("GraphQL errors occurred: %+v", graphqlResp.Errors)
	}

	if err := json.Unmarshal(graphqlResp.Data, result); err != nil {
		return fmt.Errorf("failed to unmarshal data: %w", err)
	}

	return nil
}

// StargazersQuery fetches stargazers with pagination
const StargazersQuery = `
query StargazersQuery($owner: String!, $name: String!, $cursor: String, $first: Int!) {
  repository(owner: $owner, name: $name) {
    stargazers(first: $first, after: $cursor, orderBy: {field: STARRED_AT, direction: ASC}) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      edges {
        starredAt
        node {
          id
          login
          name
          email
          company
          location
          bio
          avatarUrl
          url
          followers {
            totalCount
          }
          following {
            totalCount
          }
          createdAt
          updatedAt
        }
      }
    }
  }
}
`

// UsersDetailQuery fetches detailed user information in batches
const UsersDetailQuery = `
query UsersDetailQuery($logins: [String!]!) {
  nodes(ids: $logins) {
    ... on User {
      id
      login
      name
      email
      company
      location
      bio
      avatarUrl
      url
      followers {
        totalCount
      }
      following {
        totalCount
      }
      starredRepositories(first: 100) {
        totalCount
        nodes {
          id
          nameWithOwner
          stargazerCount
          forkCount
          issues(states: OPEN) {
            totalCount
          }
        }
      }
      watching(first: 100) {
        totalCount
        nodes {
          id
          nameWithOwner
          stargazerCount
          forkCount
          issues(states: OPEN) {
            totalCount
          }
        }
      }
      createdAt
      updatedAt
    }
  }
}
`

// FollowersQuery fetches followers for a user
const FollowersQuery = `
query FollowersQuery($login: String!, $cursor: String, $first: Int!) {
  user(login: $login) {
    followers(first: $first, after: $cursor) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        login
        name
        email
        avatarUrl
        url
      }
    }
  }
}
`

// ContributionsQuery fetches repository contributors
const ContributionsQuery = `
query ContributionsQuery($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    collaborators(first: 100) {
      totalCount
      nodes {
        login
        contributionsCollection {
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
        }
      }
    }
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 100) {
            totalCount
            edges {
              node {
                author {
                  user {
                    login
                  }
                }
                additions
                deletions
                committedDate
              }
            }
          }
        }
      }
    }
  }
}
`

// StargazersResponse represents the response from StargazersQuery
type StargazersResponse struct {
	Repository struct {
		Stargazers struct {
			TotalCount int `json:"totalCount"`
			PageInfo   struct {
				HasNextPage bool   `json:"hasNextPage"`
				EndCursor   string `json:"endCursor"`
			} `json:"pageInfo"`
			Edges []struct {
				StarredAt string `json:"starredAt"`
				Node      struct {
					ID        string `json:"id"`
					Login     string `json:"login"`
					Name      string `json:"name"`
					Email     string `json:"email"`
					Company   string `json:"company"`
					Location  string `json:"location"`
					Bio       string `json:"bio"`
					AvatarURL string `json:"avatarUrl"`
					URL       string `json:"url"`
					Followers struct {
						TotalCount int `json:"totalCount"`
					} `json:"followers"`
					Following struct {
						TotalCount int `json:"totalCount"`
					} `json:"following"`
					CreatedAt string `json:"createdAt"`
					UpdatedAt string `json:"updatedAt"`
				} `json:"node"`
			} `json:"edges"`
		} `json:"stargazers"`
	} `json:"repository"`
}

// UsersDetailResponse represents the response from UsersDetailQuery
type UsersDetailResponse struct {
	Nodes []struct {
		ID        string `json:"id"`
		Login     string `json:"login"`
		Name      string `json:"name"`
		Email     string `json:"email"`
		Company   string `json:"company"`
		Location  string `json:"location"`
		Bio       string `json:"bio"`
		AvatarURL string `json:"avatarUrl"`
		URL       string `json:"url"`
		Followers struct {
			TotalCount int `json:"totalCount"`
		} `json:"followers"`
		Following struct {
			TotalCount int `json:"totalCount"`
		} `json:"following"`
		StarredRepositories struct {
			TotalCount int `json:"totalCount"`
			Nodes      []struct {
				ID            string `json:"id"`
				NameWithOwner string `json:"nameWithOwner"`
				StargazerCount int   `json:"stargazerCount"`
				ForkCount     int    `json:"forkCount"`
				Issues        struct {
					TotalCount int `json:"totalCount"`
				} `json:"issues"`
			} `json:"nodes"`
		} `json:"starredRepositories"`
		Watching struct {
			TotalCount int `json:"totalCount"`
			Nodes      []struct {
				ID            string `json:"id"`
				NameWithOwner string `json:"nameWithOwner"`
				StargazerCount int   `json:"stargazerCount"`
				ForkCount     int    `json:"forkCount"`
				Issues        struct {
					TotalCount int `json:"totalCount"`
				} `json:"issues"`
			} `json:"nodes"`
		} `json:"watching"`
		CreatedAt string `json:"createdAt"`
		UpdatedAt string `json:"updatedAt"`
	} `json:"nodes"`
}

// FollowersResponse represents the response from FollowersQuery
type FollowersResponse struct {
	User struct {
		Followers struct {
			TotalCount int `json:"totalCount"`
			PageInfo   struct {
				HasNextPage bool   `json:"hasNextPage"`
				EndCursor   string `json:"endCursor"`
			} `json:"pageInfo"`
			Nodes []struct {
				ID        string `json:"id"`
				Login     string `json:"login"`
				Name      string `json:"name"`
				Email     string `json:"email"`
				AvatarURL string `json:"avatarUrl"`
				URL       string `json:"url"`
			} `json:"nodes"`
		} `json:"followers"`
	} `json:"user"`
}

// ContributionsResponse represents the response from ContributionsQuery
type ContributionsResponse struct {
	Repository struct {
		Collaborators struct {
			TotalCount int `json:"totalCount"`
			Nodes      []struct {
				Login                   string `json:"login"`
				ContributionsCollection struct {
					TotalCommitContributions           int `json:"totalCommitContributions"`
					TotalIssueContributions            int `json:"totalIssueContributions"`
					TotalPullRequestContributions      int `json:"totalPullRequestContributions"`
					TotalPullRequestReviewContributions int `json:"totalPullRequestReviewContributions"`
				} `json:"contributionsCollection"`
			} `json:"nodes"`
		} `json:"collaborators"`
		DefaultBranchRef struct {
			Target struct {
				History struct {
					TotalCount int `json:"totalCount"`
					Edges      []struct {
						Node struct {
							Author struct {
								User struct {
									Login string `json:"login"`
								} `json:"user"`
							} `json:"author"`
							Additions     int    `json:"additions"`
							Deletions     int    `json:"deletions"`
							CommittedDate string `json:"committedDate"`
						} `json:"node"`
					} `json:"edges"`
				} `json:"history"`
			} `json:"target"`
		} `json:"defaultBranchRef"`
	} `json:"repository"`
}