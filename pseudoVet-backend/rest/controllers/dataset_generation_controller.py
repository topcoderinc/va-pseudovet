"""
The dataset generation controller.

Methods of this controller handle requests for generating datasets.
"""

from flask import request

from rest.decorators import rest_mapping
from rest.services import dataset_generation_service


@rest_mapping('/generateDatasets', ['PUT'])
def generate():
    """
    Generate dataset by configuration with the specified title
    :return: the message with the number of generated report files
    """
    files_num = dataset_generation_service.generate(request.args.get('title'))
    message = "Dataset containing {0} files was generated successfully".format(files_num)
    return {'message': message}
