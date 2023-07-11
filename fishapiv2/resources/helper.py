from datetime import datetime as dt
from datetime import timedelta
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


def getAmountFishByType(fishtype, fishlist):
    for obj in fishlist:
        if obj['type'] == fishtype:
            return obj['amount']
    return 0


def getYearToday():
    current_year = dt.today().year
    return str(current_year)

def getListDateBettwenDate(dateA, dateB):
    # Return list of datetime.date objects (inclusive) between start_date and end_date (inclusive).
    date_list = []
    while dateA < dateB:
        date_list.append(dateA)
        dateA += timedelta(days=1)
    date_list.append(dateA)
    print(date_list)
    return date_list
