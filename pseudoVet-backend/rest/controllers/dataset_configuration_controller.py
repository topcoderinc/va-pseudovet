"""
the dateset configuration controller
this controller method handles request to save (create or update) the dataset config.
"""
from flask import request
from flask.json import loads

from rest.decorators import rest_mapping
from rest.errors import BadRequestError
from rest.services import dataset_configuration_service


@rest_mapping('/datasetConfigurations', ['PUT'])
def save():
    """
    save request body json data set configuration to a json file store on local file system
    :return: the saved data configuration json
    """
    return dataset_configuration_service.save(request.get_json(force=True, silent=True))


@rest_mapping('/datasetConfigurations', ['GET'])
def get():
    """
    get data set configurations by title , if title is None, that mean return all data set configurations
    :return: the matched data set configurations
    """
    return dataset_configuration_service.get(request.args.get('title'))


@rest_mapping('/datasetConfigurationFromFile', ['POST'])
def get_from_file():
    """
    get request post file and check the file content, then save the content to a json file store on local file system
    :return: the saved data set configuration json
    """
    config_file_obj = request.files.get('datasetConfiguration')
    if config_file_obj is None:
        raise BadRequestError('cannot found file where key = datasetConfiguration')
    return dataset_configuration_service.save(loads(config_file_obj.read()))
