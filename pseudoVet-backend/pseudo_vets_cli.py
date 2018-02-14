"""PseudoVet Randomizer and Aging.

Description:
Creates C-CDA conformant documents of fictional patients from random data and ages those records +5, +10 and +15 years

Usage:
  pseudo-vets.py [-n number] [-o output] [-y year]

Options:
    -n number       Integer number of records to create. Defaults to 1.
    -o Output       Path to the folder where the output files shall be saved to. Will be created if non existent.
     Defaults to ./output
    -y year         Base year in YYYY format to use as base for randomizing patient birth date (and thus death date).
    Defaults to 90 years before current year

    -h --help       Show this screen.
    -v --version    Show version.
"""

#
# Main entry point to the script.
# Actual script execution code starts
#
import datetime
from docopt import docopt

from rest.logger import logger
from config import GENERATED_DATASETS_DIR, BASE_YEAR
from randomizer.pseudo_vets import setup_work_session, create_files

if __name__ == '__main__':
    # Parse command line options
    options = docopt(__doc__, version='1.0.0')

    work_dir = options['-o'] or GENERATED_DATASETS_DIR
    base_year = options['-y'] or BASE_YEAR
    base_year = int(base_year)

    # be sure to create patients of at least 20 years of age
    # we subtract 35 years to have 20 of age minus 15 of random margin used in
    # random_patient()
    year_lower_bound = datetime.datetime.now().year - 35
    if base_year > year_lower_bound:
        logger.error('Base year should be less than {0} to build significant patients.'.format(year_lower_bound))
        exit(1)

    num_records = options['-n'] or 1
    num_records = int(num_records)

    # setup a new empty folder under work_dir for this session and load data sources
    setup_work_session(work_dir, base_year)

    logger.info('Creating {0} fictional patients with base year {1}.\n'.format(num_records, base_year))

    # build num_records patients
    for i in range(1, num_records + 1):
        # create the files for a new record (patient)
        create_files(i)
        logger.info('Created {0} fictional patients in folder {1}'.format(num_records, work_dir))
