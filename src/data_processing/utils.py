from datetime import datetime, timedelta
import json
import pandas as pd
import pycountry
from src.api_client.client import ClinicalTrials
import os
from src.data_processing import api_cache_root

# Calculate the start date (five years ago)
start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')

today = datetime.now().strftime('%Y-%m-%d')

SEARCH_EXPR = f"AREA[StartDate]RANGE[{start_date}, {today}]"


def get_last_five_years_data():
    """
    Returns data from the last five years. If the data is cached, it loads the data from the cache.
    Otherwise, it fetches the data, caches it, and then returns it.
    """
    cache_path = api_cache_root / "last_five_years_data.csv"

    if cache_path.exists():
        return pd.read_csv(cache_path)

    ct = ClinicalTrials()
    start_date = (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')

    last_five_years = ct.get_full_studies(search_expr=SEARCH_EXPR, max_studies=500000, fmt="csv")
    df = pd.DataFrame.from_records(last_five_years[1:], columns=last_five_years[0])
    df.to_csv(cache_path, index=False)

    return df

def get_conditions():
    """
    Returns a list of conditions. If the conditions are cached, it loads the conditions from the cache.
    Otherwise, it calculates the conditions, caches them, and then returns them.
    """
    cache_path = api_cache_root / "conditions.csv"

    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)["Condition"].tolist()

    df = get_last_five_years_data()
    Novo_Conditions = df[df["Sponsor"] == "Novo Nordisk A/S"]["Conditions"].unique()
    conditions = [item for sublist in Novo_Conditions for item in sublist.split("|")]
    df_conditions = pd.DataFrame(conditions, columns=["Condition"])
    df_conditions = df_conditions[~df_conditions["Condition"].isin(["Healthy Participants", "Healthy Volunteers"])]
    conditions = df_conditions["Condition"].value_counts()
    conditions = conditions[conditions > 1].index.tolist()

    pd.DataFrame(conditions, columns=["Condition"]).to_csv(cache_path, index=False)

    return conditions

def get_competitors():
    """
    Returns a list of competitors. If the competitors are cached, it loads the competitors from the cache.
    Otherwise, it calculates the competitors, caches them, and then returns them.
    """
    cache_path = api_cache_root / "competitors.csv"
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)["Competitor"].tolist()

    df = get_last_five_years_data()
    conditions = get_conditions()
    df_filtered = df[df["Conditions"].str.contains("|".join(conditions))]
    df_filtered = df_filtered[df_filtered["Sponsor"] != "Novo Nordisk A/S"]
    df_filtered = df_filtered[df_filtered["Funder Type"] == "INDUSTRY"]
    competitors = df_filtered["Sponsor"].value_counts()[df_filtered["Sponsor"].value_counts() > 10].index.tolist()

    pd.DataFrame(competitors, columns=["Competitor"]).to_csv(cache_path, index=False)

    return competitors

def get_competitor_trials():
    """
    Returns a DataFrame of competitor trials. If the DataFrame is cached, it loads the DataFrame from the cache.
    Otherwise, it calculates the DataFrame, caches it, and then returns it.
    """
    cache_path = api_cache_root / "competitor_trials.csv"
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)

    df = get_last_five_years_data()
    studies_by_sponsor = get_studies_by_sponsor(df)
    competitor_trials_df = df[df["NCT Number"].isin([item for sublist in studies_by_sponsor.values() for item in sublist])]
    competitor_trials_df.reset_index(drop=True, inplace=True)

    competitor_trials_df.to_csv(cache_path, index=False)

    return competitor_trials_df

def get_geographic_data():
    cache_path = api_cache_root / "geographic_data.csv"
    if os.path.exists(cache_path):
        return pd.read_csv(cache_path)

    ct = ClinicalTrials()

    # Get the NCTId and LocationCountry fields
    geographic_locations = ct.get_study_fields(
        search_expr=f"AREA[StartDate]RANGE[{start_date}, {today}]",
        fields=["NCTId","LocationCountry"],
        max_studies=500000,
        fmt="json",
    )

    geo_data_list = list(extract_data(geographic_locations))

    geo_df = pd.DataFrame(geo_data_list)

    competitor_trials_df = get_competitor_trials()

    geo_df = pd.DataFrame(geo_df).merge(competitor_trials_df, on='NCT Number', how='inner')

    # Add a new column for country code
    geo_df['Country Code'] = geo_df['Country'].apply(country_to_code)

    geo_df.to_csv(cache_path, index=False)

    return geo_df

#####

def get_studies_by_sponsor(df):
    """
    Returns a dictionary of the NCT Number of the studies by sponsor.
    """
    conditions = get_conditions()
    competitors = get_competitors()
    df_competitors = df[df["Sponsor"].isin(competitors)]
    df_competitors = df_competitors[df_competitors["Conditions"].str.contains('|'.join(conditions))]
    studies_by_sponsor = df_competitors.groupby("Sponsor")["NCT Number"].apply(list).to_dict()

    return studies_by_sponsor

def map_conditions(df, column, json_path):
    # Read the JSON file into a dictionary
    with open(json_path, 'r') as file:
        condition_groups = json.load(file)

    # Create a new column in the DataFrame that contains the group names
    df['Group'] = df[column].map(condition_groups)

    # If a condition is not in the dictionary, fill it with "Other"
    df['Group'] = df['Group'].fillna('Other')

    return df

def get_competitor_trials_one_cond(json_path="cached_data/condition_groups.json"):
    """
    Processes the competitor trials DataFrame by splitting and exploding the "Conditions" column,
    filtering the DataFrame for the specified conditions, and mapping the conditions to their groups.
    """
    conditions = get_conditions()
    competitor_trials_df = get_competitor_trials()
    # Select the necessary columns
    competitor_trials_one_cond = competitor_trials_df[["NCT Number","Sponsor", "Conditions"]]

    # Split the "Conditions" column by "|" and create a new row for each string in the split
    competitor_trials_one_cond['Condition'] = competitor_trials_one_cond['Conditions'].str.split('|')
    competitor_trials_one_cond = competitor_trials_one_cond.explode('Condition')

    # Filter competitor_trials_one_cond for conditions in the list conditions
    competitor_trials_one_cond = competitor_trials_one_cond[competitor_trials_one_cond["Condition"].isin(conditions)]

    # Map the conditions to their groups
    competitor_trials_one_cond = map_conditions(competitor_trials_one_cond, 'Condition', json_path)

    return competitor_trials_one_cond

def write_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

def extract_data(geographic_locations):
    for row in geographic_locations:
        try:
            nctId = row['protocolSection']['identificationModule']['nctId']
            for location in row['protocolSection']['contactsLocationsModule']['locations']:
                country = location['country']
                yield {'NCT Number': nctId, 'Country': country}
        except KeyError:
            pass

# Function to convert country name to country code
def country_to_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None
