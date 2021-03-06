"""
Initializer of routes for Flask application.
The controller functions will auto import into Flask app if function has a rest_mapping decorator
"""
from rest.decorators import inject_flask_app


def init(flask_app):
    """
    Import all controller functions, so that all routes can register into the Flask app
    :param flask_app: the Flask app instance
    :return: None
    """
    inject_flask_app(flask_app)
    from .dataset_configuration_controller import save, save_file, get

    from .dataset_generation_controller import generate, get_all_datasets, delete_dataset, get_dataset_by_name
    from .datasources_controller import get_morbidities_for_study_profile, get_study_profiles

    from rest.services.dataset_configuration_service import preload_all_configurations
    from rest.services.dataset_generation_service import preload_datasets

    preload_all_configurations()  # preload configurations into cache
    preload_datasets()  # preload data sets into cache