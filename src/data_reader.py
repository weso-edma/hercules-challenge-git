import json
import re
import requests

from requests.exceptions import HTTPError

from bs4 import BeautifulSoup, NavigableString

from .code_analyser import get_source_code_comments
from .repo import GitHubIssue, GitHubRepoData


GITHUB_BASE_API = "https://api.github.com"

def _get_repo_info(repo_url):
    tokens = [token for token in repo_url.split('/')
              if token != '']
    return tokens[-2], tokens[-1]

def _is_header(tag):
    p = re.compile('^h[1-6]$')
    return p.match(tag)

def _is_list(tag):
    return tag in ['ul', 'ol']

def _make_github_request(url, token):
    response = requests.get(url, headers={'Authorization': f"token {token}"})
    if response.status_code != 200:
        raise HTTPError("There was an error retrieving data from GitHub: " + str(response.content))
    return response.content

def get_issue_comments(comments_url, token):
    comments = _make_github_request(comments_url, token)
    comments_dict = json.loads(comments)
    return [comment['body'] for comment in comments_dict]

def get_repo_comments(author, repo, token):
    tarball_url = f"{GITHUB_BASE_API}/repos/{author}/{repo}/tarball"
    tarball_contents = _make_github_request(tarball_url, token)
    license_filter = lambda c: 'license' not in c.text().lower() and 'copyright' not in c.text().lower()
    return get_source_code_comments(tarball_contents, filters=[license_filter])

def get_repo_commits_messages(author, repo, token):
    commits_url = f"{GITHUB_BASE_API}/repos/{author}/{repo}/commits"
    res = []
    has_next = True
    while has_next:
        response = requests.get(commits_url, headers={'Authorization': f"token {token}"})
        commits = json.loads(response.content)
        res += [commit['commit']['message'] for commit in commits]
        if 'next' not in response.links:
            has_next = False
        else:
            commits_url = response.links['next']['url']
    return res

def get_repo_contents(author, repo, token):
    response = _make_github_request(f"{GITHUB_BASE_API}/repos/{author}/{repo}", token)
    return json.loads(response)

def get_repo_languages(languages_url, token):
    response = _make_github_request(languages_url, token)
    response_dict = json.loads(response)
    return response_dict

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
        print(author, repo)
        readme_element = soup.find('div', {'itemprop': 'text'})
        return readme_element.text.strip()
    else:
        return parse_readme_content(readme_element)

def get_repo_issues(author, repo, token):
    issues = _make_github_request(f"{GITHUB_BASE_API}/repos/{author}/{repo}/issues", token)
    issues_dict = json.loads(issues)
    return [GitHubIssue(issue['title'], issue['body'],
                        get_issue_comments(issue['comments_url'], token))
            for issue in issues_dict]

def parse_readme_content(readme_element):
    readme_tokens = []
    for a in readme_element.article.children:
        if isinstance(a, NavigableString):
            continue
        
        if a.name == 'pre':
            continue
        
        if _is_header(a.name):
            readme_tokens.append(a.text + ".")
        elif _is_list(a.name):
            readme_tokens += [li.text + "." for li in a if not isinstance(li, NavigableString)]
        else:
            readme_tokens.append(a.text)
    return ' '.join(readme_tokens).strip()

def parse_repo_url(repo_url, token):
    author, repo = _get_repo_info(repo_url)
    repo_contents = get_repo_contents(author, repo, token)
    issues = get_repo_issues(author, repo, token) if repo_contents['has_issues'] else []
    languages = get_repo_languages(repo_contents['languages_url'], token)
    readme_text = get_repo_readme_text(author, repo, token)
    commit_messages = get_repo_commits_messages(author, repo, token)
    comments = get_repo_comments(author, repo, token)
    filenames = comments.keys()
    comments_text = [single_comment 
                     for file_comments in comments.values()
                     for single_comment in file_comments]
    return GitHubRepoData(repo_contents['id'], repo_contents['name'],
        repo_contents['description'], repo_contents['owner']['login'],
        languages, readme_text, issues, commit_messages, filenames, comments_text)

