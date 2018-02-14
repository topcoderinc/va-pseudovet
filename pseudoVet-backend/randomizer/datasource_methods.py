"""
Custom methods used in ./datasources/datasource.json
They can be called from any field definition as:
    "field": {
        "method": "get_date",
        "params": ["birth"]
        }
All datasource methods receive a list of parameters as the only parameter
The patient dict as is at index 0 at that parameter        
"""

from datetime import timedelta
from random import randint

from rest.logger import logger
from config import DATASOURCES_DIR

icd_lines = None
war_lines = None


def build_problem(lines, patient, collection='icd'):
    """
    Internally used by random_icd_problem() to build a problem
    from ICD-10 or war morbidity data sources
    """
    # pick a random line from 'lines' dataset
    index = randint(0, len(lines) - 1)

    # set ICD problem as resolved if random index is pair
    resolved = (index % 2 == 0)

    # randomize onset (and resolved_on) dates
    onset = patient['date_of_birth']

    # add a random number of years from birth_date
    years_delta = randint(20, patient['total_age'])
    onset = onset + timedelta(days=years_delta * 365)

    if resolved:
        # add a random number of days to onset
        days_delta = randint(30, 100)
        resolved_on = onset + timedelta(days=days_delta)
    else:
        resolved_on = None

    if collection == 'icd':
        return {'code': lines[index][:8].strip(), 'name': icd_lines[index][8:].strip(), 'resolved': resolved,
                'onset': onset, 'resolved_on': resolved_on}
    else:
        # war collection
        data = lines[index].split(',')
        return {'code': data[1].strip('"'), 'name': data[0].strip('"'), 'resolved': resolved, 'onset': onset,
                'resolved_on': resolved_on}


def random_icd_problem(params):
    """
    Method defined in datasource.json called from get_rand_value() in pseudo_vets.py
    It is dynamically instantieted and called with a list on the first (only) param
    params[0] contains the patient dict
    """

    global icd_lines
    global war_lines

    if icd_lines is None:
        # load the ICD-10 datasource
        icd_file = DATASOURCES_DIR + '/ICD-10/icd10cm_codes_2018.txt'
        try:
            logger.info('Reading ICD-10 datasource...')
            icd_lines = [line.rstrip('\n') for line in open(icd_file)]
            logger.info('Loaded {0} records from ICD-10 datasource'.format(len(icd_lines)))
        except Exception as e:
            logger.error('Could not open ' + icd_file + ' Error: %s' % e)
            exit(1)

    patient = params[0]

    if patient['war'] is None:
        return build_problem(icd_lines, patient, 'icd')
    else:
        # get a random problem from war morbidity stats

        if war_lines is None:
            # read morbidity data for each war
            war_lines = {}

            for war in ['gulf_war', 'korean_conflict', 'vietnam_war', 'world_war_ii']:
                morbidity_file = DATASOURCES_DIR + '/morbidity_{0}.csv'.format(war)
                try:
                    logger.info('Reading morbidity data for {0}'.format(war))
                    lines = [line.rstrip('\n') for line in open(morbidity_file)]
                    logger.info('Loaded {0} records from morbidity_{1}.csv'.format(len(lines), war))
                    war_lines[war] = lines
                except Exception as e:
                    logger.error('Could not open war morbidity ' + morbidity_file + ' Error: %s' % e)
                    exit(1)

        return build_problem(war_lines[patient['war']['war_code']], patient, 'war')
