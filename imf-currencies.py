#!/usr/bin/env python
# coding: utf-8

import requests
import json
import csv
import time
from lxml import etree
from io import BytesIO
import os
import datetime
import calendar


IMF_CL_AREA_URL="http://dataservices.imf.org/REST/SDMX_JSON.svc/CodeList/CL_AREA_IFS_2019M03"
# FYI SEE ALSO
# http://dataservices.imf.org/REST/SDMX_JSON.svc/DataStructure/IFS_2019M03
COUNTRY_URL="http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.{}.ENDE_XDC_USD_RATE"
XDR_URL="http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.US.ESDE_XDR_USD_RATE"
FIELDNAMES=['Date', 'Rate', 'Currency', 'Frequency', 'Source', 'Country code', 'Country']
ISO_COUNTRY_URL = "https://www.currency-iso.org/dam/downloads/lists/list_one.xml"
COUNTRY_CODELIST = "https://codelists.codeforiati.org/api/json/en/Country.json"
EUROZONE_COUNTRIES = {'AUSTRIA': {'code': 'AT', 'currency': 'ATS'}, 'BELGIUM': {'code': 'BE', 'currency': 'BEF'}, 'CYPRUS': {'code': 'CY', 'currency': 'CYP'}, 'ESTONIA': {'code': 'EE', 'currency': 'EEK'}, 'FINLAND': {'code': 'FI', 'currency': 'FIM'}, 'FRANCE': {'code': 'FR', 'currency': 'FRF'}, 'FRENCH GUIANA': {'code': 'GF', 'currency': 'FRF'}, 'FRENCH SOUTHERN TERRITORIES (THE)': {'code': 'TF', 'currency': 'FRF'}, 'GERMANY': {'code': 'DE', 'currency': 'DEM'}, 'GREECE': {'code': 'GR', 'currency': 'GRD'}, 'IRELAND': {'code': 'IE', 'currency': 'IEP'}, 'ITALY': {'code': 'IT', 'currency': 'ITL'}, 'LATVIA': {'code': 'LV', 'currency': 'LVL'}, 'LITHUANIA': {'code': 'LT', 'currency': 'LTL'}, 'LUXEMBOURG': {'code': 'LU', 'currency': 'LUF'}, 'MALTA': {'code': 'MT', 'currency': 'MTL'}, 'NETHERLANDS (THE)': {'code': 'NL', 'currency': 'NLG'}, 'PORTUGAL': {'code': 'PT', 'currency': 'PTE'}, 'SLOVAKIA': {'code': 'SK', 'currency': 'SKK'}, 'SLOVENIA': {'code': 'SI', 'currency': 'SIT'}, 'SPAIN': {'code': 'ES', 'currency': 'ESP'}, 'GUADELOUPE': {'code': 'GP', 'currency': 'FRF'}, 'HOLY SEE (THE)': {'code': 'VA', 'currency': 'ITL'}, 'MARTINIQUE': {'code': 'MQ', 'currency': 'FRF'}, 'MAYOTTE': {'code': 'YT', 'currency': 'FRF'}, 'MONTENEGRO': {'code': 'ME', 'currency': 'EUR'}, 'RÉUNION': {'code': 'RE', 'currency': 'FRF'}, 'SAINT BARTHÉLEMY': {'code': 'BL', 'currency': 'FRF'}, 'SAINT MARTIN (FRENCH PART)': {'code': 'MF', 'currency': 'FRF'}, 'SAINT PIERRE AND MIQUELON': {'code': 'PM', 'currency': 'FRF'}, 'SAN MARINO': {'code': 'SM', 'currency': 'ITL'}}

# Unfortunately, the XML file with currency codes which
# ISO makes available does not use country codes and does not always
# exactly match ISO's name for the country.
MISSING = {
 "KOREA (THE DEMOCRATIC PEOPLE'S REPUBLIC OF)": {'code': 'KP', 'currency': 'KPW'},
 'KOSOVO': {'code': 'XK', 'currency': 'EUR'},
 "LAO PEOPLE'S DEMOCRATIC REPUBLIC (THE)": {'code': 'LA', 'currency': 'LAK'},
 'NETHERLANDS ANTILLES': {'code': 'AN', 'currency': 'NLG'},
 'SYRIAN ARAB REPUBLIC (THE)': {'code': 'SY', 'currency': 'SYP'},
 'TANZANIA, THE UNITED REPUBLIC OF': {'code': 'TZ', 'currency': 'TZS'}
}


# ## Get country codes and exchange rates and map them together

country_r = requests.get(COUNTRY_CODELIST).json()['data']
country_codes = dict(map(lambda c: (c['name'].upper(), {'code': c['code']}), country_r))
iso_country_r = BytesIO(requests.get(ISO_COUNTRY_URL).text.encode("utf-8"))
iso_exchange_rates = etree.parse(iso_country_r).xpath("//CcyNtry")

for country_rate in iso_exchange_rates:
    country = country_rate.find('CtryNm')
    currency = country_rate.find('Ccy')
    if (country == None) or (currency == None): continue
    if country_codes.get(country.text):
        country_codes[country.text]['currency'] = currency.text
country_codes.update(EUROZONE_COUNTRIES)
country_codes.update(MISSING)

countries_currencies = dict(map(lambda c: (c.get('code'), c.get('currency')), country_codes.values()))


# Optionally, check for countries with missing codes
#dict(filter(lambda code: code[1].get('currency')==None, country_codes.items()))


# ## Get list of recognised countries in this dataset from the IMF website


r_imf_countries=requests.get(IMF_CL_AREA_URL).json()
imf_countries = r_imf_countries['Structure']['CodeLists']['CodeList']['Code']

# We also want to get XDR:USD, so we cheekily include this here.
imf_countries.append({'@value': 'XDR', 'Description': {'#text': 'IMF Special Drawing Rights'}})

countries_currencies['XDR'] = 'XDR'

def fix_date(_val):
    _year, _month = _val.split("-")
    _year, _month = int(_year), int(_month)
    last_day_of_month = calendar.monthrange(_year, _month)[1]
    return datetime.date(_year, _month, last_day_of_month).isoformat()

# ## For each country, write out monthly exchange rate data

os.makedirs("output", exist_ok=True)
with open("output/imf_exchangerates.csv", "w") as output_csv:
    writer = csv.DictWriter(output_csv, FIELDNAMES)
    writer.writeheader()
    for i, country in enumerate(imf_countries):
        print("Getting data for {}".format(country))
        # There is a different API URL for XDR
        if country['@value'] == 'XDR':
            rc = requests.get(XDR_URL).json()
        else:
            rc = requests.get(COUNTRY_URL.format(country['@value'])).json()
        dataset = rc['CompactData']['DataSet']
        if countries_currencies.get(country['@value']):
            currency_code = countries_currencies.get(country['@value'])
        else:
            currency_code = ''
        if 'Series' in dataset:
            exchange_rates_data = dataset['Series']['Obs']
            if type(exchange_rates_data) != list: continue
            for row in exchange_rates_data:
                writer.writerow({
                    'Date': fix_date(row['@TIME_PERIOD']),
                    'Rate': row['@OBS_VALUE'],
                    'Currency': currency_code,
                    'Frequency': 'M',
                    'Source': 'IMF',
                    'Country code': country['@value'],
                    'Country': country['Description']['#text'],
                })
        # https://datahelp.imf.org/knowledgebase/articles/630877-api
        # IMF API is rate-limited and allows only 10 requests every 5 seconds
        time.sleep(0.75)

