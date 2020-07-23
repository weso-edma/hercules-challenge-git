import re
import tarfile
import tempfile

from comment_parser import comment_parser


FILE_EXTENSIONS_TO_MIME = {
    'c': 'text/x-c',
    'cpp': 'text/x-c++',
    'cs': 'text/x-c++',
    'go': 'text/x-go',
    'html': 'text/html',
    'java': 'text/x-java-source',
    'js': 'application/javascript',
    'py': 'text/x-python',
    'rb': 'text/x-ruby',
    'sh': 'text/x-shellscript',
    'xml': 'text/xml'
}


def get_source_code_comments(repo_content, filters=None):
    """ Return a dict with the comments of each source file in the repo.
    """
    filters = [] if filters is None else filters
    comments = dict()
    with tempfile.TemporaryFile(suffix='.tar.gz') as content_f:
        content_f.write(repo_content)
        content_f.seek(0)
        with tarfile.open(fileobj=content_f, mode='r:gz') as tar:
            for member in tar.getmembers():
                member_comments = []
                if member.isdir():
                    continue
                
                tokens = member.name.split('.')
                if len(tokens) == 1:
                    continue

                file_extension = tokens[-1]
                if file_extension in FILE_EXTENSIONS_TO_MIME:
                    inner_f = tar.extractfile(member)
                    mime = FILE_EXTENSIONS_TO_MIME[file_extension]
                    try:
                        file_comments = comment_parser.extract_comments_from_str(inner_f.read().decode('utf-8'), mime=mime)
                        member_comments += file_comments
                    except:
                        print(member.name)
                file_name = _extract_file_name(member.name)
                comments[file_name] = member_comments
    for key in comments.keys():
        for f in filters:
            comments[key] = filter(f, comments[key])
        comments[key] = [c.text().strip() for c in comments[key] if c.is_multiline()]
    return comments

def _extract_file_name(path):
    tokens = path.split('/')
    filename = tokens[-1]
    filename_no_extension = ' '.join(filename.split('.')[:-1]) # its better this? -> f.split('.')[0]
    filename_no_snake = filename_no_extension.replace('_', ' ')
    filename_no_dash = filename_no_snake.replace('-', ' ')
    filename_final = re.sub("([a-z])([A-Z])","\g<1> \g<2>",
                            filename_no_dash)
    return filename_final
