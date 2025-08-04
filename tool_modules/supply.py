import streamlit as st
import pandas as pd
import geopandas as gpd

# Function to clean and convert numeric columns


def clean_numeric_column(series):
    return (
        series.astype(str)
        .str.replace(" ", "", regex=False)   # remove thousands separator
        .str.replace(",", ".", regex=False)  # standardise decimal point
        .replace(":", None)                  # treat ":" as missing
        .astype(float)
    )


def eurostat_production():
    # Import production 2023 data
    NUTS3_solar_MWh_m2_2023 = pd.read_csv(
        "data/Energy_production/Solar_MWh_m2_2023.csv")
    NUTS3_wind_MWh_m2_2023 = pd.read_csv(
        "data/Energy_production/WindOnshore_MWh_m2_2023.csv")

    # Import geometry and area NUTS3 data
    NUTS3_area = pd.read_excel(
        "data/NUTS/NUTS3_area.xlsx", sheet_name="Sheet 1", skiprows=9)
    NUTS3_area.rename(columns={
        NUTS3_area.columns[1]: "Area (m2)",
        NUTS3_area.columns[0]: "Region name"  # assuming this is "GEO (Labels)"
    }, inplace=True)

    # Merge solar and wind on "Region name"
    production_df = pd.merge(
        NUTS3_solar_MWh_m2_2023,
        NUTS3_wind_MWh_m2_2023,
        on="Region name",
        suffixes=("_solar", "_wind")
    )

    # Merge with area data on "Region name"
    production_NUTS3 = pd.merge(
        production_df,
        NUTS3_area[["Region name", "Area (m2)"]],
        on="Region name",
        how="left"
    )
    # Apply cleaning
    production_NUTS3["Value_wind"] = clean_numeric_column(
        production_NUTS3["Value_wind"])
    production_NUTS3["Value_solar"] = clean_numeric_column(
        production_NUTS3["Value_solar"])
    production_NUTS3["Area (m2)"] = clean_numeric_column(
        production_NUTS3["Area (m2)"])

    production_NUTS3["Wind Onshore (MWh)"] = production_NUTS3["Value_wind"] * \
        production_NUTS3["Area (m2)"]
    production_NUTS3["Solar (MWh)"] = production_NUTS3["Value_solar"] * \
        production_NUTS3["Area (m2)"]

    production_NUTS3["Wind Onshore (MWh)"] = production_NUTS3["Value_wind"] * \
        production_NUTS3["Area (m2)"]
    production_NUTS3["Solar (MWh)"] = production_NUTS3["Value_solar"] * \
        production_NUTS3["Area (m2)"]
    production_NUTS3 = production_NUTS3[[
        "NUTS_solar", "Region name", "Wind Onshore (MWh)", "Solar (MWh)"]]
    production_NUTS3.rename(columns={
        "NUTS_solar": "NUTS3",
    }, inplace=True)
    # Display data

    return production_NUTS3


def enspreso():
    # Import ENSPRESO data
    enspreso_df = pd.read_csv(
        "data/ENSPRESO/enspreso_data.csv", encoding="latin1")


gdf_NUTS2_POLYGON = gpd.read_file(
    "data/NUTS/NUTS_RG_20M_2021_4326/NUTS_RG_20M_2021_4326.shp"
)


def supply():
    st.title("Renewable Energy Sources (RES) Analysis")

    production_NUTS3 = eurostat_production()
