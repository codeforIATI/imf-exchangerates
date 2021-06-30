import csv
import re
from urllib.request import Request, urlopen

EXISTING_URL="https://codeforiati.org/imf-exchangerates/imf_exchangerates.csv"

class TestIMFCurrencies:

    imf_currencies = __import__('imf-currencies')
    imf_currencies.write_monthly_exchange_rates()


    def test_row_numbers(self):
        """
        Check that running this code outputs the same
        number of lines as were previously generated.
        This will sometimes lead to some false negatives,
        given that the data is updated frequently.
        """
        request = Request(EXISTING_URL)
        existing_csv_len = len(urlopen(request).readlines())

        with open("output/imf_exchangerates.csv", "r") as input_csv:
            new_csv_len = len(input_csv.readlines())
            assert new_csv_len == existing_csv_len


    def _test_row_contents(self):
        """
        Confirm that every row has the correct contents.
        NB this doesn't work at the moment due to bugs, but
        it should eventually pass.
        """
        with open("output/imf_exchangerates.csv", "r") as input_csv:
            reader = csv.DictReader(input_csv)
            for i, row in enumerate(reader):
                try:
                    assert re.match(r"(\d{4})-(\d{2})-(\d{2})", row['Date'])
                    assert re.match(r"(\d+\.*\d*)", row['Rate'])
                    assert re.match(r"(\w+)", row['Currency'])
                    assert re.match(r"(\w+)", row['Frequency'])
                    assert re.match(r"(\w+)", row['Source'])
                except AssertionError as e:
                    print("Error on line {}, error was {}".format(i, e))
                    raise e
