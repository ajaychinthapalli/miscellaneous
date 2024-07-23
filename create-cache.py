from github import Github
import requests

# Authenticate to GitHub Enterprise
enterprise_url = 'https://your-github-enterprise-instance.com'
access_token = 'YOUR_GITHUB_ENTERPRISE_ACCESS_TOKEN'
g = Github(base_url=f"{enterprise_url}/api/v3", login_or_token=access_token)

# Repository details
owner = 'your-organization-or-username'
repo = 'your-repository-name'

# Cache details
caches = [
    {
        'key': 'cache-key1',
        'restore_keys': ['restore-key1a', 'restore-key1b'],
        'archive_url': 'https://path.to/your/cache1/archive.zip'
    },
    {
        'key': 'cache-key2',
        'restore_keys': ['restore-key2a', 'restore-key2b'],
        'archive_url': 'https://path.to/your/cache2/archive.zip'
    }
]

# URL for creating a cache
create_cache_url = f'{enterprise_url}/api/v3/repos/{owner}/{repo}/actions/cache/'

# Request headers
headers = {
    'Authorization': f'token {access_token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Create each cache
for cache in caches:
    payload = {
        'key': cache['key'],
        'restore_keys': cache['restore_keys'],
        'archive_url': cache['archive_url']
    }
    
    response = requests.post(create_cache_url, headers=headers, json=payload)
    
    # Check the response
    if response.status_code == 201:
        print(f'Cache {cache["key"]} created successfully')
    else:
        print(f'Failed to create cache {cache["key"]}: {response.status_code}')
        print(response.json())
