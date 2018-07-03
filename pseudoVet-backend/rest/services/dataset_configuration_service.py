"""
Dataset configuration service.

The dataset configuration will be stored in the file named DatasetConfiguration.<title>.json.
If the file with such name already exists, it will be overwritten.
"""

from os.path import isfile, join, relpath, exists
from os import listdir, remove

from cerberus import Validator

from config import GENERATED_DATASETS_DIR, DATASET_CONFIGURATIONS_DIR, CONFIGURATION_PREFIX
from randomizer.pseudo_vets import get_icd_morbidity_name_by_code
from rest.decorators import service, custom_validators
from rest.errors import EntityNotFoundError, InnerServerError, BadRequestError
from rest.logger import logger

from rest.services.datasources_service import get_study_profile_by_name, get_morbidities_from_study_profile_code, convert_raw_study_profile

configurations_map = {}
    
from flask.json import dumps, load

# the study profile validation schema
study_profile_schema = {
    'studyProfile': {'type': 'string', 'required': True},
    'studyProfileCode': {'type': 'string'},
    'studyProfileStartDate': {'type': 'string'},
    'percentage': {'type': 'float'},
    'studyProfileEndDate': {'type': 'string'},
}

# the morbidity validation schema
morbidity_schema = {
    'name': {'type': 'string'},
    'icd10Code': {'type': 'string', 'required': True},
    'percentOfPopulationWithDiagnosisRisk': {'type': 'float'},
    'percentOfProbabilityToAcquireDiagnosis': {'type': 'float'},
    'numberOfEncounters': {'type': 'integer'},
    'exclusionRules': {'type': 'string'},
}

# the related conditions validation schema
relatedConditions_schema = {
    'name': {'type': 'string'},
    'icd10Code': {'type': 'string', 'required': True},
    'percentOfPopulationWithDiagnosisRisk': {'type': 'float'},
    'percentOfProbabilityToAcquireDiagnosis': {'type': 'float'},
    'numberOfEncounters': {'type': 'integer'},
    'exclusionRules': {'type': 'string'},
}

# the configuration validation schema
dataset_configuration_schema = {
    'title': {'type': 'string', 'required': True},
    'studyProfile': {'type': 'dict', 'schema': study_profile_schema, 'required': True},
    'numberOfPatients': {'type': 'integer', 'required': True},
    'maleRatio': {'type': 'float', 'required': False},
    'femaleRatio': {'type': 'float', 'required': False},
    # Cerberus currently doesn't support validation of list elements properly
    # thus morbiditiesData & relatedConditions items are validated separately
    'morbiditiesData': {'type': 'list', 'minlength': 1, 'required': True},
    'relatedConditionsData': {'type': 'list', 'required': False},
    'outputFolder': {'type': 'string'},
    'outputFormat': {'type': 'string', 'required': True, 'allowed': ['CCDA', 'FHIR-XML', 'FHIR-JSON', ]},
    'year': {'type': 'integer', 'required': True},
}

# create validator for "morbiditiesData" items
cerberus_validator = Validator()


def validate_document(document):
    """
    Validate the given document. Check only body_entity.morbiditiesData elements.
    Raise BadRequestError if validation failed.
    :param document: the document to be validated
    :return: None
    """
    if 'body_entity' in document:
        body_entity = document['body_entity']
        if 'morbiditiesData' in body_entity:
            morbidities_data = body_entity['morbiditiesData']
            for item in morbidities_data:
                if not cerberus_validator.validate(item, morbidity_schema):
                    raise BadRequestError("Request validation failed for morbiditiesData. Info: " +
                                          str(cerberus_validator.errors))
        if 'relatedConditionsData' in body_entity:
            relatedConditions_data = body_entity['relatedConditionsData']
            for item in relatedConditions_data:
                if not cerberus_validator.validate(item, relatedConditions_schema):
                    raise BadRequestError("Request validation failed for relatedConditionsData. Info: " +
                                          str(cerberus_validator.errors))


# register custom validator to validate "morbiditiesData" items
custom_validators.append(validate_document)


