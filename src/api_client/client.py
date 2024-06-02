from src.api_client.utils import json_handler, csv_handler
from src.api_client import study_fields
import csv
import requests


class ClinicalTrials:
    """ClinicalTrials API client

    Provides functions to easily access the ClinicalTrials.gov API
    (https://classic.clinicaltrials.gov/api/)
    in Python.

    Attributes:
        study_fields: List of all study fields you can use in your query.
        api_info: Tuple containing the API version number and the last
        time the database was updated.
    """

    _BASE_URL = "https://clinicaltrials.gov/api/v2/"
    _JSON = "format=json"
    _CSV = "format=csv"

    def __init__(self):
        self.api_info = self.__api_info()


    @property
    def study_fields(self):
        """List of all study fields you can use in your query."""

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
    
    def __api_info(self):
        """Returns information about the API"""
        req, headers = json_handler(f"{self._BASE_URL}version")
        last_updated = req["dataTimestamp"]

        api_version = req["apiVersion"]

        return api_version, last_updated
    
    def get_full_studies(self, search_expr, max_studies=50, fmt="csv"):
            """Returns all content for a maximum of 100 study records.

            Retrieves information from the full studies endpoint, which gets all study fields.
            This endpoint can only output JSON (Or not-supported XML) format and does not allow
            requests for more than 100 studies at once.

            Args:
                search_expr (str): A string containing a search expression as specified by
                    `their documentation <https://clinicaltrials.gov/api/gui/ref/syntax#searchExpr>`_.
                max_studies (int): An integer indicating the maximum number of studies to return.
                    Defaults to 50.

            Returns:
                dict: Object containing the information queried with the search expression.

            Raises:
                ValueError: The number of studies can only be between 1 and 100
            """
            if fmt == "csv":
                format = self._CSV
                handler = csv_handler
            elif fmt == "json":
                format = self._JSON
                handler = json_handler
            else:
                raise ValueError("Format argument has to be either 'csv' or 'json")
        
            if max_studies < 1:
                raise ValueError("The number of studies can only be greater than 0")

            all_studies = []
            pageToken = None
            while len(all_studies) < max_studies:
                req = f"studies?{format}&markupFormat=legacy&query.term={search_expr}&pageSize={max_studies}"
                if pageToken:
                    req += f"&pageToken={pageToken}"
                if fmt == "json":
                    response, headers = json_handler(f"{self._BASE_URL}{req}")
                    full_studies = response['studies']
                    pageToken = response.get('nextPageToken', None)
                else:  # fmt == "csv"
                    full_studies, headers = csv_handler(f"{self._BASE_URL}{req}")
                    pageToken = headers.get('x-next-page-token', None)
                all_studies.extend(full_studies)
                if not pageToken:
                    break
            return all_studies[:max_studies]


    def get_study_fields(self, search_expr, fields, max_studies=50, fmt="csv"):
        if fmt == "json":
            format = "format=json"
            handler = json_handler
        elif fmt == "csv":
            format = "format=csv"
            handler = csv_handler
        else:
            raise ValueError("Format argument has to be either 'csv' or 'json")

        if not set(fields).issubset(self.study_fields[fmt]):
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
            url = f"{self._BASE_URL}studies?{format}{req}"
            response, headers = handler(url)
            if fmt == "json":
                full_studies = response['studies']
                pageToken = response.get('nextPageToken', None)
            else:  # fmt == "csv"
                full_studies = response
                pageToken = headers.get('x-next-page-token')
            all_studies.extend(full_studies)
            if not pageToken:
                break

        return all_studies[:max_studies]
