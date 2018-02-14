# Core libraries
import csv
import datetime
import io
import json
import os
import types
from collections import OrderedDict
from datetime import timedelta
from random import randint

from randomizer import datasource_methods
# Our libraries
from rest.logger import logger
from .renderer import Renderer
from config import DATASOURCES_DIR, BASE_YEAR
from rest.services.datasources_service import get_wars_from_file

# 3rd party libraries

# Global variables
data_source = None
work_dir = None
session_id = datetime.datetime.now().isoformat().replace(':', '')  # build a 'unique' name for a work folder
base_year = None
military_eras = None

# setup a Jinja2 template renderer
renderer = Renderer()


def setup_work_session(output_dir, in_base_year):
    # create a 'unique' work folder for each session
    global work_dir
    global session_id
    global base_year

    work_dir = output_dir
    base_year = in_base_year

    load_datasources()
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    os.mkdir("%(work_dir)s/%(session_id)s" % globals())
    logger.info("Using work folder %(work_dir)s/%(session_id)s" % globals())


def load_datasources():
    """
    load data source and military eras, terminate if error occurs
    """
    global data_source
    global military_eras

    data_source_file = DATASOURCES_DIR + '/datasource.json'
    try:
        with open(data_source_file) as data_file:
            data_source = json.load(data_file, object_pairs_hook=OrderedDict)
    except Exception as e:
        logger.error('Could not open ' + data_source_file + ' Error: %s' % e)

    if data_source is None or len(data_source) == 0:
        logger.error('Datasource not defined. Cannot continue.')
        exit(1)

    military_eras = get_wars_from_file()


def date_is_between(date, start, end):
    if start is not None and end is not None:
        return start <= date <= end

    return False


def get_war(date_of_birth):
    # randomly determine if a patient went to war based on date of birth and a number of years of age  
    global military_eras

    # assume patient entered war at age 18 - 30
    age_entered_war = randint(18, 30)
    date_entered_war = date_of_birth + timedelta(days=age_entered_war * 365)

    # return the first military_era where date_entered_war is between war start and end dates; return None if not found
    return next((x for x in military_eras if date_is_between(date_entered_war, x['start_date'], x['end_date'])), None)


def random_patient(index):
    """
    Build a patient record to be used as base for template rendering and aging
    """
    global session_id
    global base_year
    global data_source

    effective_time = datetime.datetime.now().date()

    # generate a random date of birth using base_year +/- 15 years
    year = base_year + randint(-15, 15)
    date_of_birth = datetime.date(year, randint(1, 12), randint(1, 28))

    # now, estimate a total age of 79 +/- 15 years
    # life expectancy based on https://en.wikipedia.org/wiki/List_of_sovereign_states_by_life_expectancy 
    total_age = randint(79 - 15, 79 + 15)
    date_of_death = date_of_birth + timedelta(days=total_age * 365)

    if date_of_death > effective_time:
        # patient is still alive!
        date_of_death = None
        total_age = effective_time.year - date_of_birth.year

    war = get_war(date_of_birth)

    patient_id = '{session_id}-{index}'.format(session_id=session_id, index=index)

    # initialize our patient record 
    patient = {'effective_time': effective_time, 'date_of_birth': date_of_birth, 'date_of_death': date_of_death,
               'total_age': total_age, 'war': war, 'patient_id': patient_id}

    # build more fields as defined in datasource.json
    for field in data_source:
        if "repeat_max" in data_source[field]:
            # this field should be an array of repeatble items
            # build an array of repeat_max items
            value = []
            max_index = randint(1, data_source[field]["repeat_max"])
            for idx in range(0, max_index):
                value.append(get_rand_value(field, patient))
        else:
            value = get_rand_value(field, patient)

        patient[field] = value

    return patient


