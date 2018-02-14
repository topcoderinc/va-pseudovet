import os

# the rest api base prefix
APPLICATION_ROOT = '/api/v1'

# the logger level
LOG_LEVEL = 'DEBUG'

# the logger format
LOG_FORMAT = '%(asctime)s %(levelname)s : %(message)s'

# the flask rum mode , PROD or DEBUG
FLASK_RUN_MODE = os.environ.get('MODE') or 'PROD'

# the flask run port
WEB_PORT = os.environ.get('PORT') or 5000

# the project dir
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

# the randomizer templates dir
TEMPLATES_DIR = PROJECT_DIR + '/randomizer/templates'

# the datasources dir
DATASOURCES_DIR = PROJECT_DIR + '/randomizer/datasources'

# the dateset configurations dir
DATESET_CONFIGURATIONS_DIR = PROJECT_DIR + '/output/datasetConfigurations'

# the generated datasets dir
GENERATED_DATASETS_DIR = PROJECT_DIR + '/output/generatedDatasets'

# the data set config file prefix
CONFIGURATION_PREFIX = 'DatasetConfiguration'

# the randomizer base year
BASE_YEAR = 1928
