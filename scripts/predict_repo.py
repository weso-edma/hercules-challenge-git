import argparse
import logging
import pickle
import re

import pandas as pd

from .common import GIT_FILE_PATH, load_final_pipe, show_results

def clean(text):
    return re.sub('\s+', ' ', text).strip()

def load_repos_df(input, is_file, token):
    if is_file:
        with open(input, 'r', encoding='utf-8') as f:
            repos_urls = [line.rstrip('\n') for line in f]
    else:
        repos_urls = [input]
    parsed_repos = [parse_repo_url(url, token) for url in repos_urls]
    df = pd.DataFrame([repo.to_dict() for repo in parsed_repos])
    df.fillna(value="", inplace=True)
    df['full_text'] = df["description"] + ". " + df["readme_text"] + df["filenames"]
    empty_idx = df[df['full_text'] == '. '].index
    df.loc[empty_idx, 'full_text'] = df.loc[empty_idx, 'commits_text']
    df['full_text_cleaned'] = df['full_text'].apply(lambda x: clean(x))
    return df

def parseargs():
    parser = argparse.ArgumentParser(description="Run predictions for the Git track dataset")
    parser.add_argument('input', type=str, nargs='1', help="Url of the GitHub repository to extract " +
        "the topics from. If the --file flag is set, file with the urls of the GitHub repositories.")
    parser.add_argument('--token', type=str, nargs='1', help="GitHub token used to fetch information about " +
        "the input repositories before the topic extraction steps.")
    parser.add_argument('--file', action='store_true', default=False, help="If present, this flag " +
        "indicates that the input passed to the script is a file with the urls of each repository " +
        "delimited by newlines.")
    parser.add_argument('-f', '--format', choices=OUTPUT_FORMATS, help="Output format of the results. " +
        "If no output format is specified, results are returned in JSON by default.",
        nargs='?', default='json')
    parser.add_argument('-o', '--output', help="Name of the file where the results will be saved. " +
        "If no output file is specified, results will be written to the console instead.",
        nargs='?', default=None)
    return parser.parse_args()

def main(args):
    logger.info('Loading repository data...')
    git_df = load_repos_df(args.input, args.file)
    logger.info('Loading topic extraction model...')
    final_pipe = load_final_pipe()
    repos = git_df['full_text_cleaned'].values
    logger.info('Predicting topics...')
    topics = final_pipe.transform(repos)
    logger.info('Writting results...')
    show_results(git_df, repos, topics, args.output, args.format)

if __name__ == '__main__':
    args = parseargs()
    exit(main(args))
