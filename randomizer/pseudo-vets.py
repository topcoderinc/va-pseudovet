"""PseudoVet Randomizer and Aging.

Description:
Creates C-CDA conformant documents of fictional patients from random data and ages those records +5, +10 and +15 years

Usage:
  pseudo-vets.py [-n number] [-o output] [-y year]

Options:
    -n number       Integer number of records to create. Defaults to 1.
    -o Output       Path to the folder where the output files shall be saved to. Will be created if non existent. Defaults to ./output
    -y year         Base year in YYYY format to use as base for randomizing patient birth date (and thus death date). Defaults to 90 years before current year 

    -h --help       Show this screen.
    -v --version    Show version.
"""
# Core libraries
import datetime
from datetime import timedelta
import json
import os
import io
from random import randint
from collections import OrderedDict
import types
import csv

# 3rd party libraries
from docopt import docopt

# Our libraries
from logger import logger
from renderer import Renderer
import datasource_methods

# Global variables
datasource = None
work_dir = None
session_id = datetime.datetime.now().isoformat().replace(':', '')  # build a 'unique' name for a work folder
base_year = None
military_eras = None

# setup a Jinja2 template renderer
renderer = Renderer()

def setup_work_session():
    # create a 'unique' work folder for each session
    global work_dir
    global session_id

    load_datasources()

    if not os.path.exists(work_dir):
        os.makedirs(work_dir)

    os.mkdir("%(work_dir)s/%(session_id)s" % globals())
    logger.info("Using work folder %(work_dir)s/%(session_id)s" % globals())

def load_datasources() :
    ''' 
    load data source and military eras, terminate if error occurs
    '''  
    global datasource
    global military_eras
    
    try:
        with open('./datasources/datasource.json') as data_file :    
            datasource = json.load(data_file, object_pairs_hook=OrderedDict)
    except Exception as e:
        logger.error('Could not open ./datasources/datasource.json Error: %s' % (e) )
    
    if datasource == None or len(datasource) == 0 :
        logger.error('Datasource not defined. Cannot continue.')
        exit (1)    

    # load the military_eras datasource
    try:
        logger.info('Reading military eras from datasource...')
        with open('./datasources/military_eras.csv', 'rU') as csvfile:
            military_eras_list = csv.reader(csvfile, delimiter=',', quotechar='"')
    
            # convert to dict
            military_eras = []
            for row in military_eras_list:
                # skip first element (titles row)
                if row[0] == 'war_code':
                    continue

                war_code = row[0]
                war_name = row[1]
                percentage = float(row[2])
                start_date = None
                end_date = None

                if row[3] != '':
                    start_date = datetime.datetime.strptime(row[3], "%d-%b-%Y").date()
                if row[4] != '':
                    end_date = datetime.datetime.strptime(row[4], "%d-%b-%Y").date()
                
                military_eras.append({"war_code":war_code,"war_name":war_name,"percentage":percentage,"start_date":start_date,"end_date":end_date})

        logger.info('Loaded military eras from datasource')

    except Exception as e:
        logger.error('Could not open ./datasources/military_eras.csv Error: %s' % (e) )
        exit (1)    


def date_is_between(date, start, end):
    if start is not None and end is not None:
        return start <= date <= end

    return False

def get_war(date_of_birth):
    # randomly determine if a patient went to war based on date of birth and a number of years of age  
    global military_eras

    # assume patient entered war at age 18 - 30
    age_entered_war = randint(18, 30)
    date_entered_war = date_of_birth + timedelta(days=age_entered_war*365)

    # return the first military_era where date_entered_war is between war start and end dates; return None if not found
    return next((x for x in military_eras if date_is_between(date_entered_war, x['start_date'], x['end_date'])), None)

def random_patient(index):
    '''
    Build a patient record to be used as base for template rendering and aging
    '''
    global session_id
    global base_year

    effective_time = datetime.datetime.now().date()

    # generate a random date of birth using base_year +/- 15 years
    year = base_year + randint(-15, 15)
    date_of_birth = datetime.date(year, randint(1,12), randint(1,28))

    # now, estimate a total age of 79 +/- 15 years
    # life expectancy based on https://en.wikipedia.org/wiki/List_of_sovereign_states_by_life_expectancy 
    total_age = randint(79-15, 79+15) 
    date_of_death = date_of_birth + timedelta(days=total_age*365)

    if date_of_death > effective_time:
        # patient is still alive!
        date_of_death = None
        total_age = effective_time.year - date_of_birth.year

    war = get_war(date_of_birth)

    patient_id = '{session_id}-{index}'.format(session_id=session_id, index=index)

    # initialize our patient record 
    patient = {'effective_time':effective_time, 'date_of_birth': date_of_birth, 'date_of_death': date_of_death, 'total_age':total_age, 'war': war, 'patient_id': patient_id}
    
    # build more fields as defined in datasource.json
    for field in datasource:
        if "repeat_max" in datasource[field] :
            # this field should be an array of repeatble items
            # build an array of repeat_max items
            value = []
            max_index = randint(1, datasource[field]["repeat_max"])
            for i in range(0, max_index):
                value.append(get_rand_value(field, patient))
        else:    
            value = get_rand_value(field, patient)
        
        patient[field] = value

    return patient

