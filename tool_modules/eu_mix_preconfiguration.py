import pandas as pd
import os
from pathlib import Path


def eu_mix_configuration_id_weight(pathway_name):
    base_dir = Path(__file__).resolve().parent
    model_config_path = "data/model_configuration.csv"

    model_configuration = pd.read_csv(model_config_path)

    eumix = ["EU-mix-2018", "EU-mix-2030", "EU-mix-2040", "EU-mix-2050"]

    model_configuration_without_EUMIX = model_configuration[
        ~model_configuration["route_name"].isin(eumix)
    ]

    # Extract the year from the pathway_name string (e.g., 'EU-mix-2030')
    year = pathway_name.split("-")[-1]

    # Compute result dictionaries
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

    # Retrieve the correct dictionary based on the extracted year
    configuration_id_EUMIX_weight = locals().get(f"result_dict_{year}", {})

    return configuration_id_EUMIX_weight
