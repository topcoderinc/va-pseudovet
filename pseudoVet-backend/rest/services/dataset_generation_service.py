"""
The dataset service.
It provides a method for generating records according to the specified dataset configuration.
"""
from randomizer.pseudo_vets import generate_from_config
from rest.decorators import service
from rest.services import dataset_configuration_service
from rest.errors import EntityNotFoundError


@service(schema={'title': {'type': 'string', 'required': True}})
def generate(title):
    """
    Generate a dataset according to dataset configuration file with the specified title.
    It raises EntityNotFoundError if file cannot be found.
    :param title: the dataset configuration title
    :return: the number of generated report files
    """
    configurations = dataset_configuration_service.get(title)  # the length will be 1
    if len(configurations) <= 0:
        raise EntityNotFoundError('Cannot find configuration with title ' + title)
    return generate_from_config(configurations[0])
