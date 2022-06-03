from datetime import datetime as dt


def reformatStringDate(strDate, fromFormat, toFormat):
    datetime_date = dt.strptime(strDate, fromFormat)
    str_date = datetime_date.strftime(toFormat)
    return str_date
