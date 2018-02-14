# PseudoVet - Convert Aging Algorithm Into REST API Python Challenge



## Local deploy

- install python3,pip3,virtualenv
  - for ubuntu, you need run `sudo apt install python3 python3-pip virtualenv`
- create python virtual env , please run below commands 
  - `mkdir venv`
  - `virtualenv -p python3 venv`
  - `source venv/bin/activate`
- install python deps, `pip3 install -r requirements.txt`



## Run

- the cli program, the cli program is the old randomizer cli program, you can use `python pseudo_vets_cli.py`,more details see *randomizer/README.md*
- the rest program, run `python3 pseudo_vets_server.py`

## Configuration

these are a lot of values need config , all values you can found in config.py

| config name                | description                              | environment key | default value                           |
| -------------------------- | ---------------------------------------- | --------------- | --------------------------------------- |
| APPLICATION_ROOT           | the rest backend endpoint route prefix   |                 | /api/v1                                 |
| LOG_LEVEL                  | the backend log level                    |                 | DEBUG                                   |
| LOG_FORMAT                 | the app log message format               |                 | %(asctime)s %(levelname)s : %(message)s |
| FLASK_RUN_MODE             | the flask run mode, DEBUG or PROD        | MODE            | PROD                                    |
| WEB_PORT                   | the flask run web port                   | PORT            | 5000                                    |
| TEMPLATES_DIR              | the jinja2 templates dir                 |                 | ./randomizer/templates                  |
| DATASOURCES_DIR            | the datasource dir path                  |                 | ./randomizer/datasources                |
| DATESET_CONFIGURATIONS_DIR | the data source configuration files store dir path |                 | ./output/datasetConfigurations          |
| GENERATED_DATASETS_DIR     | the generated datasets file dir path     |                 | ./output/generatedDatasets              |
| CONFIGURATION_PREFIX       | the datasource configuration file name prefix |                 | DatasetConfiguration                    |



## Verification Steps

- download postman(https://www.getpostman.com/) and run postman
- import *docs/pseudoVet-backend.postman_collection.json* and *docs/pseudoVet-env.postman_environment.json* and then run these endpoint.

## Video

<https://youtu.be/GWFE5N2-8Fc>