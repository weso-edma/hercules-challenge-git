class GitHubIssue():
    def __init__(self, title, body, comments):
        self.title = title
        self.body = body
        self.comments = comments


class GitHubRepoData():
    def __init__(self, gh_id, name, description,
                 owner_name, languages, 
                 readme_text, issues,
                 commit_messages, filenames,
                 source_code_comments):
        self.gh_id = gh_id
        self.name = name
        self.description = description
        self.owner_name = owner_name
        self.languages = languages
        self.readme_text = readme_text
        self.issues = issues
        self.commit_messages = commit_messages
        self.filenames = filenames
        self.source_code_comments = source_code_comments

    def to_dict(self):
        return {
            'gh_id': self.gh_id,
            'name': self.name,
            'description': self.description,
            'owner_name': self.owner_name,
            'languages': self.languages,
            'readme_text': self.readme_text,
            'issues_text': '\n'.join([issue.body for issue in self.issues]),
            'commits_text': '\n'.join(self.commit_messages),
            'filenames': '\n'.join(self.filenames),
            'comments_text': '\n'.join(self.source_code_comments)
        }
    
    def __eq__(self, other):
        if not isinstance(other, GitHubRepoData):
            return False
        return self.gh_id == other.gh_id

    def __str__(self):
        return f"{self.gh_id} - {self.owner_name}: {self.name} - {self.description}"

