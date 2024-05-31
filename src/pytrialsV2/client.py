from pytrials.utils import json_handler, csv_handler
from pytrials import study_fields
import csv
import requests
from io import StringIO

class ClinicalTrials:
    """ClinicalTrials API client"""

    _BASE_URL = "https://clinicaltrials.gov/api/v2/"

    def __init__(self):
        self.api_info = self._get_api_info()
        self.study_fields = self._load_study_fields()

    def _load_study_fields(self):
        """Loads available study fields from CSV."""
        csv_fields = []
        json_fields = []
        with open(study_fields, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_fields.append(row["Column Name"])
                json_fields.append(row["Included Data Fields"].split("|"))
        return {
            "csv": csv_fields,
            "json": [item for sublist in json_fields for item in sublist],
        }

    def _get_api_info(self):
        """Fetches API version and last update timestamp."""
        req = json_handler(f"{self._BASE_URL}version")
        return req["apiVersion"], req["dataTimestamp"]

    def get_full_studies(search_expr, max_studies=50, fmt="json"):
        if fmt == "json":
            format = "format=json"
            handler = json_handler
        elif fmt == "csv":
            format = "format=csv"
            handler = csv_handler
        else:
            raise ValueError("Format argument has to be 'json")

        if max_studies < 1:
            raise ValueError("The number of studies can only be greater than 0")

        all_studies = []
        pageToken = None
        while len(all_studies) < max_studies:
            req = f"studies?{format}&markupFormat=legacy&query.term={search_expr}&pageSize={max_studies}"
            if pageToken:
                req += f"&pageToken={pageToken}"
            if fmt == "json":
                response = json_handler(f"https://clinicaltrials.gov/api/v2/{req}")
                full_studies = response['studies']
                if 'nextPageToken' in response:
                    pageToken = response['nextPageToken']
            else:  # fmt == "csv"
                response = requests.get(f"https://clinicaltrials.gov/api/v2/{req}")
                csv_reader = csv.reader(StringIO(response.text))
                full_studies = list(csv_reader)
                pageToken = response.headers.get('x-next-page-token')
            all_studies.extend(full_studies)
            if not pageToken:
                break
        return all_studies[:max_studies]

    def get_study_fields(search_expr, fields, max_studies=50, fmt="csv"):
        if fmt == "json":
            format = "format=json"
            handler = json_handler
        elif fmt == "csv":
            format = "format=csv"
            handler = csv_handler
        else:
            raise ValueError("Format argument has to be either 'csv' or 'json")

        if not set(fields).issubset(study_fields[fmt]):
            raise ValueError(
                "One of the fields is not valid!"
                "Check the study_fields attribute for a list of valid ones."
                "They are different depending on the return format, json or csv."
            )

        all_studies = []
        pageToken = None
        while len(all_studies) < max_studies:
            concat_fields = "|".join(fields)
            req = f"&query.term={search_expr}&markupFormat=legacy&fields={concat_fields}&pageSize={max_studies}"
            if pageToken:
                req += f"&pageToken={pageToken}"
            url = f"https://clinicaltrials.gov/api/v2/studies?{format}{req}"
            response = handler(url)
            if fmt == "json":
                full_studies = response['studies']
                if 'nextPageToken' in response:
                    pageToken = response['nextPageToken']
            else:  # fmt == "csv"
                full_studies = response
                pageToken = response.headers.get('x-next-page-token')
            all_studies.extend(full_studies)
            if not pageToken:
                break

        return all_studies[:max_studies]
