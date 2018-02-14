"""
the dateset controller

this controller method handles request to generate datasets.
"""

from rest.decorators import rest_mapping
from flask import request
from rest.services import dataset_generation_service


@rest_mapping('/generateDatasets', ['PUT'])
def generate():
    """
    generate dataset by config title
    :return: None
    """
    return dataset_generation_service.generate(request.args.get('title'))
