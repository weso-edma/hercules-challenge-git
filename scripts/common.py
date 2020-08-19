import csv
import joblib
import json
import os
import sys

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

from herc_common.utils import add_text_topics_to_graph, load_object, EDMA, ITSRDF, NIF

RESULTS_DIR = 'results'
NOTEBOOK_1_RESULTS_DIR = os.path.join(RESULTS_DIR, '1_data_fetching')
NOTEBOOK_6_RESULTS_DIR = os.path.join(RESULTS_DIR, '6_complete_system')

GIT_FILE_PATH = os.path.join(NOTEBOOK_1_RESULTS_DIR, 'git_dataframe.pkl')
FINAL_PIPE_FILE_PATH = os.path.join(NOTEBOOK_6_RESULTS_DIR, 'final_pipe.pkl')

RDF_FORMATS = {'json-ld', 'n3', 'xml', 'turtle'}
OUTPUT_FORMATS = RDF_FORMATS | {'csv', 'json'}

def create_git_graph(git_df, repos, topics):
    g = Graph()
    g.bind('edma', EDMA)
    g.bind('itsrdf', ITSRDF)
    g.bind('nif', NIF)
    collection_element = URIRef(f"{EDMA}{joblib.hash(git_df)}")
    g.add((collection_element, RDF.type, NIF.ContextCollection))
    for idx, repo_topics in enumerate(topics):
        text = repos[idx]
        git_row = git_df.loc[idx]
        uri = f"https://www.github.com/{git_row['owner_name']}/{git_row['name']}"
        gh_id = git_row['gh_id']
        context_element = add_text_topics_to_graph(uri, gh_id, text, repo_topics, g)
        g.add((collection_element, NIF.hasContext, context_element))
    return g

def load_final_pipe():
    import string
    import en_core_sci_lg
    from collections import Counter
    from tqdm import tqdm

    en_core_sci_lg.load()
    return load_object(FINAL_PIPE_FILE_PATH)

def show_git_csv_results(git_df, repos, topics, out_file):
    fieldnames = ['repo_id', 'topics']
    if out_file is not None:
        with open(out_file, 'w', encoding='utf-8') as f:
            csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
            _write_csv_contents(csvwriter, git_df, repos, topics)
    else:
        csvwriter = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        _write_csv_contents(csvwriter, git_df, repos, topics)

def show_git_graph_results(git_df, repos, topics, format, out_file):
    g = create_git_graph(git_df, repos, topics)
    if out_file is not None:
        g.serialize(destination=out_file, format=format)
    else:
        print(g.serialize(format=format).decode("utf-8"))

def show_git_json_results(git_df, repos, topics, out_file):
    res = {}
    for idx, repo_topics in enumerate(topics):
        repo_topics = [t[0] for t in repo_topics]
        repo_row = git_df.loc[idx]
        repo_id = repo_row['gh_id']
        repo_name = repo_row['name']
        repo_author = repo_row['owner_name']
        source_url = f"https://www.github.com/{repo_author}/{repo_name}"
        res[str(repo_id)] = {
            'source_url': source_url,
            'author': repo_author,
            'name': repo_name,
            'languages': repo_row['languages'],
            'topics': [{
                'labels': t.labels,
                'external_ids': t.uris,
                'descriptions': t.descs,
                'score': t.score
            } for t in repo_topics]
        }
    _write_json_contents(res, out_file)

def show_results(git_df, repos, topics, out_file, format):
    if format in RDF_FORMATS:
        show_git_graph_results(git_df, repos, topics, format, out_file)
    elif format == 'csv':
        show_git_csv_results(git_df, repos, topics, out_file)
    else:
        show_git_json_results(git_df, repos, topics, out_file)


def _write_csv_contents(csvwriter, git_df, repos, topics):
    csvwriter.writeheader()
    for idx, repo_topics in enumerate(topics):
        repo_topics = [t[0] for t in repo_topics]
        repo_id = git_df.loc[idx]['gh_id']
        csvwriter.writerow({
            'repo_id': repo_id,
            'topics': ' - '.join([str(t) for t in repo_topics])
        })

def _write_json_contents(res, out_file):
    if out_file is not None:
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(res, indent=2, ensure_ascii=False))
