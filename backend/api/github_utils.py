from github import Github
import os

def get_github_client():
    token = os.environ.get('GITHUB_PAT')
    if not token:
        raise ValueError("GITHUB_PAT is missing from environment variables")
    return Github(token)

def create_branch(repo_name, branch_name, base_branch="main"):
    g = get_github_client()
    repo = g.get_repo(repo_name)
    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_ref.object.sha)
    return branch_name

def commit_file(repo_name, branch_name, file_path, content, commit_message):
    g = get_github_client()
    repo = g.get_repo(repo_name)
    
    try:
        # Check if file exists to update
        contents = repo.get_contents(file_path, ref=branch_name)
        repo.update_file(contents.path, commit_message, content, contents.sha, branch=branch_name)
    except Exception: # File not found, create it
        repo.create_file(file_path, commit_message, content, branch=branch_name)
        
    return file_path

def open_pull_request(repo_name, branch_name, title, body, base_branch="main"):
    g = get_github_client()
    repo = g.get_repo(repo_name)
    pr = repo.create_pull(title=title, body=body, head=branch_name, base=base_branch)
    return pr.html_url
