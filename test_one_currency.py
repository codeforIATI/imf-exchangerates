import csv
import os
import pytest


EXISTING_URL="https://codeforiati.org/imf-exchangerates/imf_exchangerates.csv"

class TestOneCurrency:
    def setup_class(cls):
        imf_currencies = __import__("imf-currencies")
        os.makedirs("output", exist_ok=True)
        with open("output/imf_exchangerates_one_currency.csv", "w") as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=imf_currencies.FIELDNAMES)
            writer.writeheader()
            imf_currencies.write_data_for_country(
                frequency="M",
                source="ENDE",
                target="USD",
                country="G163",
                writer=writer,
            )

    @pytest.fixture
    def countries_currencies(self):
        imf_currencies = __import__("imf-currencies")
        return imf_currencies.get_country_code_2_to_currencies()


    @pytest.fixture
    def imf_countries(self):
        imf_currencies = __import__("imf-currencies")
        return imf_currencies.get_country_code_3_to_names()


    def test_first_row(self):
        """
        Check that the first row outputs the expected data.
        """

        with open("output/imf_exchangerates_one_currency.csv", "r") as input_csv:
            reader = csv.DictReader(input_csv)
            assert next(reader) == {
                "Date": "1999-01-31",
                "Rate": "0.8784258608573436",
                "Currency": "EUR",
                "Frequency": "M",
                "Source": "IMF",
                "Country code": "U2",
                "Country": "Euro Area (EA)"
            }

    def test_currency_list(self, countries_currencies):
        """
        Check that there are a lot of countries/currencies listed.
        """

        # At the last count, it was 259. We shouldn't expect it
        # to vary greatly from this.
        assert len(countries_currencies) > 250


    def test_currency_list_contains(self, countries_currencies):
        """
        Check that the list of countries/currencies contains the Eurozone.
        """

        assert "U2" in countries_currencies.keys()


    def test_currency_list_eurozone_countries(self, countries_currencies):
        """
        Check that the list of Eurozone countries/currencies is as expected.
        """
        countries = [k for k, v in countries_currencies.items() if v == "EUR"]
        assert countries == ["AX", "AD", "XK", "MC", "ME", "U2"]
        # Aland Islands, Andorra, Kosovo, Monaco, Montenegro all use EUR but are not members
        assert len([v for k, v in countries_currencies.items() if v == "EUR"]) == 6

