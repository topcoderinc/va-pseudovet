"""
dataset configuration service

the dataset config will be stored to the file named <DatasetConfiguration.title>.json.
 If the file with such name already exist, it will be overwritten.
"""

from os.path import isfile, join

from flask.json import dumps, load
from os import listdir

from config import GENERATED_DATASETS_DIR, DATESET_CONFIGURATIONS_DIR, CONFIGURATION_PREFIX
from rest.decorators import service
from rest.errors import EntityNotFoundError, InnerServerError
from rest.services.datasources_service import get_war_era_by_name, get_morbidities_from_war_code, \
    convert_raw_war

# the war era validate schema
war_era_schema = {
    'warEra': {'type': 'string', 'required': True},
    'warEraCode': {'type': 'string'},
    'warEraStartDate': {'type': 'string'},
    'percentage': {'type': 'float'},
    'warEraEndDate': {'type': 'string'},
}

# the morbidity validate schema
morbidity_schema = {
    'name': {'type': 'string'},
    'icd10Code': {'type': 'string', 'required': True},
    'percentOfPopulationWithDiagnosis': {'type': 'float'},
    'percentOfProbabilityToAcquireDiagnosis': {'type': 'float'},
    'numberOfEncounters': {'type': 'integer'},
    'exclusionRules': {'type': 'string'},
}

# the configuration validate schema
dataset_configuration_schema = {
    'title': {'type': 'string', 'required': True},
    'warEra': {'type': 'dict', 'schema': war_era_schema, 'required': True},
    'numberOfPatients': {'type': 'integer', 'required': True},
    'maleRatio': {'type': 'float', 'required': True},
    'femaleRatio': {'type': 'float', 'required': True},
    'morbiditiesData': {'type': 'list', 'minlength': 1,
                        'items': [{'type': 'dict', 'schema': morbidity_schema, 'required': True}]},
    'outputFolder': {'type': 'string'},
    'year': {'type': 'integer', 'required': True},
}


@service(
    schema={
        'body_entity': {'type': 'dict', 'schema': dataset_configuration_schema}
    }
)
def save(body_entity):
    """
    1. check the body entity warEra and morbidities are exist or not
    2. the save it to local file system
    :param body_entity: the request data set configuration entity
    :return:
    """

    war_era = get_war_era_by_name(body_entity['warEra']['warEra'])  # make sure war era exist
    body_entity['warEra'] = convert_raw_war(war_era)  # update request war era

    total_morbidities = get_morbidities_from_war_code(war_era['war_code'])
    for request_morbidity in body_entity['morbiditiesData']:  # make sure morbidity
        morbidity_exist = False
        for morbidity in total_morbidities:
            if request_morbidity['icd10Code'] == morbidity['icd10Code']:
                request_morbidity['name'] = morbidity['name']  # update request morbidity
                morbidity_exist = True
        if not morbidity_exist:
            raise EntityNotFoundError('cannot found morbidity in '
                                      + war_era['war_name']
                                      + ' where morbidity icd10Code = ' + request_morbidity['icd10Code'])
    body_entity['outputFolder'] = GENERATED_DATASETS_DIR
    configuration_file = DATESET_CONFIGURATIONS_DIR + '/' + CONFIGURATION_PREFIX + '.' + body_entity['title'] + '.json'
    try:
        with open(configuration_file, 'w') as f:
            f.write(dumps(body_entity, indent=2))
        return body_entity

    except Exception as e:
        raise InnerServerError('cannot save file , err = %s', e)


def read_configuration_from_file(file_path):
    """
    read configuration from file path
    :param file_path: the configuration file path
    :return: the configuration entity
    """
    try:
        with open(file_path, 'rU') as f:
            return load(f)
    except Exception as e:
        raise InnerServerError('cannot read file ' + 'file_path' + ', err = %s', e)


@service(schema={'title': {'type': 'string', 'nullable': True}})
def get(title):
    """
    get configuration by title, if title is None, then return all configurations
    :param title: the configuration title
    :return: the configurations
    """
    if title is None:  # return all configurations
        configurations = []
        files = [f for f in listdir(DATESET_CONFIGURATIONS_DIR) if isfile(join(DATESET_CONFIGURATIONS_DIR, f))]
        for file in files:
            configurations.append(read_configuration_from_file(DATESET_CONFIGURATIONS_DIR + '/' + file))
        return configurations
    else:
        configuration_file_path = DATESET_CONFIGURATIONS_DIR + '/' + CONFIGURATION_PREFIX + '.' + title + '.json'
        if isfile(configuration_file_path):
            return [read_configuration_from_file(configuration_file_path)]
        else:
            raise EntityNotFoundError('cannot found configuration where title = ' + title)