def get_rand_value(field, patient) : 
    '''
    generate a new random value calling a datasource method, from a linked field or just
    read from the datasource.json definiton
    '''
    global datasource

    if "method" in datasource[field] :
        # some fields define a method call to be made
        method_name = datasource[field]["method"]
        method_params = [patient] + datasource[field]["params"]

        if isinstance(datasource_methods.__dict__.get(method_name), types.FunctionType):
            method = datasource_methods.__dict__.get(method_name)
            return method(method_params)

    else :    
        if "linked_to" in datasource[field] :
            # some fields are linked to other fields, gender => gender_code(defined first)
            value_key = patient[datasource[field]["linked_to"]]
            value = datasource[field]["values"][value_key]
        else :
            if "values_from" in datasource[field] :
                # some fields share the same dataset values
                values_from_field = datasource[field]["values_from"]
                field_values = datasource[values_from_field]["values"]
            else:
                field_values = datasource[field]["values"]
                
            value_index = randint(0, len(field_values) - 1)
            value = field_values[value_index]
    
    return value 

def age_patient(patient, years) :
    '''
    Based on last aged 'patient' information determines the future field values at 'years',
    biological(calculated values) and non-biological(new random values) fields are considered.
    'patient' contains the last aged patient (preious aging)
    '''
    global datasource

    # start with the original 
    new_aged_patient = patient

    # only age patients that are alive. If a patient is dead, its record will not change.
    if patient['date_of_death'] is None:
        new_age = patient['total_age'] + years
        new_aged_patient['total_age'] = new_age

        # age date_of_death and total_age
        if patient['total_age'] >= 79+15:
            death_age = 79+15
        else:
            # use a random death age based on life expectancy
            death_age = randint(patient['total_age'], 79+15) 

        if new_age >= death_age:
            # patient died
            date_of_death = patient['date_of_birth'] + timedelta(days=death_age*365)
            new_aged_patient['total_age'] = death_age
            new_aged_patient['date_of_death'] = date_of_death

        for field in datasource:
            value = patient[field]
                   
            if "aging" in datasource[field]:
                if datasource[field]["aging"] == True:
                    # only generate a new random value
                    value = get_rand_value(field, new_aged_patient)
                elif years in datasource[field]["aging"]:
                    # biological aging, calculate aging rate
                    rates = datasource[field]["aging"][years]
                    rate = datasource[field]["aging"][years][randint(0, len(rates) - 1)]
                    value = float(value) 
                    value += value * rate
                    value = format(value, '.2f')

            new_aged_patient[field] = value
            
    return new_aged_patient


def create_file(record, index, age):
    '''
    Create an xml output file for each patient / aged patient
    '''
    global renderer
    global work_dir
    global session_id

    result = renderer.render(record)
    if age is None:
        filename = "{work_dir}/{session_id}/{session_id}-{index}.xml".format(work_dir=work_dir, session_id=session_id, index=index)
    else:
        filename = "{work_dir}/{session_id}/{session_id}-{index}_{age}.xml".format(work_dir=work_dir, session_id=session_id, index=index, age=age)
        
    with io.open(filename, 'w', encoding='utf-8') as f: 
        f.write(result)

def create_files(index):
    '''
    Create one file for patient initial state and files for 5, 10 and 15 years aged patient
    '''

    # build a random patient
    patient = random_patient(index)
    create_file(patient, index, None)

    # start aging with the original record
    aged_patient = patient
    age = 0 

    for i in range(0, 3):
        # age patient record in 3 increments of 5 years each (5, 10, 15)
        aged_patient = age_patient(aged_patient, 5)
        age += 5
        create_file(aged_patient, index, age)

# 
# Main entry point to the script.
# Actual script execution code starts
# 
if __name__ == '__main__':
    # Parse command line options
    options = docopt(__doc__, version='1.0.0')

    work_dir = options['-o'] or './output'
    
    base_year = options['-y'] or datetime.datetime.now().year - 90
    base_year = int(base_year)

    # be sure to create patients of at least 20 years of age 
    # we substract 35 years to have 20 of age minus 15 of random margin used in
    # random_patient()
    year_lower_bound = datetime.datetime.now().year - 35
    if base_year > year_lower_bound:
        logger.error('Base year should be less than {0} to build significant patients.'.format(year_lower_bound))
        exit(1)

    num_records = options['-n'] or 1
    num_records = int(num_records)

    # setup a new empty folder under work_dir for this session and load data sources
    setup_work_session()

    logger.info('Creating {0} fictional patients with base year {1}.\n'.format(num_records, base_year))

    # build num_records patients
    for i in range(1, num_records+1) :
        # create the files for a new record (patient)
        create_files(i)

    logger.info('')
    logger.info('Created {0} fictional patients in folder {1}/{2}/'.format(num_records, work_dir, session_id))

