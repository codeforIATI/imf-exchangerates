import calendar
import csv
import datetime
from functools import lru_cache
from io import BytesIO
import json
import os

import click
from lxml import etree
import requests


DEFAULT_FREQ = "M"
DEFAULT_SOURCE = "ENDE"
DEFAULT_TARGET = "USD"
FIELDNAMES = ["Date", "Rate", "Currency", "Frequency", "Source", "Country code", "Country"]


def fix_date(date_val):
    if "M" in date_val:
        year, month = date_val.split("-M")
    elif "Q" in date_val:
        year, quarter = date_val.split("-Q")
        month = int(quarter) * 3
    else:
        year, month = date_val, 12
    year, month = int(year), int(month)
    last_day_of_month = calendar.monthrange(year, month)[1]
    return datetime.date(year, month, last_day_of_month).isoformat()


def get_names_to_currencies():
    ISO_COUNTRY_URL = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"
    iso_country_r = BytesIO(requests.get(ISO_COUNTRY_URL).text.encode("utf-8"))
    iso_exchange_rates = etree.parse(iso_country_r).xpath("//CcyNtry")
    return {
        country_rate.find("CtryNm").text.upper(): country_rate.find("Ccy").text
        for country_rate in iso_exchange_rates
        if country_rate.find("CtryNm") is not None
        and country_rate.find("Ccy") is not None
        and country_rate.find("CcyNm").get("IsFund") is None
    }