@service(
    schema={
        'body_entity': {'type': 'dict', 'schema': dataset_configuration_schema}
    }
)
def save(body_entity):
    """
    Check whether the body entity studyProfile and morbidities exist or not.
    Then save it to the local file system.
    :param body_entity: the request dataset configuration entity
    :return: the same fully populated dataset configuration entity
    """

    # make sure study profile exists
    study_profile = get_study_profile_by_name(body_entity['studyProfile']['studyProfile'])
    # update request study profile
    body_entity['studyProfile'] = convert_raw_study_profile(study_profile)

    total_morbidities = get_morbidities_from_study_profile_code(study_profile['study_profile_code'])

    for request_morbidity in body_entity['morbiditiesData']:
        morbidity_code = request_morbidity['icd10Code']
        # check whether morbidity exists in CSV file of the specified study profile
        morbidity_exists = False
        for morbidity in total_morbidities:
            if morbidity_code == morbidity['icd10Code']:
                # set or update morbidity name in request
                request_morbidity['name'] = morbidity['name']
                morbidity_exists = True
                break

        # if not found, try to find morbidity in ICD-10 datasource
        if not morbidity_exists:
            morbidity_name = get_icd_morbidity_name_by_code(morbidity_code)
            if morbidity_name:
                # set or update morbidity name in request
                request_morbidity['name'] = morbidity_name
                morbidity_exists = True

        if not morbidity_exists:
            raise EntityNotFoundError('Morbidity with ICD-10 code {0} is unknown'.format(morbidity_code))

    # set default output folder to the configuration
    output_folder = GENERATED_DATASETS_DIR
    # try to use short relative to the current directory path if possible
    try:
        output_folder = relpath(output_folder)
    except ValueError:
        pass
    body_entity['outputFolder'] = output_folder

    configuration_file = DATASET_CONFIGURATIONS_DIR + '/' + CONFIGURATION_PREFIX + '.' + body_entity['title'] + '.json'
    try:
        with open(configuration_file, 'w') as f:
            f.write(dumps(body_entity, indent=2))
        get_cache_map()[body_entity['title']] = body_entity  # inject to cache
        return body_entity

    except Exception as e:
        raise InnerServerError('Cannot save file {0}. Error: {1}'.format(configuration_file, e))


def read_configuration_from_file(file_path):
    """
    Read configuration from file with the specified path.
    :param file_path: the configuration file path
    :return: the configuration entity
    """
    try:
        with open(file_path, 'rU') as f:
            return load(f)
    except Exception as e:
        raise InnerServerError('Cannot read file {0}. Error: {1}'.format(file_path, e))


@service(schema={'title': {'type': 'string', 'nullable': True}})
def get(title):
    """
    Get configuration by title. If title is None, then return all configurations.
    :param title: the configuration title
    :return: the list with configuration entities
    """
    if title is None:  # return all configurations
        configurations = []
        keys = get_cache_map().keys()
        for key in keys:
            conf = get_cache_map().get(key)
            if conf is not None:
                configurations.append(conf)
        return sorted(configurations, key=lambda k: k['title'].lower())
    else:
        # put single configuration to a list
        return [get_configuration_by_title(title)]


def preload_all_configurations():
    """
    preload all configurations into cache
    :return: None
    """
    files = [f for f in listdir(DATASET_CONFIGURATIONS_DIR) if isfile(join(DATASET_CONFIGURATIONS_DIR, f))]
    for file in files:
        configuration = read_configuration_from_file(DATASET_CONFIGURATIONS_DIR + '/' + file)
        get_cache_map()[configuration['title']] = configuration
        logger.info("succeed load configuration = " + configuration['title'])


def get_configuration_by_title(title):
    """
    Get single configuration with the specified title
    :param title: the configuration title
    :return: the dataset configuration instance
    """
    configuration = get_cache_map().get(title)
    if configuration is not None:
        return configuration

    configuration_file_path = DATASET_CONFIGURATIONS_DIR + '/' + CONFIGURATION_PREFIX + '.' + title + '.json'
    if isfile(configuration_file_path):
        configuration = read_configuration_from_file(configuration_file_path)
        get_cache_map()[title] = configuration
        return configuration
    else:
        raise EntityNotFoundError('Cannot find configuration file for title ' + title)


def get_cache_map():
    """
    get cache map
    :return: the cached configurations
    """
    global configurations_map
    return configurations_map


@service(schema={'title': {'type': 'string', 'required': True}})
def delete_config_by_title(title):
    """
    Delete dateset Config by title
    It raises EntityNotFoundError if dataset config not found
    :param title: the dataset Config title
    """

    config_file = join(DATASET_CONFIGURATIONS_DIR, '{0}.{1}.{2}'.format(CONFIGURATION_PREFIX, title, 'json'))
    if not exists(config_file):
        raise EntityNotFoundError("Dataset config not found where title = " + title)
    remove(config_file)

    if get_cache_map().get(title) is not None:  # delete from cache
        get_cache_map().pop(title, None)

    from rest.services.dataset_generation_service import remove_dateset_by_config_title
    remove_dateset_by_config_title(title)
