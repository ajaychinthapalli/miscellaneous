import csv
import time
from github import Github
import re

def check_rate_limit(g):
    """
    Check the rate limit and handle if the limit is exceeded.
    
    Args:
        g: GitHub object for API interactions.
    """
    rate_limit = g.get_rate_limit()
    remaining = rate_limit.core.remaining
    reset_time = rate_limit.core.reset
    
    if remaining == 0:
        reset_timestamp = reset_time.timestamp()
        current_timestamp = time.time()
        wait_time = reset_timestamp - current_timestamp
        
        print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds.")
        if wait_time > 0:
            time.sleep(wait_time + 10)  # Adding some buffer time

def check_workflows(repo, pattern, results, g):
    """
    Check workflows in the given repository for the specified pattern.
    
    Args:
        repo: GitHub repository object.
        pattern: Compiled regular expression pattern to search for.
        results: List to store the results.
        g: GitHub object for API interactions.
    """
    print(f"Checking workflows in repository: {repo.name}")
    try:
        # Check if the .github/workflows directory exists
        try:
            contents = repo.get_contents(".github/workflows")
        except:
            # Directory does not exist or other error
            return
        
        for content in contents:
            if content.type == "file":
                workflow_file = content.decoded_content.decode("utf-8")
                if pattern.search(workflow_file):
                    results.append({
                        'Repository': repo.name,
                        'File Path': content.path,
                        'Line Number': None,  # Line number extraction is not handled here
                        'Match': pattern.search(workflow_file).group(0)
                    })
                
            # Check rate limit after processing each file
            check_rate_limit(g)
    except Exception as e:
        print(f"Could not check workflows in {repo.name}: {e}")

def main():
    # Replace 'your_access_token' with your GitHub Enterprise access token
    g = Github("your_access_token", base_url="https://your-github-enterprise-instance/api/v3")

    # Replace 'your_organization' with your GitHub organization
    organization = g.get_organization('your_organization')

    # Define the pattern to search for
    pattern = re.compile(r'actions/usage@[\w\.]+')

    # List to store results
    results = []

    # Iterate over repositories in the organization
    for repo in organization.get_repos():
        check_workflows(repo, pattern, results, g)
        
        # Check rate limit after processing each repository
        check_rate_limit(g)

    # Write results to CSV
    with open('workflow_references.csv', 'w', newline='') as csvfile:
        fieldnames = ['Repository', 'File Path', 'Line Number', 'Match']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

    print("Results have been written to workflow_references.csv")

if __name__ == "__main__":
    main()
