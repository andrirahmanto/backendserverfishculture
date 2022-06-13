from datetime import datetime as dt
from flask import current_app
import time


def reformatStringDate(strDate, fromFormat, toFormat):
    datetime_date = dt.strptime(strDate, fromFormat)
    str_date = datetime_date.strftime(toFormat)
    return str_date


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower(
        ) in current_app.config['ALLOWED_EXTENSIONS']


def pad_timestamp(filename):
    name = filename.split('.')
    return name[0] + '_' + str(round(time.time())) + '.' + name[1]
