"""
the data source service , the service used to read csv content and cache the content.
because of military_eras.csv and morbidity_xxxx.csv are static files local in data source dir,
and most endpoint need check the wars, etc.. data, so this service must be cache data sources
to avoid read file for each request.
"""

import datetime
import csv

from rest.decorators import service
from rest.logger import logger
from config import DATASOURCES_DIR
from rest.errors import EntityNotFoundError

# use this list to cache war ears data
military_eras = None

# use the map to cache morbidities data, the cache key is the war_code
morbidity_map = {}


@service(
    schema={'war_era': {'type': 'string', 'required': True}}
)
def get_morbidities_for_war_era(war_era):
    """
    get morbidities data by war_era name , it will return 404 if didn't found war_era
    :param war_era: the war era name
    :return: the morbidities data
    """
    war_code = get_war_era_by_name(war_era)['war_code']
    return get_morbidities_from_war_code(war_code)


@service()
def get_war_eras():
    """
    get all war eras data
    :return:  the war eras data
    """
    war_list = get_wars_from_file()
    return list(map(lambda war: convert_raw_war(war), war_list))


def convert_raw_war(war):
    """
    convert raw war to request war entity
    :param war: the raw war
    :return: the request war
    """
    return {
        'warEra': war['war_name'], 'warEraCode': war['war_code'],
        'warEraStartDate': war['start_date'],
        'warEraEndDate': war['end_date']
    }


def get_war_era_by_name(name):
    """
    get war era by war name, it will raise 404 error if didn't found
    :param name:  the war name
    :return: the war era
    """
    wars = get_wars_from_file()
    filter_wars = list(filter(lambda w: w['war_name'] == name, wars))
    if len(filter_wars) <= 0:
        raise EntityNotFoundError('cannot found war era where name = ' + name)
    return filter_wars[0]


def get_morbidities_from_war_code(war_code):
    """
    get morbidities from war code, if the result already cached, then return the cached result
    and it will rasie 404 if didn't found
    :param war_code:  the war code
    :return: the morbidities data
    """
    global morbidity_map

    if morbidity_map.get(war_code) is not None:  # return cached data
        return morbidity_map.get(war_code)

    file_path = DATASOURCES_DIR + '/morbidity_' + war_code + '.csv'
    try:
        with open(file_path, 'rU') as csv_file:
            morbidity_raw_list = csv.reader(csv_file, delimiter=',', quotechar='"')
            morbidity_list = []
            for row in morbidity_raw_list:
                if row[0] == 'Morbidity':  # skip first element
                    continue
                morbidity_list.append({
                    'name': row[0],
                    'icd10Code': row[1]
                })
            morbidity_map[war_code] = morbidity_list
            return morbidity_list
    except Exception as e:
        logger.error(e)
        raise EntityNotFoundError('Could not open ' + file_path + ' Error: %s' % e)


def str_to_datetime(str_time):
    """
    convert csv str time to datetime
    :param str_time: the str time from csv file
    :return:  the datetime or None
    """
    if str_time is None or str_time == '':
        return None

    return datetime.datetime.strptime(str_time, "%d-%b-%Y").date()


def get_wars_from_file():
    """
    get war eras from file, it will return cache result if data already cached
    :return: the war eras
    """
    global military_eras
    if military_eras is not None:  # return cached data
        return military_eras

    wars_data_path = DATASOURCES_DIR + '/military_eras.csv'
    try:  # load the military_eras datasource
        with open(wars_data_path, 'rU') as csv_file:
            military_eras_list = csv.reader(csv_file, delimiter=',', quotechar='"')
            military_eras = []
            for row in military_eras_list:
                if row[0] == 'war_code':  # skip first element (titles row)
                    continue

                war_code = row[0]
                war_name = row[1]
                percentage = float(row[2])
                start_date = str_to_datetime(row[3])
                end_date = str_to_datetime(row[4])

                military_eras.append({"war_code": war_code,
                                      "war_name": war_name,
                                      "percentage": percentage,
                                      "start_date": start_date,
                                      "end_date": end_date})
            return military_eras
    except Exception as e:
        logger.error('Could not open ' + wars_data_path + ' Error: %s' % e)
