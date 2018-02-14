"""
the controller functions will auto import into flask app if function had rest_mapping decorator
"""
from rest.decorators import inject_flask_app


def init(flask_app):
    """
    import all controller function, so that all route can register into flask app
    :param flask_app: the flask app instance
    :return: void
    """
    inject_flask_app(flask_app)
    from .dataset_configuration_controller import save, get_from_file, get
    from .dataset_controller import generate
    from .datasources_controller import get_morbidities_for_war_era, get_war_eras
