from github import Github
import re
import time
import csv

# Replace with your GitHub token
GITHUB_TOKEN = 'your_github_token'

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

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
        fieldnames = ['Repository', 'Workflow', 'Job', 'Step', 'Uses Cache']
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
        
        # Fetch workflows
        workflows = repo.get_workflows()
        
        for workflow in workflows:
            check_rate_limit()
            
            # Fetch workflow runs
            runs = workflow.get_runs()
            
            for run in runs:
                check_rate_limit()
                # Fetch run jobs
                jobs = run.get_jobs()
                
                for job in jobs:
                    check_rate_limit()
                    
                    for step in job.steps:
                        uses_cache = 'Yes' if cache_regex.search(step.name) else 'No'
                        rows.append({
                            'Repository': repo.name,
                            'Workflow': workflow.name,
                            'Job': job.name,
                            'Step': step.name,
                            'Uses Cache': uses_cache
                        })
    
    write_to_csv(rows)
    print("Script execution completed. Check the github_actions_cache_usage.csv file for results.")

if __name__ == "__main__":
    main()
