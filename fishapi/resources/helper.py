from datetime import datetime as dt
from flask import current_app
import json
import time


def reformatStringDate(strDate, fromFormat, toFormat):
    datetime_date = dt.strptime(strDate, fromFormat)
    str_date = datetime_date.strftime(toFormat)
    return str_date


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower(
        ) in current_app.config['ALLOWED_EXTENSIONS']

def get_value_from_cfg_file(file_path, key):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            # Melewati baris yang tidak mengandung "="
            if '=' not in line:
                continue
            
            # Memecah baris menjadi key dan value
            parts = line.strip().split('=')
            file_key = parts[0].strip()
            value = parts[1].strip()
            
            # Memeriksa apakah key cocok
            if file_key == key:
                return value
    
    # Jika key tidak ditemukan
    return None

def getAliasConnection():
    file_path = 'fishapi/../instance/settings.cfg'
    key = 'MONGODB_SETTINGS'
    str_value = get_value_from_cfg_file(file_path, key)
    dict_value =  json.loads(str_value)
    return dict_value['alias']


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
