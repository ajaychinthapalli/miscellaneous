import csv
from github import Github
import re

# Replace 'your_access_token' with your GitHub Enterprise access token
g = Github("your_access_token", base_url="https://your-github-enterprise-instance/api/v3")

# Replace 'your_organization' with your GitHub organization
organization = g.get_organization('your_organization')

# Define the pattern to search for
pattern = re.compile(r'actions/usage@[\w\.]+')

# List to store results
results = []

# Function to check workflows for pattern
def check_workflows(repo):
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
    except Exception as e:
        print(f"Could not check workflows in {repo.name}: {e}")

# Iterate over repositories in the organization
for repo in organization.get_repos():
    check_workflows(repo)

# Write results to CSV
with open('workflow_references.csv', 'w', newline='') as csvfile:
    fieldnames = ['Repository', 'File Path', 'Line Number', 'Match']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for result in results:
        writer.writerow(result)

print("Results have been written to workflow_references.csv")
