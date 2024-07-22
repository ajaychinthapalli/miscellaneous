from github import Github
import requests
import json

def initialize_github_client(token, base_url):
    return Github(base_url=base_url, login_or_token=token)

def fetch_cache_keys(org_name, client, headers, output_file):
    org = client.get_organization(org_name)
    repos = org.get_repos()

    with open(output_file, 'w') as file:
        for repo in repos:
            owner = repo.owner.login
            repo_name = repo.name
            
            # Fetch cache usage by repository
            cache_usage_url = f"{client.base_url}/orgs/{org_name}/actions/cache/usage-by-repository"
            response = requests.get(cache_usage_url, headers=headers)
            
            if response.status_code == 200:
                cache_usages = response.json()
                for usage in cache_usages['repositories']:
                    if usage['repository']['full_name'] == f"{owner}/{repo_name}":
                        # Fetch GitHub Actions caches for the repository
                        cache_url = f"{client.base_url}/repos/{owner}/{repo_name}/actions/caches"
                        cache_response = requests.get(cache_url, headers=headers)
                        
                        if cache_response.status_code == 200:
                            caches = cache_response.json()
                            for cache in caches['actions_caches']:
                                # Write cache keys to the file
                                file.write(f"{repo_name},{cache['key']}\n")
                        else:
                            print(f"Failed to fetch caches for repository {repo_name}: {cache_response.status_code}")
            else:
                print(f"Failed to fetch cache usage for organization {org_name}: {response.status_code}")

def delete_caches(repo_owner, repo_name, cache_keys, headers, base_url):
    for cache_key in cache_keys:
        delete_url = f"{base_url}/repos/{repo_owner}/{repo_name}/actions/caches"
        delete_response = requests.delete(delete_url, headers=headers, json={"key": cache_key})
        if delete_response.status_code == 204:
            print(f"Successfully deleted cache {cache_key} for repository {repo_name}")
        else:
            print(f"Failed to delete cache {cache_key} for repository {repo_name}: {delete_response.status_code}")

def read_and_delete_cache_keys(filename, headers, base_url):
    with open(filename, 'r') as file:
        for line in file:
            repo_name, cache_key = line.strip().split(',')
            delete_caches(your_repo_owner, repo_name, [cache_key], headers, base_url)

def main():
    # GitHub Enterprise settings
    token = "your_github_token"
    base_url = "https://github.yourcompany.com/api/v3"
    org_name = "your_org_name"
    output_file = "cache_keys.txt"

    client = initialize_github_client(token, base_url)
    headers = {"Authorization": f"token {token}"}

    # Fetch and save cache keys
    fetch_cache_keys(org_name, client, headers, output_file)

    # Read cache keys from the file and delete them
    read_and_delete_cache_keys(output_file, headers, base_url)

if __name__ == "__main__":
    main()
