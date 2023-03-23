## IMF Currency Rates against the U.S. Dollar

This simple scraper creates a dataset of historical IMF exchange rates to the U.S. Dollar for 168 currencies. Data comes from the [IMF's International Financial Statistics](https://data.imf.org/?sk=4C514D48-B6BA-49ED-8AB9-52B0C1A0179B).

This scraper runs nightly at 5am GMT on Github Actions.

You can find the data in the gh-pages branch of this repository, or alternatively under:

IMF Currencies converted to USD (end of month): https://codeforiati.org/imf-exchangerates/imf_exchangerates.csv <br />
IMF Currencies converted to USD (annual average): https://codeforiati.org/imf-exchangerates/imf_exchangerates_A_ENDA_USD.csv
IMF Currencies converted to SDR (monthly average): https://codeforiati.org/imf-exchangerates/imf_exchangerates_M_ENSA_XDR.csv

## Notes on the data

The IMF API provides data by _country_. This means that we have to map from country to currency code. There are a couple of unpleasant steps to get there, involving using a couple of different ISO country and exchange rate codelists.

It appears that the IMF API uses the ISO 3166 Alpha-2 code for each country, which makes this process a little easier.

### Currency codes are _probably_ correct

Currencies may change from time to time. Though it is difficult to be 100% sure about this from the available documentation on the API, it appears that all of the values are in each country's most recent currency.

For example: according to [the IMF's Metadata PDF document for this dataset](https://data.imf.org/api/document/download?key=62969181), in January 1, 2005, Turkey introduced the New Turkish Lira (TRY), equivalent to 1,000,000 Turkish Lira. However, there does not appear to be any major change in the rate against the USD around that time.

### Euro-area countries

Euro-area countries are handled differently. Here, the IMF API returns data for the country _up to that country's adoption of the Euro_. In these cases, we ignore ISO's mapping of countries to currencies, because the API is providing us with the pre-Eurozone data (e.g. for France, it returns data on French Francs (FRF)). These are contained in the `eurozone.csv` file, which needs to be updated when a new country accedes to the Eurozone.

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

There are two optional parameters, source and target. The table below describes the options. The default behaviour is using ENDE as the source, and USD as the target. It is worth noting that for all cases XDR is appended to the end of the dataset as a conversion to USD, as converting XDR to XDR does not make sense.

| Data source description                              | Full source       | Example data | Source | Target |
|------------------------------------------------------|-------------------|--------------|--------|--------|
| National Currency per SDR, end of period             | ENSE_XDC_XDR_RATE | [SDR end](http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.NL.ENSE_XDC_XDR_RATE)         | ENSE   | XDR    |
| National Currency per SDR, average of period         | ENSA_XDC_XDR_RATE | [SDR average](http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.NL.ENSA_XDC_XDR_RATE)         | ENSA   | XDR    |
| Domestic currency per U.S. Dollar, end of period     | ENDE_XDC_USD_RATE | [USD end](http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.NL.ENDE_XDC_USD_RATE)         | ENDE   | USD    |
| Domestic currency per U.S. Dollar, average of period | ENDA_XDC_USD_RATE | [USD average](http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/M.NL.ENDA_XDC_USD_RATE)         | ENDA   | USD    |

A parameterized scraper can be called with, for example:
```
python3 imf-currencies.py --source=ENSA --target=XDR
```

## IMF Data License

This data is extracted from the International Monetary Funds (IMF)'s International Financial Statistics (IFS).

Below is an excerpt from the [IMF Copyright and Usage page](https://www.imf.org/external/terms.htm) (effective 2020-01-02, accessed 2021-02-18):

> Users may download, extract, copy, create derivative works, publish, distribute, and sell Data obtained from IMF Sites, including for commercial purposes, subject to the following conditions:
>
> * When Data is distributed or reproduced, it must appear accurately and attributed to the IMF as the source, e.g. “Source: International Monetary Fund.” This source attribution requirement is attached to any use of IMF Data, whether obtained directly from the IMF or from a User.
> * Users who make IMF Data available to other users through any type of distribution or download environment agree to take reasonable efforts to communicate and promote compliance by their end users with these terms.
> * The Data is provided to Users “as is” and without warranty of any kind, either express or implied, including, without limitation, warranties of merchantability, fitness for a particular purpose, and noninfringement.
> * If IMF Data is sold by Users as a standalone product; sellers must inform purchasers that the Data is available free of charge from the IMF.
> * Users shall not infringe upon the integrity of the Data and in particular shall refrain from any act of alteration of the Data that intentionally affects its nature or accuracy. If the Data is materially transformed by the User, this must be stated explicitly along with the required source citation.
> * The policy of free access and free reuse does not imply a right to obtain confidential or any unpublished underlying data, over which the IMF reserves all rights.
>
> Except as stated in this Section VIII, all other terms set forth in the general terms and conditions shall continue to apply to use of IMF Data.


## Dataset coverage

_As of 2021-03-03_, the earliest and latest dates in the dataset are as follows (NB for certain currencies, most notably Zimbabwe (`ZWL`), there are gaps in the data).

Currency | Earliest Date | Latest Date
--- | --- | ---
AED | 31/01/1966 | 31/01/2021
AFN | 31/01/1955 | 30/11/2020
ALL | 31/01/1992 | 31/12/2020
AMD | 30/04/1992 | 31/01/2021
ANG | 31/10/2010 | 31/01/2021
AOA | 31/01/1957 | 31/01/2021
ARS | 31/01/1959 | 31/01/2021
ATS | 31/01/1957 | 31/12/1998
AUD | 31/01/1957 | 31/01/2021
AWG | 31/01/1986 | 31/01/2021
AZN | 31/12/1992 | 31/12/2020
BAM | 31/01/1997 | 31/12/2020
BBD | 31/01/1957 | 31/01/2021
BDT | 31/01/1972 | 31/01/2021
BEF | 31/01/1957 | 31/12/1998
BGN | 31/01/1957 | 31/01/2021
BHD | 31/01/1966 | 31/01/2021
BIF | 31/01/1957 | 31/12/2020
BMD | 31/01/1940 | 31/01/2021
BND | 31/01/1957 | 31/01/2021
BOB | 31/03/1959 | 31/01/2021
BRL | 31/01/1964 | 31/01/2021
BSD | 31/01/1940 | 31/01/2021
BTN | 31/01/1957 | 31/01/2021
BWP | 31/01/1957 | 31/01/2021
BYN | 31/01/1992 | 31/12/2020
BZD | 31/01/1957 | 31/01/2021
CAD | 31/01/1957 | 31/01/2021
CDF | 31/01/1957 | 31/01/2021
CHF | 31/01/1957 | 31/01/2021
CLP | 31/01/1957 | 31/01/2021
CNY | 31/01/1957 | 31/01/2021
COP | 31/01/1957 | 31/01/2021
CRC | 31/01/1957 | 31/12/2020
CUC | 31/01/1967 | 31/08/1975
CVE | 31/01/1957 | 30/11/2020
CYP | 31/01/1957 | 31/12/2007
CZK | 31/01/1993 | 31/01/2021
DEM | 31/01/1957 | 31/12/1998
DJF | 31/01/1957 | 31/01/2021
DKK | 31/01/1957 | 31/01/2021
DOP | 31/01/1957 | 31/12/2020
DZD | 31/01/1957 | 31/01/2021
EEK | 30/06/1992 | 31/12/2010
EGP | 31/01/1957 | 30/11/2020
ERN | 28/02/1957 | 31/01/2021
ESP | 31/01/1957 | 31/12/1998
ETB | 31/01/1957 | 29/02/2020
EUR | 31/01/1999 | 31/01/2021
FIM | 31/01/1957 | 31/12/1998
FJD | 31/01/1957 | 31/01/2021
FRF | 31/01/1957 | 31/01/1999
GBP | 31/01/1957 | 31/01/2021
GEL | 31/10/1995 | 31/01/2021
GHS | 31/01/1957 | 31/12/2020
GIP | 31/01/1957 | 31/01/2021
GMD | 31/01/1957 | 31/12/2020
GNF | 31/01/1957 | 31/12/2019
GRD | 31/01/1957 | 31/12/2000
GTQ | 31/01/1957 | 31/01/2021
GYD | 31/01/1957 | 31/12/2020
HKD | 31/01/1957 | 31/01/2021
HNL | 31/01/1957 | 31/01/2021
HRK | 31/01/1992 | 31/01/2021
HUF | 31/01/1968 | 31/01/2021
IDR | 31/01/1967 | 31/01/2021
IEP | 31/01/1957 | 31/12/1998
ILS | 31/01/1957 | 31/01/2021
INR | 31/01/1957 | 31/01/2021
IQD | 31/01/1957 | 31/10/2020
IRR | 31/01/1957 | 31/01/2021
ISK | 31/01/1957 | 31/01/2021
ITL | 31/01/1957 | 31/01/2021
JMD | 31/01/1957 | 31/01/2021
JOD | 31/01/1957 | 31/01/2021
JPY | 31/01/1957 | 31/01/2021
KES | 31/01/1957 | 31/01/2021
KGS | 31/05/1993 | 31/01/2021
KHR | 31/01/1957 | 31/12/2020
KMF | 31/01/1957 | 31/01/2021
KRW | 31/01/1957 | 31/01/2021
KWD | 31/01/1957 | 31/01/2021
KYD | 31/01/1957 | 31/01/2021
KZT | 30/11/1993 | 31/01/2021
LAK | 31/01/1957 | 31/12/2020
LBP | 31/01/1957 | 31/01/2021
LKR | 31/01/1957 | 31/08/2020
LRD | 31/01/1957 | 30/06/2020
LTL | 31/01/1992 | 31/12/2014
LUF | 31/01/1957 | 31/12/1998
LVL | 29/02/1992 | 31/12/2013
LYD | 31/01/1957 | 31/05/2020
MAD | 31/01/1957 | 31/12/2020
MDL | 31/12/1991 | 31/01/2021
MGA | 31/01/1957 | 31/12/2020
MKD | 31/12/1993 | 31/01/2021
MMK | 31/01/1957 | 31/12/2020
MNT | 31/07/1990 | 31/01/2021
MOP | 31/12/1967 | 31/01/2021
MRU | 31/01/1957 | 30/09/2020
MTL | 31/01/1957 | 31/12/2007
MUR | 31/01/1957 | 31/01/2021
MVR | 31/01/1957 | 31/01/2021
MWK | 31/01/1957 | 30/09/2020
MXN | 31/01/1957 | 31/01/2021
MYR | 31/01/1957 | 31/01/2021
MZN | 31/01/1957 | 31/01/2021
NGN | 31/01/1957 | 31/12/2020
NIO | 31/01/1957 | 31/10/2020
NLG | 31/01/1957 | 30/09/2010
NOK | 31/01/1957 | 31/01/2021
NPR | 31/01/1957 | 30/09/2020
NZD | 31/01/1957 | 31/01/2021
OMR | 31/01/1957 | 31/01/2021
PEN | 31/01/1960 | 31/05/2020
PGK | 31/01/1957 | 30/11/2020
PHP | 31/01/1957 | 31/01/2021
PKR | 31/01/1957 | 31/01/2021
PLN | 31/01/1957 | 31/01/2021
PTE | 31/01/1957 | 31/12/1998
PYG | 30/09/1957 | 31/01/2021
QAR | 31/01/1966 | 31/01/2021
RON | 31/01/1957 | 31/01/2021
RSD | 31/12/1997 | 31/01/2021
RUB | 30/06/1992 | 31/01/2021
RWF | 31/01/1957 | 31/01/2021
SAR | 31/01/1957 | 31/01/2021
SBD | 31/01/1957 | 31/12/2020
SCR | 31/01/1957 | 31/12/2020
SDG | 31/01/1957 | 30/09/2020
SEK | 31/01/1957 | 31/01/2021
SGD | 31/01/1957 | 31/01/2021
SIT | 31/12/1991 | 28/02/2007
SKK | 31/01/1993 | 31/12/2008
SLL | 31/01/1957 | 31/12/2020
SOS | 31/01/1957 | 30/06/2018
SRD | 31/01/1957 | 31/12/2020
SSP | 31/07/2011 | 31/12/2020
STN | 31/01/1957 | 30/06/2020
SYP | 31/01/1957 | 30/09/2018
SZL | 31/01/1957 | 31/01/2021
THB | 31/01/1957 | 31/01/2021
TJS | 31/01/1992 | 30/11/2020
TMT | 30/11/1993 | 31/12/2001
TND | 31/01/1957 | 31/01/2021
TOP | 31/01/1957 | 31/12/2020
TRY | 31/01/1957 | 30/11/2020
TTD | 31/01/1957 | 31/01/2021
TWD | 31/01/1957 | 31/12/2020
TZS | 31/01/1957 | 30/11/2020
UAH | 31/12/1992 | 31/12/2020
UGX | 31/01/1957 | 31/01/2021
USD | 31/01/1940 | 31/01/2021
UYW | 31/01/1964 | 31/12/2020
UZS | 30/06/1999 | 31/01/2021
VES | 31/01/1957 | 30/06/2018
VND | 31/01/1957 | 31/12/2020
VUV | 31/07/1957 | 30/11/2020
WST | 31/01/1957 | 31/01/2021
XAF | 31/01/1957 | 31/01/2021
XCD | 31/01/1957 | 31/01/2021
XDR | 31/01/1940 | 31/01/2021
XOF | 31/01/1957 | 31/01/2021
XPF | 31/01/1957 | 31/01/2021
YER | 31/05/1990 | 31/01/2021
ZAR | 31/01/1957 | 31/01/2021
ZMW | 31/01/1957 | 31/01/2021
ZWL | 31/01/1957 | 31/10/2020
