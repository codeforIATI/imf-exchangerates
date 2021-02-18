## IMF Currency Rates against the U.S. Dollar

This simple scraper creates a dataset of historical IMF exchange rates to the U.S. Dollar for 168 countries. Data comes from the [IMF's International Financial Statistics](https://data.imf.org/?sk=4C514D48-B6BA-49ED-8AB9-52B0C1A0179B).

This scraper runs nightly at 5am GMT on Github Actions.

You can find the data in the gh-pages branch of this repository, or alternatively under:

https://codeforiati.org/imf-currencies/imf_rates.csv

## Notes on the data

The IMF API provides data by _country_. This means that we have to map from country to currency code. There are a couple of unpleasant steps to get there, involving using a couple of different ISO country and exchange rate codelists.

It appears that the IMF API uses the ISO 3166 Alpha-2 code for each country, which makes this process a little easier.

### Currency codes are _probably_ correct

Currencies may change from time to time. Though it is difficult to be 100% sure about this from the available documentation on the API, it appears that all of the values are in each country's most recent currency.

For example: according to [the IMF's Metadata PDF document for this dataset](https://data.imf.org/api/document/download?key=62969181), in January 1, 2005, Turkey introduced the New Turkish Lira (TRY), equivalent to 1,000,000 Turkish Lira. However, there does not appear to be any major change in the rate against the USD here.

### Euro-area countries

The one major exception to this appears to be Euro-area countries. Here, the IMF API returns data for the country _up to that country's adoption of the Euro_. In these cases, we ignore ISO's mapping of countries to currencies, because the API is providing us with the pre-Eurozone data (e.g. for France, it returns data on French Francs (FRF)).

## Installation

If you want to get the software running yourself, you can follow these steps:

1. Install a `virtualenv` and the requirements
```
virtualenv ./pyenv -p python3
source ./pyenv/bin/activate
pip3 install -r requirements.txt
```

2. Run the scraper:
```
python3 imf-currencies.py
```