def get_rand_value(field, patient):
    """
    generate a new random value calling a datasource method, from a linked field or just
    read from the datasource.json definiton
    """
    global data_source

    if "method" in data_source[field]:
        # some fields define a method call to be made
        method_name = data_source[field]["method"]
        method_params = [patient] + data_source[field]["params"]

        if isinstance(datasource_methods.__dict__.get(method_name), types.FunctionType):
            method = datasource_methods.__dict__.get(method_name)
            return method(method_params)
    else:
        if "linked_to" in data_source[field]:
            # some fields are linked to other fields, gender => gender_code(defined first)
            value_key = patient[data_source[field]["linked_to"]]
            value = data_source[field]["values"][value_key]
        else:
            if "values_from" in data_source[field]:
                # some fields share the same data set values
                values_from_field = data_source[field]["values_from"]
                field_values = data_source[values_from_field]["values"]
            else:
                field_values = data_source[field]["values"]

            value_index = randint(0, len(field_values) - 1)
            value = field_values[value_index]
        return value


def age_patient(patient, years):
    """
    Based on last aged 'patient' information determines the future field values at 'years',
    biological(calculated values) and non-biological(new random values) fields are considered.
    'patient' contains the last aged patient (previous aging)
    """
    global data_source

    # start with the original 
    new_aged_patient = patient

    # only age patients that are alive. If a patient is dead, its record will not change.
    if patient['date_of_death'] is None:
        new_age = patient['total_age'] + years
        new_aged_patient['total_age'] = new_age

        # age date_of_death and total_age
        if patient['total_age'] >= 79 + 15:
            death_age = 79 + 15
        else:
            # use a random death age based on life expectancy
            death_age = randint(patient['total_age'], 79 + 15)

        if new_age >= death_age:
            # patient died
            date_of_death = patient['date_of_birth'] + timedelta(days=death_age * 365)
            new_aged_patient['total_age'] = death_age
            new_aged_patient['date_of_death'] = date_of_death

        for field in data_source:
            value = patient[field]

            if "aging" in data_source[field]:
                if data_source[field]["aging"] is True:
                    # only generate a new random value
                    value = get_rand_value(field, new_aged_patient)
                elif years in data_source[field]["aging"]:
                    # biological aging, calculate aging rate
                    rates = data_source[field]["aging"][years]
                    rate = data_source[field]["aging"][years][randint(0, len(rates) - 1)]
                    value = float(value)
                    value += value * rate
                    value = format(value, '.2f')

            new_aged_patient[field] = value

    return new_aged_patient


def create_file(record, index, age):
    """
    Create an xml output file for each patient / aged patient
    """
    global renderer
    global work_dir
    global session_id

    result = renderer.render(record)
    if age is None:
        filename = "{work_dir}/{session_id}/{session_id}-{index}.xml".format(work_dir=work_dir, session_id=session_id,
                                                                             index=index)
    else:
        filename = "{work_dir}/{session_id}/{session_id}-{index}_{age}.xml".format(work_dir=work_dir,
                                                                                   session_id=session_id, index=index,
                                                                                   age=age)

    with io.open(filename, 'w', encoding='utf-8') as f:
        f.write(result)


def create_files(index):
    """
    Create one file for patient initial state and files for 5, 10 and 15 years aged patient
    """

    # build a random patient
    patient = random_patient(index)
    create_file(patient, index, None)

    # start aging with the original record
    aged_patient = patient
    age = 0

    for idx in range(0, 3):
        # age patient record in 3 increments of 5 years each (5, 10, 15)
        aged_patient = age_patient(aged_patient, 5)
        age += 5
        create_file(aged_patient, index, age)


def generate_from_config(dataset_config):
    """
    accept dataset config file and according config file filter params to generate dataset

    for now, just return the randomizer dataset,
    https://apps.topcoder.com/forums/?module=Thread&threadID=912489&start=0
    :param dataset_config: the dataset config file
    :return: the generated config file
    """
    # TODO generate data by config
    logger.debug(dataset_config)
    create_files(1)  # create random dataset
