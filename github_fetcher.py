import requests

def get_user_public_repos(username: str):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return []

def get_repo_deep_context(username: str, repo_name: str) -> str:
    """Membaca README.md dan requirements.txt dari repository publik."""
    deep_text = ""
    # Header raw+json meminta teks mentah langsung dari GitHub API tanpa perlu decode base64
    headers = {"Accept": "application/vnd.github.raw+json"}

    # 1. Cek README.md
    readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    try:
        r_readme = requests.get(readme_url, headers=headers, timeout=5)
        if r_readme.status_code == 200:
            deep_text += f" [README]: {r_readme.text} "
    except Exception:
        pass

    # 2. Cek requirements.txt
    req_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/requirements.txt"
    try:
        r_req = requests.get(req_url, headers=headers, timeout=5)
        if r_req.status_code == 200:
            deep_text += f" [REQUIREMENTS]: {r_req.text} "
    except Exception:
        pass

    return deep_text

if __name__ == "__main__":
    test_user = "sulthanrunvarg-wq"
    test_repo = "doodle-diffusion"
    context = get_repo_deep_context(test_user, test_repo)
    print(f"Kutipan Deep Context dari {test_repo}:")
    print(context[:300] + "..." if len(context) > 300 else context)
