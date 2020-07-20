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
    filters = [] if filters is None else filters
    comments = []
    with tempfile.TemporaryFile(suffix='.tar.gz') as content_f:
        content_f.write(repo_content)
        content_f.seek(0)
        with tarfile.open(fileobj=content_f, mode='r:gz') as tar:
            for member in tar.getmembers():
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
                        comments += file_comments
                    except:
                        print(member.name)
    for f in filters:
        comments = filter(f, comments)
    return [c.text() for c in comments if c.is_multiline()]
