import pandas as pd
import os
from pathlib import Path


def eu_mix_configuration_id_weight(pathway_name):
    """
    Returns a dictionary mapping configuration_id to weighted share (%) 
    for a given EU-mix year (e.g., 'EU-mix-2030'), based on model_configuration.csv.

    Parameters:
        pathway_name (str): Name of the EU-mix pathway (e.g., 'EU-mix-2040').

    Returns:
        dict: configuration_id → route weight (as a percentage).
    """

    # Define the path to the CSV file relative to this script
    base_dir = Path(__file__).resolve().parent
    model_config_path = "data/model_configuration.csv"

    # Load the configuration data
    model_configuration = pd.read_csv(model_config_path)

    # List of known EU-mix route names (we want to exclude these from calculations)
    eumix = ["EU-mix-2018", "EU-mix-2030", "EU-mix-2040", "EU-mix-2050"]

    # Filter out rows that correspond to EU-mix routes
    model_configuration_without_EUMIX = model_configuration[
        ~model_configuration["route_name"].isin(eumix)
    ]

    # Extract the year from the pathway name (e.g. '2030' from 'EU-mix-2030')
    year = pathway_name.split("-")[-1]

    # Create dictionaries mapping configuration_id to weight (%) for each target year
    result_dict_2018 = {}
    for _, row in model_configuration_without_EUMIX.iterrows():
        if row["mix_2018"] != 0:
            result_dict_2018[row["configuration_id"]] = row["mix_2018"] * 100

    result_dict_2030 = {}
    for _, row in model_configuration_without_EUMIX.iterrows():
        if row["mix_2030"] != 0:
            result_dict_2030[row["configuration_id"]] = row["mix_2030"] * 100

    result_dict_2040 = {}
    for _, row in model_configuration_without_EUMIX.iterrows():
        if row["mix_2040"] != 0:
            result_dict_2040[row["configuration_id"]] = row["mix_2040"] * 100

    result_dict_2050 = {}
    for _, row in model_configuration_without_EUMIX.iterrows():
        if row["mix_2050"] != 0:
            result_dict_2050[row["configuration_id"]] = row["mix_2050"] * 100

    # Dynamically select the appropriate dictionary for the requested year
    configuration_id_EUMIX_weight = locals().get(f"result_dict_{year}", {})

    return configuration_id_EUMIX_weight
