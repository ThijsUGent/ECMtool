import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import calendar
import plotly.express as px


def profile_load():
    st.title("Industrial Load Profile Matching")

    st.subheader("Renewable Profile Selection")

    country = st.text_input("Enter country code (e.g. 'DE')", value="BE")
    NUTS2 = st.text_input("Or enter NUTS2 region code (e.g. 'BE23')")
    scenario = st.select_slider("ENSPRESO Scenario", ["high", "medium", "low"])

    if not country and not NUTS2:
        st.warning("Please enter either a country code or a NUTS2 code.")
        return
    if NUTS2:
        energy_vol_enspreso_solar, energy_vol_enspreso_wind = enspreso_extract(
            NUTS2, scenario)
    else:
        energy_vol_enspreso_solar = None
        energy_vol_enspreso_wind = None
    solar_default = float(
        energy_vol_enspreso_solar) if energy_vol_enspreso_solar else 1.0
    wind_default = float(
        energy_vol_enspreso_wind) if energy_vol_enspreso_wind else 1.0
    energy_volume_solar = st.number_input(
        "Set solar energy volume (TWh)", value=solar_default)
    energy_volume_wind = st.number_input(
        "Set onshore wind energy volume (TWh)", value=wind_default)
    year = st.slider("Select year for solar/wind data", 1986, 2015, 2015)

    # Load generation profiles
    solar_profile, solar_time = solar_generation(
        country=country, NUTS2=NUTS2, energy_volume=energy_volume_solar, year=year)
    wind_profile, wind_time = onshore_generation(
        country=country, NUTS2=NUTS2, energy_volume=energy_volume_wind, year=year)

    df_solar = pd.DataFrame(
        {"Time": pd.to_datetime(solar_time) if solar_time is not None else pd.Series(dtype='datetime64[ns]'), "Solar": solar_profile})
    df_wind = pd.DataFrame(
        {"Time": pd.to_datetime(wind_time) if wind_time is not None else pd.Series(dtype='datetime64[ns]'), "Wind": wind_profile})

    if df_solar.empty or df_wind.empty:
        st.warning("No solar or wind data for selected year.")
        return

    # Load industry profile
    data_source = st.radio("Select industry data source", ["ELMAS", "JERICHO"])
    if data_source == "JERICHO":
        sector = st.radio(
            "Select a sector",
            [
                "Food", "Glass, Ceramics, Stones", "Automotive", "Chemical",
                "Paper", "Mechanical Engineering", "Iron, Steel", "Other Industry"
            ]
        )
        profile, time, label = jericho_data(sector)
    else:
        profile, time, label = elmas_data()

    if profile is None or time is None:
        return

    # Create hourly datetime index starting at Jan 1 of selected year
    start_time = pd.Timestamp(f"{year}-01-01 00:00")
    time_year = pd.date_range(
        start=start_time, periods=len(time), freq="H")
    df_industry = pd.DataFrame(
        {"Time": time_year, "Industry": profile})

    if df_industry.empty:
        st.warning("No industry data available for selected year.")
        return

    unit = st.radio("Target energy unit", ["GJ", "TWh"], index=1)
    target_energy = st.number_input(
        f"Set target energy ({unit})", value=3.6)
    if unit == "TWh":
        target_energy *= 3.6e6  # Convert to GJ

    # Scale and convert to MWh
    industry_scaled = scale_profile_to_energy(
        df_industry["Industry"].values, target_energy) / 3.6
    df_industry["Industry"] = industry_scaled

    # Merge all on Time (inner join to keep common times)
    df = df_solar.merge(df_wind, on="Time", how="inner")
    df = df.merge(df_industry[["Time", "Industry"]], on="Time", how="inner")

    # Compute renewables and mismatch
    df["Renewables"] = df["Solar"] + df["Wind"]
    df["Mismatch"] = np.where(
        df["Renewables"] < df["Industry"], df["Industry"] - df["Renewables"], 0)
    energy_deficit_TWh = df["Mismatch"].sum() / 1e6  # MWh → TWh

    st.markdown(
        f"### ⚠️ Total Energy Deficit in {year}: **{energy_deficit_TWh:.2f} TWh**")

    # Curve selection checkboxes
    st.markdown("### 📊 Select Curves to Display")
    show_industry = st.checkbox("Show Industry", value=True)
    show_renewables = st.checkbox("Show Renewables (Total)", value=True)
    show_solar = st.checkbox("Show Solar", value=False)
    show_wind = st.checkbox("Show Wind", value=False)
    show_deficit = st.checkbox("Show Deficit (Mismatch)", value=False)

    y_columns = []
    line_colors = {}

    if show_renewables:
        y_columns.append("Renewables")
        line_colors["Renewables"] = "green"
    if show_solar:
        y_columns.append("Solar")
        line_colors["Solar"] = "orange"  # yellow/orange
    if show_wind:
        y_columns.append("Wind")
        line_colors["Wind"] = "blue"
    if show_industry:
        y_columns.append("Industry")
        line_colors["Industry"] = "grey"

    if not y_columns and not show_deficit:
        st.warning("Please select at least one curve to display.")
        return

    fig = go.Figure()

    # Add selected energy profiles with colors
    for col in y_columns:
        fig.add_trace(go.Scatter(
            x=df["Time"],
            y=df[col],
            mode="lines",
            name=col,
            line=dict(color=line_colors[col])
        ))

    # Add deficit area if selected
    if show_deficit:
        fig.add_trace(go.Scatter(
            x=df["Time"],
            y=df["Mismatch"],
            name="Deficit",
            mode="lines",
            line=dict(width=0),
            fill="tozeroy",
            fillcolor="rgba(255,0,0,0.3)",
            hoverinfo="skip"  # optional: avoid hover clutter
        ))
    fig.update_layout(
        title=f"Port of Antwerp profile load EU-MIX-2050 (106 TWh) with RES BE23",
        xaxis_title="Time",
        yaxis_title="Energy (MW)",
        legend_title="Profile",
        xaxis=dict(
            tickformat="%H:%M<br>%d %b",  # hour:minute, line break, day and abbreviated month
            tickmode="auto"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def scale_profile_to_energy(profile, target_energy):
    current_total = np.sum(profile)
    if current_total == 0:
        raise ValueError("Profile sum is zero — cannot scale.")
    return profile * (target_energy / current_total)


def elmas_data():
    df_time_cluster = pd.read_csv(
        "data/ELMAS_dataset/Time_series_18_clusters.csv", sep=";")
    df_cluster_NACE = pd.read_csv(
        "data/ELMAS_dataset/Clusters_after_manual_reclassification.csv", sep=";")
    # df_nace = pd.read_csv(
    #     "data/ELMAS_dataset/NACE_classification.csv", sep=';')

    # df_cluster_NACE["Class_description"] = df_cluster_NACE["Class"].map(
    #     df_nace.set_index("Class")["Class_description"]
    # )
    # st.write(df_cluster_NACE[df_cluster_NACE["Cluster"] == 1])
    df_time_cluster["Industry"] = df_time_cluster["1"].str.replace(
        ",", ".", regex=False).astype(float)
    profile = df_time_cluster["Industry"].values
    time = df_time_cluster["Time"]
    profile = np.array(profile, dtype=float) * 0.0036  # kWh to GJ
    return profile, time, "ELMAS baseyear 2018"


def jericho_data(sector):
    df_industry = pd.read_csv(
        "data/E-JERICHO/industrial_standard_load_profiles.csv")

    if sector not in df_industry.columns:
        st.warning("Sector not found in dataset.")
        return None, None, None

    profile = df_industry[sector].astype(float)
    df_industry["datetime"] = pd.to_datetime(
        "2022-01-01") + pd.to_timedelta(df_industry["hour"], unit="h")
    time = df_industry["datetime"]

    return profile, time, sector


def solar_generation(country, energy_volume, year, NUTS2=None):
    if NUTS2:
        data_source = pd.read_csv("data/EMHIRES/EMHIRES_PVGIS_TSh_CF_n2_19862015_reformatt.csv",
                                  usecols=["time_step", NUTS2])
        start_date = pd.Timestamp("1986-01-01")
        data_source["Date"] = pd.to_timedelta(
            data_source["time_step"], unit="h") + start_date
        country = NUTS2
    else:
        data_source = pd.read_csv(
            "data/EMHIRES/EMHIRESPV_TSh_CF_Country_19862015.csv", usecols=["Date", country])
        data_source["Date"] = pd.to_datetime(
            data_source["Date"], dayfirst=True)
    data_source = data_source[data_source["Date"].dt.year == year]

    if NUTS2:
        if NUTS2 not in data_source.columns:
            st.warning("NUTS2 region not found in dataset.")
            return None, None
        capacity_factor_profile = data_source[NUTS2]
    else:
        if country not in data_source.columns:
            st.warning("Country not found in dataset.")
            return None, None
        capacity_factor_profile = data_source[country]

    profile = capacity_factor_profile * \
        (energy_volume * 1e6 / capacity_factor_profile.sum())

    time = data_source["Date"]

    return profile, time


def onshore_generation(country, energy_volume, NUTS2=None, year=None):
    if NUTS2:
        data_source = pd.read_csv(
            "data/EMHIRES/EMHIRES_WIND_NUTS2_June2019.csv", usecols=["Time step", NUTS2])
        start_date = pd.Timestamp("1986-01-01")
        data_source["Date"] = pd.to_timedelta(
            data_source["Time step"], unit="h") + start_date
        data_source["Date"] = pd.to_datetime(
            data_source["Date"], dayfirst=True)
        data_source = data_source[data_source["Date"].dt.year == year]
        country = NUTS2

    else:
        data_source = pd.read_csv(
            "data/EMHIRES/EMHIRES_WIND_COUNTRY_June2019.csv", usecols=["Date", country])

        # Format: "dd/mm/yyyy"
        data_source["Date"] = pd.to_datetime(
            data_source["Date"], format="%d/%m/%Y")

        # Add an hourly time per row (0 to 23, repeated for each day)
        num_rows = len(data_source)
        hours = list(range(24)) * (num_rows // 24)

        # Ensure list matches dataframe length
        if len(hours) < num_rows:
            hours += list(range(num_rows - len(hours)))

        # Add 'DateTime' with hourly resolution
        data_source["Date"] = data_source["Date"] + \
            pd.to_timedelta(hours, unit="h")
        # Select year
        data_source = data_source[data_source["Date"].dt.year == year]
    if NUTS2:
        if NUTS2 not in data_source.columns:
            st.warning("NUTS2 region not found in dataset.")
            return None, None
        capacity_factor_profile = data_source[NUTS2]
    else:
        if country not in data_source.columns:
            st.warning("Country not found in dataset.")
            return None, None
        capacity_factor_profile = data_source[country]

    profile = capacity_factor_profile * \
        (energy_volume * 1e6 / capacity_factor_profile.sum())

    # Assume 'Date' is the start date (e.g. 2015-01-01), same for all rows
    start_date = pd.to_datetime(data_source["Date"].iloc[0])

    time = data_source["Date"]

    return profile, time


def offshore_generation(country):
    data_source = pd.read_csv("PATH")
    # This function is not yet implemented.
    pass


def enspreso_extract(NUTS2, level):
    col = [
        "nuts2_code",
        f"wind_onshore_production_twh_{level}",
        f"solar_production_twh_{level}_total"
    ]
    df = pd.read_csv(
        "data/ENSPRESO/ENSPRESO_Integrated_NUTS2_Data2021.csv", usecols=col)
    df_filter = df[df["nuts2_code"] == NUTS2]

    if df_filter.empty:
        return None, None

    wind_series = df_filter[col[1]]
    solar_series = df_filter[col[2]]

    # Get the first (and presumably only) value as float, or None if missing
    wind = float(wind_series.iloc[0]) if not wind_series.empty else None
    solar = float(solar_series.iloc[0]) if not solar_series.empty else None

    return solar, wind
