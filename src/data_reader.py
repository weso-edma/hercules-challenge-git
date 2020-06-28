import json
import requests

from requests.exceptions import HTTPError

from bs4 import BeautifulSoup

from .repo import GitHubIssue, GitHubRepoData


GITHUB_BASE_API = "https://api.github.com"

def _get_repo_info(repo_url):
    tokens = [token for token in repo_url.split('/')
              if token != '']
    return tokens[-2], tokens[-1]

def _make_github_request(url, token):
    response = requests.get(url, headers={'Authorization': f"token {token}"})
    if response.status_code != 200:
        raise HTTPError("There was an error retrieving data from GitHub: " + str(response.content))
    return response.content

def get_issue_comments(comments_url, token):
    comments = _make_github_request(comments_url, token)
    comments_dict = json.loads(comments)
    return [comment['body'] for comment in comments_dict]

def get_repo_contents(author, repo, token):
    response = _make_github_request(f"{GITHUB_BASE_API}/repos/{author}/{repo}", token)
    return json.loads(response)

def get_repo_languages(languages_url, token):
    response = _make_github_request(languages_url, token)
    response_dict = json.loads(response)
    return [(language, num_bytes) 
            for language, num_bytes
            in response_dict.items()]

def get_repo_readme_text(author, repo, token):
    try:
        res = _make_github_request(f"{GITHUB_BASE_API}/repos/{author}/{repo}/readme", token)
    except HTTPError as e:
        if "Not Found" in str(e):
            return ""
        else:
            raise(e)
    html_url = json.loads(res)['html_url']
    readme_html= requests.get(html_url).content
    soup = BeautifulSoup(readme_html, 'lxml')
    readme_element = soup.find('div', {'id': 'readme'})
    if readme_element is None:
        # readme.txt file
        readme_element = soup.find('div', {'itemprop': 'text'})
    return readme_element.text.strip()

def get_repo_issues(author, repo, token):
    issues = _make_github_request(f"{GITHUB_BASE_API}/repos/{author}/{repo}/issues", token)
    issues_dict = json.loads(issues)
    return [GitHubIssue(issue['title'], issue['body'],
                        get_issue_comments(issue['comments_url'], token))
            for issue in issues_dict]
    

def parse_repo_url(repo_url, token):
    author, repo = _get_repo_info(repo_url)
    repo_contents = get_repo_contents(author, repo, token)
    issues = get_repo_issues(author, repo, token) if repo_contents['has_issues'] else []
    languages = get_repo_languages(repo_contents['languages_url'], token)
    readme_text = get_repo_readme_text(author, repo, token)
    return GitHubRepoData(repo_contents['id'], repo_contents['name'],
        repo_contents['description'], repo_contents['owner']['login'],
        languages, readme_text, issues)

