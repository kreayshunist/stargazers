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
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
)

// GraphQLCacheKey generates a cache key for GraphQL queries
func GraphQLCacheKey(query string, variables map[string]interface{}) string {
	data := struct {
		Query     string                 `json:"query"`
		Variables map[string]interface{} `json:"variables"`
	}{
		Query:     query,
		Variables: variables,
	}
	
	jsonData, _ := json.Marshal(data)
	hash := sha256.Sum256(jsonData)
	return hex.EncodeToString(hash[:])
}

// GraphQLCacheEntry represents a cached GraphQL response
type GraphQLCacheEntry struct {
	Response json.RawMessage `json:"response"`
	Query    string          `json:"query"`
}

// GetGraphQLCache checks if a GraphQL query response is cached
func GetGraphQLCache(c *Context, query string, variables map[string]interface{}) (json.RawMessage, bool, error) {
	cacheKey := GraphQLCacheKey(query, variables)
	cachePath := filepath.Join(c.CacheDir, c.Repo, "graphql", cacheKey+".json")
	
	if _, err := os.Stat(cachePath); os.IsNotExist(err) {
		return nil, false, nil
	}
	
	data, err := ioutil.ReadFile(cachePath)
	if err != nil {
		return nil, false, err
	}
	
	var entry GraphQLCacheEntry
	if err := json.Unmarshal(data, &entry); err != nil {
		return nil, false, err
	}
	
	return entry.Response, true, nil
}

// PutGraphQLCache stores a GraphQL query response in cache
func PutGraphQLCache(c *Context, query string, variables map[string]interface{}, response json.RawMessage) error {
	cacheKey := GraphQLCacheKey(query, variables)
	cacheDir := filepath.Join(c.CacheDir, c.Repo, "graphql")
	
	if err := os.MkdirAll(cacheDir, 0755); err != nil {
		return err
	}
	
	entry := GraphQLCacheEntry{
		Response: response,
		Query:    query,
	}
	
	data, err := json.Marshal(entry)
	if err != nil {
		return err
	}
	
	cachePath := filepath.Join(cacheDir, cacheKey+".json")
	return ioutil.WriteFile(cachePath, data, 0644)
}

// GraphQLClientWithCache is a GraphQL client with caching support
type GraphQLClientWithCache struct {
	*GraphQLClient
	context *Context
}

// NewGraphQLClientWithCache creates a new GraphQL client with caching
func NewGraphQLClientWithCache(token string, context *Context) *GraphQLClientWithCache {
	return &GraphQLClientWithCache{
		GraphQLClient: NewGraphQLClient(token),
		context:       context,
	}
}

// ExecuteWithCache executes a GraphQL query with caching
func (c *GraphQLClientWithCache) ExecuteWithCache(query string, variables map[string]interface{}, result interface{}) error {
	// Check cache first
	if cachedResponse, found, err := GetGraphQLCache(c.context, query, variables); err == nil && found {
		return json.Unmarshal(cachedResponse, result)
	}
	
	// Execute the query
	err := c.Execute(query, variables, result)
	if err != nil {
		return err
	}
	
	// Cache the result
	resultBytes, err := json.Marshal(result)
	if err != nil {
		return err
	}
	
	if err := PutGraphQLCache(c.context, query, variables, resultBytes); err != nil {
		// Log but don't fail on cache errors
		fmt.Printf("Warning: failed to cache GraphQL response: %v\n", err)
	}
	
	return nil
}