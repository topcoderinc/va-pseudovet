"""
the flask app entry py
"""
import os
from http import HTTPStatus

from flask import Flask

from config import FLASK_RUN_MODE, WEB_PORT, DATESET_CONFIGURATIONS_DIR, GENERATED_DATASETS_DIR, BASE_YEAR
from rest.controllers import init
from rest.errors import error_handler
from rest.logger import logger
from randomizer.pseudo_vets import setup_work_session

app = Flask(__name__)  # create new flask app


@app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
@app.errorhandler(HTTPStatus.NOT_FOUND)
@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
@app.errorhandler(Exception)
def app_error_handler(err):
    """
    handler all errors
    :param err: the error instance
    :return: the err json response
    """
    return error_handler(err)


if __name__ == '__main__':  # start flask app

    logger.info('check output dir ...')

    if not os.path.exists(DATESET_CONFIGURATIONS_DIR):  # check and create dirs
        os.makedirs(DATESET_CONFIGURATIONS_DIR)
    if not os.path.exists(GENERATED_DATASETS_DIR):
        os.makedirs(GENERATED_DATASETS_DIR)

    setup_work_session(GENERATED_DATASETS_DIR, BASE_YEAR)  # init randomizer
    logger.info('starting app at port= ' + str(WEB_PORT) + ', with mode= ' + FLASK_RUN_MODE)
    init(app)  # inject routers
    app.run(debug=(FLASK_RUN_MODE == 'DEBUG'), port=int(WEB_PORT))  # start run app
