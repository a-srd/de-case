"""Basic utilities module"""
import requests
import csv

def request_ct(url):
    """Performs a get request with error handling."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx, 5xx)
    except requests.exceptions.RequestException as ex:
        raise ex  # Re-raise the original exception to keep the error information
    except ImportError:
        raise ImportError(  # Specific error for potential missing libraries
            "Couldn't retrieve the data. Check your search expression or try again later. Ensure 'requests' library is installed."
        )
    else:
        return response

def json_handler(url):
    """Returns request in JSON format."""
    return request_ct(url).json()

def csv_handler(url):
    """Returns request in CSV format."""
    response = request_ct(url)
    decoded_content = response.content.decode("utf-8")
    
    # csv.reader expects a file-like object, not a string
    return list(csv.reader(decoded_content.splitlines(), delimiter=","))  
