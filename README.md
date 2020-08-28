# hercules-challenge-git
Code related to the Git Repositories track from Hercules challenge

## Directory layout
* __data__: Directory with the input dataset for this track.
* __notebooks__: Jupyter notebooks with the process taken for the creation and training of the topic extraction system.
* __results__: Output of the notebooks and scripts from the system. This folder contains a variety of files (pickled models, dataframes, track output...).
* __scripts__: Scripts provided to run the final system and obtain predictions for the track.
* __src__: Track-specific source code regarding the parsing and handling of repositories.

## Dependencies
In order to run the code from this repository, Python 3.7 or greater is required. Experiments were executed in Python 3.7.8, and that is the preferred version for the execution of the models. 

Instructions to install Python 3.7.8 are available at the [official website](https://www.python.org/downloads/release/python-378/). 

Once Python has been installed, it is preferrable to create a [environment] before installing the dependencies. To create a new python environment, the following command can be used:
```python
python -m venv edma_env
```

This environment can be then used with the following command:
```bash
souce edma_env/bin/activate
```

Finally, we can install the dependencies of the system with pip:
```python
pip install -r requirements.txt
```

## Exploring the creation of the systems
In the notebooks directory we provide a series of Jupyter notebooks that can be executed to explore how the systems were created and get more information about them or finetune their hyperparameters. In this section we will explain how to run those notebooks and provide some advice on how they should be executed.

If you have followed the steps from the previous section to install Python and the project dependencies, the [jupyter package](https://pypi.org/project/jupyter/) should already be installed. In order to run the Jupyter client, go to the notebooks directory and run the _jupyter notebook_ command:
```bash
cd notebooks
jupyter notebook
```

This will open a new tab in your browser with the Jupyter explorer where the different files can be explored:
![](./results/notebook_example.PNG)

If the browser was not automatically opened, you can connect to the Jupyter client through localhost on port 8888 ([localhost:8888](http://localhost:8888)).

Now you can click on any of the notebooks to explore its content or even rerun and modify the cells. Instructions on how to do this are provided in the [official Notebook docs](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Notebook%20Basics.html).

It is recommended to run the notebooks in a sequential manner, in the order indicated by their first filename number (i.e. notebook _1_data_fetching.ipynb_ should be run before _2_Topic_Modelling.ipynb_ and so on). Non-sequential execution is not recommended and should be avoided, since the execution of one notebook may depend on outputs produced by the previous ones.

## How to run the systems
> __Note__: In order to run the systems you must first obtain the models used to perform the topic extraction. Due to size constraints, they are not included in these repositories. There are two main alternatives to obtain the models: the first one is the execution of every notebook to retrain and build the systems from scratch, but this may take some time; the second alternative is to go to the [complete_system directory](./results/6_complete_system) and follow the instructions to download the trained models.
Several scripts are provided in the _scripts_ folder to execute the systems and reproduce the results obtained for this track. In the following sections we will explain the main functionality of each script and how they can be executed.

### Compute track results
The script _run_track_predictions.py_ can be used to obtain at once all the topics assigned to every repository from the dataset. The following parameters can be passed to the script:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| -f --format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_, _rdf/xml_ or _ttl_ |
| -o --output | Name of the file where the results will be saved. If no output file is specified, results will be written to the console instead. | No | Any valid filename. |

For more additional information about how to run the script, you can execute the following command:
```bash
python scripts/run_track_predictions.py -h
```

In the following example, we will be running the script twice. The first execution will print the results in console and in json format (default values). The second one will save the results to the file _results.ttl_ in the turtle format:
```bash
python scripts/run_track_predictions.py
python scripts/run_track_predictions.py -o results.ttl -f ttl
```

### Predict repository topics
The script _predict_repo.py_ can be used to obtain the topics for a given protocol or list of protocols. The following parameters can be passed to the string:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| input | Url of the GitHub repository to extract the topics from. If the --file flag is set, file with the urls of the GitHub repositories. | __Yes__ | Any GitHub url or file. |
| --isFile | If present, this flag indicates that the input passed to the script is a file with the urls of each repository delimited by newlines. | No | True or False |
| --token | itHub token used to fetch information about the input repositories before the topic extraction steps. | No | Github tokens |
| -f --format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _csv_, _json_, _jsonld_, _n3_ or _ttl_ |
| -o --output | Name of the file where the results will be saved. If no output file is specified, results will be written to the console instead. | No | Any valid filename. |

For more additional information about how to run the script, you can execute the following command:
```bash
python scripts/predict_repo.py -h
```

In the following example, we will be running the script twice. The first execution will print the results in console and in json format (default values). The second one we will use the list of repositories urls from the [script directory](./scripts/test.txt) to predict the topics for those repositories. After that, we will save the results to the file _results.ttl_ in the turtle format:
```bash
python scripts/predict_protocol.py https://github.com/cmungall/LIRICAL/
python scripts/predict_protocol.py scripts/test.txt --isFile -o results.ttl -f ttl
```

## Using the demo API
An API has been deployed at http://edma-challenge.compute.weso.network/ where the different functionality of the system can be tested out without needing to manually run the scripts with Python.

For the Git track, we provide the __api/git/topics__ GET endpoint to predict the topics of a given GitHub repository. The following parameters can be sent in the JSON body:
| Name | Description | Compulsory | Allowed Values |
| ---- | ----------- | ---------- | ------ |
| input | Url of the GitHub repository to extract the topics from. | __Yes__ | Any GitHub url. |
| token | itHub token used to fetch information about the input repositories before the topic extraction steps. | No | Github tokens |
| format | Output format of the results. If no output format is specified, results are returned in JSON by default. | No | One of _json_, _jsonld_, _n3_ or _ttl_ |

An example body passed to the API could be as follows:
```json
{
  "input": "https://github.com/cmungall/LIRICAL/",
  "token": "GITHUB_TOKEN_HERE",
  "format": "ttl"
}
```

The response will be as follows:
```json
{
  "task_id": "YOUR_TASK_ID"
}
```

A task identifier will be returned. We can query the __api/prediction/<task_id>__ endpoint to get the status of our task. When the task is finished, we will get a result like the following one:
```json
{
   "result":"{'216602979': {'source_url': 'https://www.github.com/cmungall/LIRICAL', 'author': 'cmungall', 'name': 'LIRICAL', 'languages': {'Java': 492423, 'FreeMarker': 13149, 'Python': 849}, 'topics': [{'labels': {'en': 'computer science', 'es': 'ciencias de la computación'}, 'external_ids': ['https://www.wikidata.org/w/Q21198', 'https://freebase.toolforge.org//m/01mkq', 'https://www.jstor.org/topic/computer-science-education', 'https://academic.microsoft.com/v2/detail41008148', 'http://vocabularies.unesco.org/thesaurus/concept450'], 'descriptions': {'en': 'study of the theoretical foundations of computation', 'es': 'ciencia dedicada a la computación y al proceso de información'}, 'score': 0.21895332390381894}, {'labels': {'en': 'software', 'es': 'software'}, 'external_ids': ['https://www.wikidata.org/w/Q7397', 'https://id.ndl.go.jp/auth/ndlsh/00684642', 'https://freebase.toolforge.org//m/01mf0', 'https://www.jstor.org/topic/computer-software', 'https://meshb.nlm.nih.gov/record/ui?ui=D012984', 'https://academic.microsoft.com/v2/detail2777904410', 'http://vocabularies.unesco.org/thesaurus/concept6081'], 'descriptions': {'en': 'non-tangible executable component of a computer', 'es': 'equipamiento lógico o soporte lógico de un sistema informático'}, 'score': 0.2180281690140845}, {'labels': {'en': 'artificial intelligence', 'es': 'inteligencia artificial'}, 'external_ids': ['https://www.wikidata.org/w/Q11660', 'https://id.ndl.go.jp/auth/ndlsh/00574798', 'https://freebase.toolforge.org//m/0mkz', 'https://meshb.nlm.nih.gov/record/ui?ui=D001185', 'https://www.jstor.org/topic/artificial-intelligence', 'http://vocabularies.unesco.org/thesaurus/concept3052', 'http://id.nlm.nih.gov/mesh/G17.035.250', 'http://id.nlm.nih.gov/mesh/L01.224.050.375', 'https://academic.microsoft.com/v2/detail154945302'], 'descriptions': {'en': 'intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals', 'es': 'rama de la informática que desarrolla máquinas y software con inteligencia similar a la humana'}, 'score': 0.21228743828853539}, {'labels': {'en': 'interaction science', 'es': ''}, 'external_ids': ['https://www.wikidata.org/w/Q97008347'], 'descriptions': {'en': 'scientific discipline', 'es': ''}, 'score': 0.21164889253486463}, {'labels': {'en': 'engineering', 'es': 'ingeniería'}, 'external_ids': ['https://www.wikidata.org/w/Q11023', 'https://id.ndl.go.jp/auth/ndlsh/00566144', 'https://freebase.toolforge.org//m/02ky346', 'https://www.jstor.org/topic/engineering', 'http://vocabularies.unesco.org/thesaurus/concept623', 'http://uri.gbv.de/terminology/bk/5', 'https://meshb.nlm.nih.gov/record/ui?ui=D004738', 'http://id.nlm.nih.gov/mesh/J01.293', 'https://academic.microsoft.com/v2/detail127413603'], 'descriptions': {'en': 'applied science', 'es': 'ciencia aplicada'}, 'score': 0.21032608695652175}, {'labels': {'en': 'automation', 'es': 'automatización'}, 'external_ids': ['https://www.wikidata.org/w/Q184199', 'https://freebase.toolforge.org//m/017cmr', 'http://vocabularies.unesco.org/thesaurus/concept3401', 'https://meshb.nlm.nih.gov/record/ui?ui=D001331', 'https://academic.microsoft.com/v2/detail115901376', 'https://academic.microsoft.com/v2/detail167123822'], 'descriptions': {'en': 'use of various control systems for operating equipment', 'es': 'uso de sistemas o elementos computerizados y electromecánicos para controlar maquinarias o procesos industriales'}, 'score': 0.2096424702058505}, {'labels': {'en': 'statistics', 'es': 'estadística'}, 'external_ids': ['https://www.wikidata.org/w/Q12483', 'https://id.ndl.go.jp/auth/ndlsh/00573173', 'https://freebase.toolforge.org//m/06mnr', 'https://www.jstor.org/topic/statistics', 'https://meshb.nlm.nih.gov/record/ui?ui=D020500', 'https://meshb.nlm.nih.gov/record/ui?ui=D013223', 'http://id.nlm.nih.gov/mesh/V02.925', 'http://id.nlm.nih.gov/mesh/E05.318.740', 'http://id.nlm.nih.gov/mesh/H01.548.832', 'http://id.nlm.nih.gov/mesh/N05.715.360.750', 'http://id.nlm.nih.gov/mesh/N06.850.520.830', 'https://academic.microsoft.com/v2/detail105795698', 'http://vocabularies.unesco.org/thesaurus/concept119', 'http://vocabularies.unesco.org/thesaurus/concept2238'], 'descriptions': {'en': 'study of the collection, organization, analysis, interpretation, and presentation of data', 'es': 'estudio de la recolección, organización, análisis, interpretación y presentación de los datos'}, 'score': 0.2094722598105548}]}}",
   "task_status":"Finished"
}

```

## Results obtained
The results obtained for the track dataset can be found in the [script_results folder](./results/8_script_results). These results are provided in multiple formats (_.csv_, _.json_, _.jsonld_, and _.ttl_).
