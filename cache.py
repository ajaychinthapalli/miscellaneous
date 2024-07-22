import requests

def initialize_headers(token):
    return {"Authorization": f"token {token}"}

def fetch_cache_usage(org_name, base_url, headers):
    cache_usage_url = f"{base_url}/orgs/{org_name}/actions/cache/usage-by-repository"
    response = requests.get(cache_usage_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch cache usage: {response.status_code}")
        return None

def fetch_caches_for_repository(owner, repo_name, base_url, headers):
    cache_url = f"{base_url}/repos/{owner}/{repo_name}/actions/caches"
    caches = []
    
    while cache_url:
        response = requests.get(cache_url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            caches.extend(result.get('actions_caches', []))
            
            # Handle pagination
            if 'next' in response.links:
                cache_url = response.links['next']['url']
            else:
                cache_url = None
        else:
            print(f"Failed to fetch caches for repository {repo_name}: {response.status_code}")
            cache_url = None
    
    return caches

def write_cache_keys_to_file(caches, output_file):
    with open(output_file, 'w') as file:
        for cache in caches:
            file.write(f"{cache['key']}\n")

def delete_caches(owner, repo_name, cache_keys, base_url, headers):
    for cache_key in cache_keys:
        print(f"Deleting cache key {cache_key} for repository: {repo_name}")
        delete_url = f"{base_url}/repos/{owner}/{repo_name}/actions/caches"
        response = requests.delete(delete_url, headers=headers, json={"key": cache_key})
        
        if response.status_code == 204:
            print(f"Successfully deleted cache {cache_key} for repository {repo_name}")
        else:
            print(f"Failed to delete cache {cache_key} for repository {repo_name}: {response.status_code}")

def main():
    # GitHub Enterprise settings
    token = "your_github_token"
    base_url = "https://github.yourcompany.com/api/v3"
    org_name = "your_org_name"
    output_file = "cache_keys.txt"

    headers = initialize_headers(token)
    
    # Fetch and list cache usage
    cache_usage_data = fetch_cache_usage(org_name, base_url, headers)
    if cache_usage_data:
        print("Cache usage by repository:")
        for repo_usage in cache_usage_data.get('repository_cache_usages', []):
            print(f"Repository: {repo_usage['full_name']}, Active Caches: {repo_usage['active_caches_count']}, Size: {repo_usage['active_caches_size_in_bytes']} bytes")
    
    # Fetch caches for each repository and write keys to file
    repos = [repo_usage['full_name'] for repo_usage in cache_usage_data.get('repository_cache_usages', [])]
    all_caches = []
    for repo_full_name in repos:
        owner, repo_name = repo_full_name.split('/')
        caches = fetch_caches_for_repository(owner, repo_name, base_url, headers)
        all_caches.extend(caches)
    
    write_cache_keys_to_file(all_caches, output_file)
    
    # Read cache keys from the file and delete them
    with open(output_file, 'r') as file:
        cache_keys = [line.strip() for line in file.readlines()]

    for repo_full_name in repos:
        owner, repo_name = repo_full_name.split('/')
        delete_caches(owner, repo_name, cache_keys, base_url, headers)

if __name__ == "__main__":
    main()
