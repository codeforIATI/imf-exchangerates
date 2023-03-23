#!/usr/bin/env python
# coding: utf-8

import click
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
DEFAULT_FREQ = 'M'
DEFAULT_SOURCE = 'ENDE'
DEFAULT_TARGET = 'USD'
FIELDNAMES=['Date', 'Rate', 'Currency', 'Frequency', 'Source', 'Country code', 'Country']
ISO_COUNTRY_URL = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"
COUNTRY_CODELIST = "https://codelists.codeforiati.org/api/json/en/Country.json"
SLEEP_TIME = 0.25

# Eurozone countries need to have the old currency code specified manually.
with open('source/eurozone.csv', 'r') as eurozone_file:
    csvreader = csv.DictReader(eurozone_file)
    EUROZONE_COUNTRIES = dict([(row['country_name'], {'code': row['country_code'], 'currency': row['currency_code']}) for row in csvreader])

# Unfortunately, the XML file with currency codes which
# ISO makes available does not use country codes and does not always
# exactly match ISO's name for the country.
with open('source/missing.csv', 'r') as missing_file:
    csvreader = csv.DictReader(missing_file)
    MISSING = dict([(row['country_name'], {'code': row['country_code'], 'currency': row['currency_code']}) for row in csvreader])

# Gradually back off to allow for IMF rate limiting
# IMF API is rate-limited and allows only 10 requests every 5 seconds
# https://datahelp.imf.org/knowledgebase/articles/630877-api
def get_request(url, sleep_time, attempt=1):
    # If sleep time has crept up to 10 seconds, looks like it isn't going
    # to work this time.
    if attempt >1:
        print("Attempt {}.".format(attempt))
    if sleep_time >= 60:
        raise Exception("Unable to retrieve url {} even after waiting for {} seconds.".format(
            url, sleep_time))
    # Sleep longer the more attempts there are.
    time.sleep(sleep_time * attempt)
    try:
        json_data = requests.get(url).json()
    except json.decoder.JSONDecodeError:
        sleep_time += 0.5
        print("Slowing down to {} seconds to handle rate limiting.".format(sleep_time))
        return get_request(url, sleep_time, attempt+1)
    return json_data, sleep_time


# ## Get country codes and exchange rates and map them together

country_request, _ = get_request(COUNTRY_CODELIST, SLEEP_TIME)
country_r = country_request['data']
iso_country_r = BytesIO(requests.get(ISO_COUNTRY_URL).text.encode("utf-8"))
iso_exchange_rates = etree.parse(iso_country_r).xpath("//CcyNtry")

def get_countries_codes(update_eurozone=True, update_missing=True):
    country_codes = dict(map(lambda c: (c['name'].upper(), {'code': c['code']}), country_r))
    for country_rate in iso_exchange_rates:
        country = country_rate.find('CtryNm')
        currency = country_rate.find('Ccy')
        currency_name = country_rate.find('CcyNm')
        if (country == None) or (currency == None): continue
        if currency_name.get('IsFund') is not None: continue
        if country_codes.get(country.text):
            country_codes[country.text]['currency'] = currency.text
    if update_eurozone:
        country_codes.update(EUROZONE_COUNTRIES)
    if update_missing:
        country_codes.update(MISSING)

    countries_currencies = dict(map(lambda c: (c.get('code'), c.get('currency')), country_codes.values()))
    countries_currencies['XDR'] = 'XDR'
    return countries_currencies
countries_currencies = get_countries_codes()


# Optionally, check for countries with missing codes
#dict(filter(lambda code: code[1].get('currency')==None, country_codes.items()))


# ## Get list of recognised countries in this dataset from the IMF website


r_imf_countries, _ = get_request(IMF_CL_AREA_URL, SLEEP_TIME)
imf_countries = r_imf_countries['Structure']['CodeLists']['CodeList']['Code']

# We also want to get XDR:USD, so we cheekily include this here.
imf_countries.append({'@value': 'XDR', 'Description': {'#text': 'IMF Special Drawing Rights'}})


def fix_date(_val):
    if len(_val.split("-")) == 2:
        _year, _month = _val.split("-")
    else:
        _year, _month = _val, 12
    _year, _month = int(_year), int(_month)
    last_day_of_month = calendar.monthrange(_year, _month)[1]
    return datetime.date(_year, _month, last_day_of_month).isoformat()

def write_countries_currencies():
    with open('output/currencies_pre_eurozone.json', 'w') as countries_currencies_json:
        json.dump(get_countries_codes(), countries_currencies_json)
    with open('output/currencies.json', 'w') as countries_currencies_json:
        json.dump(get_countries_codes(update_eurozone=False), countries_currencies_json)


# ## For each country, write out monthly exchange rate data
@click.command()
@click.option('--freq', default=DEFAULT_FREQ, help='Frequency of rates. Options: A (Annual), B (Biannual), Q (Quarterly), M (Monthly), W (Weekly), D (Daily).')
@click.option('--source', default=DEFAULT_SOURCE, help='Data source. Options: ENSE (National Currency per SDR, end of period), ENSA (National Currency per SDR, average of period), ENDE (Domestic currency per target USD, end of period), ENDA (Domestic currency per target USD, average of period).')
@click.option('--target', default=DEFAULT_TARGET, help='Conversion target, Options: XDR (combined with ENSE/ENSA source), USD (combined with ENDE, ENDA source).')
def _write_monthly_exchange_rates(freq, source, target):
    write_monthly_exchange_rates(freq, source, target)
    write_countries_currencies()


def write_monthly_exchange_rates(freq, source, target):
    """ For each country, write out monthly exchange rate data.
    Using click to allow optional parameters source and target.
    """
    country_url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/{}.{}.{}_XDC_{}_RATE'
    xdr_url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/{}.US.ESD{}_XDR_USD_RATE'
    output_file = 'output/imf_exchangerates{}.csv'.format("" if source is DEFAULT_SOURCE and target is DEFAULT_TARGET
                                                          else "_{}_{}_{}".format(freq, source, target))
    os.makedirs('output', exist_ok=True)
    with open(output_file, "w") as output_csv:  # Include format statement to catch the default
        writer = csv.DictWriter(output_csv, FIELDNAMES)
        writer.writeheader()
        sleep_time = SLEEP_TIME
        for i, country in enumerate(imf_countries):
            print("Getting data for {}".format(country))
            # There is a different API URL for XDR
            # Monthly average/end of period for consistency
            if country['@value'] == 'XDR':
                rc, sleep_time = get_request(xdr_url.format(freq, source[-1]),
                    sleep_time)
            else:
                rc, sleep_time = get_request(country_url.format(freq, country['@value'], source, target),
                    sleep_time)
            dataset = rc['CompactData']['DataSet']
            if countries_currencies.get(country['@value']):
                currency_code = countries_currencies.get(country['@value'])
            else:
                currency_code = ''
            if 'Series' in dataset:
                exchange_rates_data = dataset['Series']['Obs']
                if type(exchange_rates_data) != list: continue
                for row in exchange_rates_data:
                    if '@OBS_VALUE' not in row: continue  # Safety for possible missing data for ENSA and ENDA.
                    writer.writerow({
                        'Date': fix_date(row['@TIME_PERIOD']),
                        'Rate': row['@OBS_VALUE'],
                        'Currency': currency_code,
                        'Frequency': freq,
                        'Source': 'IMF',
                        'Country code': country['@value'],
                        'Country': country['Description']['#text'],
                    })

if __name__ == "__main__":
    _write_monthly_exchange_rates()