@lru_cache
def get_eurozone_countries():
    with open("source/eurozone.csv", "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


@lru_cache
def get_missing_countries():
    with open("source/missing.csv", "r") as f:
        return list(csv.DictReader(f))


@lru_cache
def get_country_code_2_to_names():
    COUNTRY_CODELIST = "https://codelists.codeforiati.org/api/json/en/Country.json"
    country_request = requests.get(COUNTRY_CODELIST).json()
    return {
        c["code"]: c["name"]
        for c in country_request["data"]
    }


def get_country_code_2_to_currencies(update_eurozone=True, update_missing=True):
    country_name_to_currency = get_names_to_currencies()
    country_code_2_to_names = get_country_code_2_to_names()
    countries_to_currencies = {
        code: country_name_to_currency.get(name.upper())
        for code, name in country_code_2_to_names.items()
    }
    if update_eurozone:
        eurozone_countries = get_eurozone_countries()
        countries_to_currencies.update({
            eurozone_country["country_code_2"]: eurozone_country["currency_code"]
            for eurozone_country in eurozone_countries
        })
    if update_missing:
        missing_countries = get_missing_countries()
        countries_to_currencies.update({
            missing_country["country_code_2"]: missing_country["currency_code"]
            for missing_country in missing_countries
        })
    countries_to_currencies["XDR"] = "XDR"
    return countries_to_currencies


def get_country_code_3_to_code_2s():
    region_m49_data = requests.get("https://codelists.codeforiati.org/api/json/en/RegionM49.json").json()
    code_3_to_code_2s = {
        c["codeforiati:iso-alpha-3-code"]: c["codeforiati:iso-alpha-2-code"]
        for c in region_m49_data["data"]
    }
    code_3_to_code_2s.update({
        missing_country["country_code_3"]: missing_country["country_code_2"]
        for missing_country in get_missing_countries()
    })
    code_3_to_code_2s["XDR"] = "XDR"
    return code_3_to_code_2s


def get_country_code_3_to_names():
    IMF_CL_AREA_URL = "https://api.imf.org/external/sdmx/3.0/structure/codelist/IMF.STA/CL_ER_COUNTRY_PUB"
    r_imf_countries = requests.get(IMF_CL_AREA_URL).json()
    lookup = {c["id"]:  c["name"] for c in r_imf_countries["data"]["codelists"][0]["codes"]}
    lookup["XDR"] = "IMF Special Drawing Rights"
    return lookup


def get_exchange_rates(frequency, source, target, country="*", base="XDC"):
    if source[-1] == "E":
        # End of period
        transformation = "EOP_RT"
    else:
        # Average of period
        transformation = "PA_RT"
    url = f"https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/%2B/{country}.{base}_{target}.{transformation}.{frequency}?attributes=SCALE"
    response = requests.get(url)
    rc = response.json()
    country_codes_3 = [c["id"] for c in rc["data"]["structures"][0]["dimensions"]["series"][0]["values"]]
    time_periods = [c["value"] for c in rc["data"]["structures"][0]["dimensions"]["observation"][0]["values"]]
    exchange_rates = {}
    for series_id, series in rc["data"]["dataSets"][0]["series"].items():
        country_code_3 = country_codes_3[int(series_id.split(":", 1)[0])]
        if "observations" not in series:
            print(f"No exchange rate data found for country code: {country_code_3}")
            continue
        exchange_rates[country_code_3] = sorted([
            (time_periods[int(time_period_id)], value[0])
            for time_period_id, value in series["observations"].items()
        ])
    return exchange_rates


def write_countries_currencies():
    os.makedirs("output", exist_ok=True)
    with open("output/currencies_pre_eurozone.json", "w") as countries_currencies_json:
        json.dump(get_country_code_2_to_currencies(), countries_currencies_json)

    with open("output/currencies.json", "w") as countries_currencies_json:
        json.dump(get_country_code_2_to_currencies(update_eurozone=False), countries_currencies_json)


def get_rates_and_country_data(frequency, source, target, country="*", base="XDC"):
    exchange_rates = get_exchange_rates(frequency, source, target, country, base)
    country_code_3_to_code_2s = get_country_code_3_to_code_2s()
    country_code_2_to_currencies = get_country_code_2_to_currencies()
    country_code_3_to_names = get_country_code_3_to_names()
    data = []
    for country_code_3, exchange_rates in exchange_rates.items():
        if base == "XDR":
            country_code_3 = "XDR"
        country_name = country_code_3_to_names.get(country_code_3)
        country_code_2 = country_code_3_to_code_2s.get(country_code_3)
        currency_code = country_code_2_to_currencies.get(country_code_2)
        data.append({
            "rates": exchange_rates,
            "currency": currency_code,
            "frequency": frequency,
            "country_code_3": country_code_3,
            "country_code_2": country_code_2,
            "country_name": country_name,
        })
    return data


def write_data_for_country(frequency, source, target, country, writer):
    data = get_rates_and_country_data(frequency, source, target, country)
    if country == "*":
        if target == "USD":
            data += get_rates_and_country_data(frequency, source, target, "USA", "XDR")
        data = sorted(data, key=lambda x: x["country_name"])

    for country_data in data:
        for time_period, rate in country_data["rates"]:
            writer.writerow({
                "Date": fix_date(time_period),
                "Rate": rate,
                "Currency": country_data["currency"],
                "Frequency": country_data["frequency"],
                "Source": "IMF",
                "Country code": country_data["country_code_2"],
                "Country": country_data["country_name"],
            })


def write_monthly_exchange_rates(frequency, source, target):
    fname_suffix = (
        ""
        if source is DEFAULT_SOURCE and target is DEFAULT_TARGET
        else "_{}_{}_{}".format(frequency, source, target)
    )
    output_filename = f"output/imf_exchangerates{fname_suffix}.csv"
    os.makedirs("output", exist_ok=True)
    with open(output_filename, "w") as f:
        writer = csv.DictWriter(f, FIELDNAMES)
        writer.writeheader()

        write_data_for_country(frequency, source, target, "*", writer)


@click.command()
@click.option("--freq", default=DEFAULT_FREQ, help="Frequency of rates. Options: A (Annual), Q (Quarterly), M (Monthly).", type=click.Choice(["A", "Q", "M"], case_sensitive=False))
@click.option("--source", default=DEFAULT_SOURCE, help="Data source. Options: ENSE (National Currency per SDR, end of period), ENSA (National Currency per SDR, average of period), ENDE (Domestic currency per target USD, end of period), ENDA (Domestic currency per target USD, average of period).", type=click.Choice(["ENSE", "ENSA", "ENDE", "ENDA"], case_sensitive=False))
@click.option("--target", default=DEFAULT_TARGET, help="Conversion target, Options: XDR (combined with ENSE/ENSA source), USD (combined with ENDE, ENDA source).", type=click.Choice(["XDR", "USD"], case_sensitive=False))
def _write_monthly_exchange_rates(freq, source, target):
    if target == "USD":
        assert source[-2] == "D", "Expected source to be ENDE or ENDA for USD target."
    else:
        assert source[-2] == "S", "Expected source to be ENSA or ENSE for XDR target."
    write_monthly_exchange_rates(freq, source, target)
    write_countries_currencies()


if __name__ == "__main__":
    _write_monthly_exchange_rates()
