import logging
import os
import sys

# set up module paths for imports
module_path = os.path.abspath(os.path.join('..'))
sys.path.append(module_path)
src_path = os.path.abspath(os.path.join('..', 'src'))
sys.path.append(src_path)

# start logging system and set logging level
logger = logging.getLogger()
logger.setLevel(logging.WARN)
logging.info("Starting logger")

DATA_DIR = os.path.join(module_path, 'data')
RESULTS_DIR = os.path.join(module_path, 'results')
NOTEBOOK_1_RESULTS_DIR = os.path.join(RESULTS_DIR, '1_data_fetching')
NOTEBOOK_2_RESULTS_DIR = os.path.join(RESULTS_DIR, '2_topic_modeling')
NOTEBOOK_3_RESULTS_DIR = os.path.join(RESULTS_DIR, '3_topic_labelling')
NOTEBOOK_4_RESULTS_DIR = os.path.join(RESULTS_DIR, '4_named_entity_recognition')
NOTEBOOK_5_RESULTS_DIR = os.path.join(RESULTS_DIR, '5_ner_topic_extraction')
NOTEBOOK_6_RESULTS_DIR = os.path.join(RESULTS_DIR, '6_complete_system')
NOTEBOOK_7_RESULTS_DIR = os.path.join(RESULTS_DIR, '7_evaluation')