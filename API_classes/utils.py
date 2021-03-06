from email.contentmanager import raw_data_manager
import json
import datetime
import re
from bs4 import BeautifulSoup
import pytz
import requests
import urllib3
import pytz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TWITTER_FOLDER = '1lLBCk9CxaCKLyOb8Wwagge05t6f-yNRc'

def write_dict_to_file(FILE_name, dict):
        with open(FILE_name, "a") as outfile:
                    json.dump(dict, outfile,indent=4)

def get_current_date():
    time_t = datetime.datetime.now(datetime.timezone.utc)
    time_t = time_t - datetime.timedelta(microseconds=time_t.microsecond)
    return time_t

def get_current_date_string():
    time_t = datetime.datetime.now(datetime.timezone.utc)
    time_t = time_t - datetime.timedelta(microseconds=time_t.microsecond)
    return str(time_t)

def string_to_datetime(string_date):
    return datetime.datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S%z')
    
# Funcion para leer el archivo Json que contiene la informacion con las incidencias BGP
def parseJson(json_cntent):
    # Apertura y lectura del archivo Json correspondiente y almacenado localmente
    # with open(filename)as json_file:
    #     raw_data  = json.load(json_file)

    raw_data = json_cntent
    
    # Inicializacion de listas que seleccionaran la informacion que sera tratada en la aplicacion
    country = []
    ot_data = []
    country_iso2 = []

    # Obtencion de las fechas mas reciente y mas antigua para limitar el calendario de la aplicacion
    try:
        recent_date= string_to_datetime(raw_data['most_recent_date'])
        oldest_date= string_to_datetime(raw_data['oldest_date'])
    except:
        recent_date= get_current_date()
        oldest_date= get_current_date()

    # Poblado de datos con la informacion del Json, para que sea mas facil de tratar
    for k in raw_data.keys():
        if k not in ["oldest_date", "most_recent_date"]:
            country.append(raw_data[k]['ctry_fullname'])
            country_iso2.append(k)
            ot_data.append(raw_data[k]['OT_count'])

    return country, country_iso2, raw_data, ot_data, oldest_date, recent_date


def webscapp(url):
    req = requests.get(url.replace('\u2026',''), verify=False)
    netx_url = req.url
    response = requests.get(netx_url, verify=False)
    response = BeautifulSoup(response.content, "html.parser")
    html_body = response.body
    ret = []
    try:
        for item in html_body.strings:
            if item != '\n':
                ret.append(item.replace('\n','').strip())
    except:
        ret = ['URL NOT REACHABLE','URL NOT REACHABLE','URL NOT REACHABLE']
    
    return ret

def get_hj_characteristics(url):
    try:
        html_body_strings = webscapp(url)

        # Expresion regular para extraer la informacion del as_path
        regex = re.compile(r'^Detected AS Path',re.IGNORECASE)
        regex_to_sub = re.compile(r'^Detected AS Path',re.IGNORECASE)
        # obtenemos el as_path
        as_path = [regex_to_sub.sub("",i).split(" ") for i in html_body_strings if regex.match(i)]


        return as_path
        
    except:
        return []

def get_ot_characteristics(url):
    try:
        html_body_strings = webscapp(url)

        # Expresion regular para extraer la informacion 
        regex = re.compile(r'^Beginning at',re.IGNORECASE)
        regex_to_sub = re.compile(r'^Beginning at',re.IGNORECASE)
        # obtenemos 
        important_info = [regex_to_sub.sub("",i) for i in html_body_strings if regex.match(i)]


        regex = re.compile(r'^Start time:',re.IGNORECASE)
        regex_to_sub = re.compile(r'^Start time:',re.IGNORECASE)
        start_time = [regex_to_sub.sub("",i) for i in html_body_strings if regex.match(i)]

        regex = re.compile(r'^End time:',re.IGNORECASE)
        regex_to_sub = re.compile(r'^End time:',re.IGNORECASE)
        end_time = [regex_to_sub.sub("",i) for i in html_body_strings if regex.match(i)]


        return important_info, start_time, end_time
    except:
        return ['URL NOT REACHABLE','URL NOT REACHABLE','URL NOT REACHABLE']

