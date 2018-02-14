"""
the dataset service
"""
from randomizer.pseudo_vets import generate_from_config
from rest.decorators import service
from rest.services import dataset_configuration_service
from rest.errors import EntityNotFoundError


@service(schema={'title': {'type': 'string', 'required': True}})
def generate(title):
    """
    generate a dataset according by config file, it will raise 404 problem if didn't found file
    :param title: the config title
    :return:
    """
    configurations = dataset_configuration_service.get(title)  # the length will be 1
    if len(configurations) <= 0:
        raise EntityNotFoundError('cannot found configuration where title = ' + title)
    generate_from_config(configurations[0])
