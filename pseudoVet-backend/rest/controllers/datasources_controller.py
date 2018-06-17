"""
The datasource controller.
Method of this controller handle requests for getting study profile eras and morbidities.
"""
from rest.decorators import rest_mapping
from rest.errors import BadRequestError
from rest.services import datasources_service
from flask import request


@rest_mapping('/morbidities', ['GET'])
def get_morbidities_for_study_profile_era():
    """
    Get all morbidities by study profile name.
    :return: JSON response with all morbidities
    """
    study_profile_era_name = request.args.get('studyProfileEra')
    if not study_profile_era_name:
        raise BadRequestError("studyProfileEra parameter is missing")
    return datasources_service.get_morbidities_for_study_profile_era(study_profile_era_name)


@rest_mapping('/studyProfileEras', ['GET'])
def get_study_profile_eras():
    """
    Get list of all study profile eras.
    :return: JSON response with all study profile eras
    """
    return datasources_service.get_study_profile_eras()
