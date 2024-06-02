"""Basic utilities module"""
import requests
import csv
import re
import json
import sys


def request_ct(url):
    """Performs a get request that provides a (somewhat) useful error message."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as ex:
        raise ex
    except ImportError:
        raise ImportError(
            "Couldn't retrieve the data, check your search expression or try again later."
        )
    else:
        return response

def json_handler(url):
    """Returns request in JSON (dict) format and headers"""
    response = request_ct(url)
    return response.json(), response.headers

def csv_handler(url):
    """Returns request in CSV (list of records) format and headers"""
    response = request_ct(url)
    decoded_content = response.content.decode("utf-8")
    csv.field_size_limit(sys.maxsize)
    cr = csv.reader(decoded_content.splitlines(), delimiter=",")
    records = list(cr)
    return records, response.headers