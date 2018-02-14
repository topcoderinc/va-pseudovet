"""
the datasource  controller

this controller method handles request to get war ears and morbidities.
"""
from rest.decorators import rest_mapping
from rest.services import datasources_service
from flask import request


@rest_mapping('/morbidities', ['GET'])
def get_morbidities_for_war_era():
    """
    get all morbidities by war name
    :return: the all morbidities json response
    """
    return datasources_service.get_morbidities_for_war_era(request.args.get('warEra'))


@rest_mapping('/warEras', ['GET'])
def get_war_eras():
    """
    get all war eras
    :return:  the war eras json response
    """
    return datasources_service.get_war_eras()
