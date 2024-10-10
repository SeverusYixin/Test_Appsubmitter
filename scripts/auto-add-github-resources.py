import sys
import os
from _github_utilities import create_branch, get_file_in_repository, get_issue_body, write_file, send_pull_request
import yaml
from github import Github

def main():
    repository = sys.argv[1]
    issue = int(sys.argv[2])
    
    yml_filename = "resources/nfdi4bioimage.yml"
    
    # Get issue body (the GitHub link)
    issue_text = get_issue_body(repository, issue)
    if "\n" in issue_text or not issue_text.startswith("https://github.com/"):
        print(issue_text, " is not a GitHub repository link. I show myself out.")
        return

    github_repo_url = issue_text
    
    # Fetch data from the GitHub repository
    github_data_dict = complete_github_data(github_repo_url)
    github_yml = "\n- " + yaml.dump(github_data_dict).replace("\n", "\n  ")

    # Read the "database" (YAML file) from the repository
    branch = create_branch(repository)
    file_content = get_file_in_repository(repository, branch, yml_filename).decoded_content.decode()
    
    print("yml file content length:", len(file_content))

    # Add the new GitHub entry to the YAML content
    file_content += github_yml

    # Save the updated content back to GitHub
    write_file(repository, branch, yml_filename, file_content, "Add " + github_repo_url)
    res = send_pull_request(repository, branch, "Add " + github_repo_url, f"closes #{issue}") 

    print("Done.", res)
    

def complete_github_data(github_repo_url):
    # Retrieve the GitHub token from environment variables
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise Exception("GitHub token not found in environment. Please set GITHUB_TOKEN.")

    g = Github(token)
    
    # Extract the owner and repo name from the URL
    repo_path = github_repo_url.replace("https://github.com/", "")
    repo = g.get_repo(repo_path)

    # Build the data dictionary with repository details
    entry = {}
    entry['url'] = github_repo_url
    entry['name'] = repo.name
    entry['description'] = repo.description
    entry['license'] = repo.get_license().license.name if repo.get_license() else "No License"
    entry['authors'] = ", ".join([collab.login for collab in repo.get_collaborators()])

    return entry


if __name__ == "__main__":
    main()
