# PseudoVet Randomizer and Aging

## Description
This utility script creates C-CDA compliant documents of any number of fictional patients, using random data. It has the following features:
1. Builds as many C-CDA documents as requested by command line option.
2. Ages the patient record +5, +10 and +15 years automatically.
3. Calculates death based on [life expectancy](https://en.wikipedia.org/wiki/List_of_sovereign_states_by_life_expectancy) and modifies C-CDA documents accordingly. 
4. Allows the base year to be defined as an input option, so that the patients age and profile fits to a time period. 
5. Randomly assigns a war era to a patient based on its birth date and a random age when enlisting for war.  

## Extensibility
This library uses the very powerful [Jinja2](http://jinja.pocoo.org/docs/2.10) templating engine which allows great flexibility and readability of the XML template files. Jinja2 is the most widely used templating engine by all Python developers.

I created jinja2 temlplate files for the **Continuity of Care Document (CCD)** and it would be easy to add new templates using the same library.

The templates are populated from variables read from a data source file (see `datasources/datasource.json`) which allows even more extensibility. New variables can be added to the data source and they will be readily usable in the templates.

## Demonstration video
See a demo video here https://youtu.be/8drwJ9o3OEE

## Prerequisites
1. Python 3.6.0
2. pip3 9.0.1

## Local Deployment
Extract the zip contents to a folder, and cd into that folder
```bash
unzip pseudo-vets.zip -d pseudo-vets
cd pseudo-vets
```

Make sure you are using the correct Python3 and pip3 version (see above). If using virtualenv you can do this:
```bash
virtualenv --version
mkdir ~/virtualenvs
virtualenv -p python3 ~/virtualenvs/pseudo-vets
source ~/virtualenvs/pseudo-vets/bin/activate
```

Now install the script dependencies:
```bash
# this takes a couple of minutes
pip3 install -r requirements.txt 
```

Verify the script is working and see the help screen:
```bash
python3 pseudo-vets.py --help
```
That will produce this help screen:
```bash
PseudoVet Randomizer and Aging.

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
```

## Production Build and Installation
To move to a production server, just unzip the file to a folder in the target server and make sure the script runs under a user with permissions to create the work folder (by default `./output`) and write to it.

## Verification guide
Run the script with default options like this:
```bash
python3 pseudo-vets.py 
```
You should see logs like these:
 <img src="docs/sample_logs.png" />

The script creates a work folder `./output` and each time it runs, creates a subfolder to hold the results, for example: a folder `./output/2018-01-11T163449.235942` will hold the patient files of the work session `2018-01-11T163449.235942`


### Document scoring
Any resulting document can be validated with the [C-CDA Scorecard](https://sitenv.org/scorecard/). As of version 1.0 of this script the scores are **at least 95/100**. 

### C-CDA Viewer
Useful for verification is also this online [C-CDA Viewer](http://brynlewis.org/challenge/index.htm) copy the contents of the file to verify, and paste on the text area in the web page; then click the view button above the text area. In a few seconds, you should see a screen like this one:
<img src="docs/cda_viewer.png" />


## File names
The general format of the file name is `{session_id}-{patient_number}_{age}.xml`. For each patient there will be four files: one for the base record and one for each +5, +10 and +15 aged record. File names for patient_number 1 would be like these:

- `2018-01-11T163449.235942-1.xml` the base file
- `2018-01-11T163449.235942-1_5.xml` the +5 years aged record file
- `2018-01-11T163449.235942-1_10.xml` the +10 years aged record file
- `2018-01-11T163449.235942-1_15.xml` the +15 years aged record file

## Notes
Note that if a patient *'dies'* when aging the record at +5 years, the +10 and +15 aged records will be the same as when the patient *'died'*

## Docs
The C-CDA Implementation Guide is included for convenience in `docs/C-CDAImplementationGuide.pdf`

## Licenses 
To the best of my knowledge, all libraries used are open source. The ICD-10 problems list under the folder `./datasources/ICD-10` are covered by [this license](http://apps.who.int/classifications/apps/icd/ClassificationDownloadNR/license.htm) and were downloaded from [here](ftp://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2018/)

