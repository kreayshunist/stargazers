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
//
// Author: Spencer Kimball (spencer.kimball@gmail.com)

package cmd

// ExtendedContext

import (
	"errors"
	"fmt"
	"log"

	"github.com/kreayshunist/stargazers/fetch"
	"github.com/spf13/cobra"
)

// ExtendedContext wraps the original Context and adds mode support
type ExtendedContext struct {
    fetch.Context  // Embed the original Context
    Mode string // Add mode field
}

// NewContext creates a new ExtendedContext with the specified parameters
func NewContext(repo, token, cacheDir, mode string) *ExtendedContext {
    return &ExtendedContext{
        Context: fetch.Context{
            Repo:     repo,
            Token:    token,
            CacheDir: cacheDir,
        },
        Mode: mode,
    }
}

// GetBaseContext returns the base Context for fetch operations
func (c *ExtendedContext) GetBaseContext() *fetch.Context {
    return &fetch.Context{
        Repo:     c.Repo,
        Token:    c.Token,
        CacheDir: c.CacheDir,
        Mode:     c.Mode,
    }
}

// FetchCmd recursively fetches stargazer github data.
var FetchCmd = &cobra.Command{
	Use:   "fetch --repo=:owner/:repo --token=:access_token",
	Short: "recursively fetch all stargazer github data",
	Long: `
Recursively fetch all stargazer github data starting with the list of
stargazers for the specified :owner/:repo and then descending into
each stargazer's followers, other starred repos, and subscribed
repos. Each subscribed repo is further queried for that stargazer's
contributions in terms of additions, deletions, and commits. All
fetched data is cached by URL.

Use --graphql flag to switch from REST API to GraphQL API for
significantly reduced API calls and improved performance with large
repositories.
`,
	Example: `  stargazers fetch --repo=cockroachdb/cockroach --token=f87456b1112dadb2d831a5792bf2ca9a6afca7bc --graphql`,
	RunE:    RunFetch,
}


// RunFetch recursively queries all relevant github data for
// the specified owner and repo.

// RunFetch recursively queries all relevant github data for
// the specified owner and repo.
func RunFetch(cmd *cobra.Command, args []string) error {
	if len(Repo) == 0 {
		return errors.New("repository not specified; use --repo=:owner/:repo")
	}
	token, err := getAccessToken()
	if err != nil {
		return err
	}
	log.Printf("fetching GitHub data for repository %s", Repo)
	ctx := NewContext(Repo, token, CacheDir, Mode)
	if err := validateMode(ctx); err != nil {
		return err
	}
	
	// Choose API interface based on GraphQL flag
	if GraphQL {
		log.Printf("using GraphQL API")
		if err := fetch.QueryAllGraphQL(ctx.GetBaseContext()); err != nil {
			log.Printf("failed to query stargazer data with GraphQL: %s", err)
			return nil
		}
	} else {
		log.Printf("using REST API")
		if err := fetch.QueryAll(ctx.GetBaseContext()); err != nil {
			log.Printf("failed to query stargazer data: %s", err)
			return nil
		}
	}
	return nil
}

func validateMode(ctx *ExtendedContext) error {
	if ctx.Mode != "basic" && ctx.Mode != "full" {
		return fmt.Errorf("invalid mode: %s. Use 'basic' or 'full'", ctx.Mode)
	}
	return nil
}