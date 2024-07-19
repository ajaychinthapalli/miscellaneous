from github import Github
import re
import csv

# Replace with your GitHub token and Enterprise URL if applicable
GITHUB_TOKEN = 'your_github_token'
GITHUB_ENTERPRISE_URL = 'https://your-enterprise-url.com/api/v3'  # Optional for GitHub Enterprise

# Initialize GitHub API client
g = Github(GITHUB_TOKEN, base_url=GITHUB_ENTERPRISE_URL if GITHUB_ENTERPRISE_URL else None)

# Specify the organization or user
org_name = "your_org_or_user"

# Regular expression to match any version of actions/cache
cache_regex = re.compile(r'actions/cache@\d+\.\d+\.\d+|actions/cache@latest|actions/cache@\*')

def check_rate_limit():
    rate_limit = g.get_rate_limit().core
    remaining = rate_limit.remaining
    reset = rate_limit.reset.timestamp()
    
    if remaining == 0:
        sleep_time = reset - time.time() + 5  # Add a buffer of 5 seconds
        print(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)

def write_to_csv(rows):
    with open('github_actions_cache_usage.csv', 'w', newline='') as csvfile:
        fieldnames = ['Repository', 'Workflow File', 'Uses Cache']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def main():
    rows = []
    
    # Fetch repositories
    org = g.get_organization(org_name)
    repos = org.get_repos()

    # Iterate through repositories
    for repo in repos:
        check_rate_limit()
        
        # Fetch workflow files from the repository
        contents = repo.get_contents(".github/workflows")
        
        for content in contents:
            if content.type == "file":
                check_rate_limit()
                workflow_file = repo.get_contents(content.path)
                file_content = workflow_file.decoded_content.decode("utf-8")
                
                # Search for actions/cache usage in the file content
                uses_cache = 'Yes' if cache_regex.search(file_content) else 'No'
                rows.append({
                    'Repository': repo.name,
                    'Workflow File': content.name,
                    'Uses Cache': uses_cache
                })
    
    write_to_csv(rows)
    print("Script execution completed. Check the github_actions_cache_usage.csv file for results.")

if __name__ == "__main__":
    main()
