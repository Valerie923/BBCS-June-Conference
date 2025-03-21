import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry_convert as pc

@st.cache_data
def load_and_process_data():
    # CO2 Emissions Data
    df1 = pd.read_excel('CO2_Emissions.xlsx')[17:]  # Start from the 17th row
    df1 = df1[['Unnamed: 1', 'Unnamed: 4']].rename(columns={'Unnamed: 1': 'Country and Area', 'Unnamed: 4': '% change since 1990'})
   
    # Mining Data
    df2 = pd.read_excel('Contribution of mining to value added.xlsx', sheet_name='Data').dropna()
    df2 = df2[['Country and area', 2018]].rename(columns={2018: 'Mining', 'Country and area': 'Country and Area'})
   
    # Forest Area Data
    df3 = pd.read_excel('Forest Area.xlsx', sheet_name="data").dropna()
    df3 = df3[['CountryID', 'Country and Area', 'Forest Area as a Proportion of Total Land Area, 2020']]
    df3.rename(columns={'Forest Area as a Proportion of Total Land Area, 2020': 'Forest'}, inplace=True)
   
    # Marine Protected Areas Data
    df4 = pd.read_excel('Marine protected areas.xlsx', sheet_name="Data").dropna()
    df4 = df4[['CountryID', 'Country and area', 'Marine protected areas']].rename(columns={'Country and area': 'Country and Area'})
   
    # Terrestrial Protected Areas Data
    df5 = pd.read_excel('Terrestrial protected areas.xlsx', sheet_name="Data").dropna()
    df5 = df5[['CountryID', 'Country and area', 'Terrestrial protected areas']].rename(columns={'Country and area': 'Country and Area'})
   
    # Merge all dataframes
    merged_df = pd.merge(df1, df2, on='Country and Area')
    merged_df = pd.merge(merged_df, df3, on='Country and Area')
    merged_df = pd.merge(merged_df, df4, on='Country and Area')
    merged_df = pd.merge(merged_df, df5, on='Country and Area')

    # Remove duplicate columns
    merged_df = merged_df.drop(["CountryID_x", "CountryID_y"], axis=1)
   
    # Add region based on country name
    def get_region(country_name):
        try:
            country_code = pc.country_name_to_country_alpha2(country_name)
            continent_code = pc.country_alpha2_to_continent_code(country_code)
            continent_map = {
                "AF": "Africa", "AS": "Asia", "EU": "Europe", "NA": "North America", "SA": "South America", "OC": "Oceania"
            }
            return continent_map.get(continent_code, "Unknown")
        except:
            return "Unknown"
   
    merged_df["Region"] = merged_df["Country and Area"].apply(get_region)
    merged_df = merged_df[merged_df["Region"] != "Unknown"]
   
    return merged_df

# Load forest and mining data for the regions
forestdf = pd.read_csv('region_forest_means.csv')
miningdf = pd.read_csv('region_mining_means.csv')

# Rename columns in forest data for clarity
forestdf = forestdf.rename(columns={
    'Forest Area, 1990': '1990',
    'Forest Area, 2000': '2000',
    'Forest Area, 2010': '2010',
    'Forest Area, 2015': '2015',
    'Forest Area, 2020': '2020'
})

# Streamlit title and initial message
st.title("Welcome to Biodiversity Warrior!")
st.subheader("Ready to play your part in saving biodiversity?")
st.write("Select your region to explore key statistics and understand the risks affecting biodiversity.")

# Dropdown to select the region
regions = ["Africa", "Asia", "Europe", "North America", "Oceania", "South America"]
selected_region = st.selectbox("Choose your region:", regions)

# Explore button action
if st.button("Explore"):
    st.session_state.selected_region = selected_region
    if "selected_region" in st.session_state:
        selected_region = st.session_state.selected_region
        st.write(f"You have selected **{selected_region}**. Let's explore!")

        # Forest data plot
        region_forest_data = forestdf[forestdf['Region'] == selected_region]
        if region_forest_data.empty:
            st.write(f"No forest data available for {selected_region}. Please select a valid region.")
        else:
            years = ['1990', '2000', '2010', '2015', '2020']
            forest_area = region_forest_data[years].iloc[0].values  # Get values for forest area
            years_int = [int(year) for year in years]
           
            plt.figure(figsize=(10, 6))
            plt.plot(years_int, forest_area, marker='o', linestyle='-', color='green')
            plt.title(f"Forest Area in {selected_region} Over Time")
            plt.xlabel("Year")
            plt.ylabel("Forest Area (km²)")
            plt.xticks(years_int)
            plt.grid(True)
            st.pyplot(plt)

            if forest_area[-1] < forest_area[0]:
                st.write("This decline in forest area highlights the urgent need for conservation efforts.")

        # Mining data plot
        region_mining_data = miningdf[miningdf['Region'] == selected_region]
        if region_mining_data.empty:
            st.write(f"No mining data available for {selected_region}.")
        else:
            mining_years = [str(year) for year in range(1990, 2019)]
            mining_values = region_mining_data[mining_years].iloc[0].values.astype(float)
           
            mining_years_int = [int(year) for year in mining_years]
            z = np.polyfit(mining_years_int, mining_values, 1)
            p = np.poly1d(z)

            plt.figure(figsize=(10, 6))
            plt.plot(mining_years_int, mining_values, marker='o', linestyle='-', color='red', label="Mining Data")
            plt.plot(mining_years_int, p(mining_years_int), linestyle="--", color="blue", label="Best Fit Line")
            plt.title(f"Mining Activity in {selected_region} Over Time")
            plt.xlabel("Year")
            plt.ylabel("Mining Activity")
            plt.xticks(mining_years_int[::2], rotation=45)
            plt.grid(True)
            plt.legend()
            st.pyplot(plt)

            st.write("This shows the percentage of the region's GDP made up of mining.")

    # 30x30 Target section
    st.subheader("The 30x30 Target: Protecting Our Planet")
    st.write("Did you know about the 30x30 Target? It's a global goal to protect 30% of our planet's land and oceans by 2030.")
    st.write("However, as of 2018, only 14.5% of the world's land and oceans were protected.")

    # Find out the percentage of protected areas your country has
    st.write("Find out the percentage of protected areas your country has!")
    countryprotecteddf = pd.read_excel('Terrestrial_Marine protected areas.xlsx', sheet_name="Data")
    countryprotecteddf["Country and area"] = countryprotecteddf["Country and area"].str.strip()
    selected_country = st.selectbox("Select a Country", countryprotecteddf["Country and area"].unique())

    filtered_data = countryprotecteddf.loc[countryprotecteddf["Country and area"] == selected_country, "Terrestrial and marine protected areas "]

    if not filtered_data.empty:
        protected_area_value = filtered_data.values[0]
        st.write(f"**Terrestrial and Marine Protected Areas for {selected_country}:** {protected_area_value}")
    else:
        st.write(f"**No data available for {selected_country}.**")

# Actionable Tips section
if st.button("What Can I Do?"):
    st.session_state.page = "what_can_i_do"
    if "page" in st.session_state and st.session_state.page == "what_can_i_do":
        st.title("What Can I Do?")
        st.write("Explore how environmental factors affect biodiversity and take action!")

        # Display correlation heatmap
        newerdf = pd.read_csv('newer_datasetfinal.csv')
        st.subheader("Correlation Heatmap")
        st.write("See how different factors correlate with endangered species.")

        selected_cols = ['Mining', 'Forest', 'Marine protected areas', 'Terrestrial protected areas', '% change since 1990', 'Trigger Species']
        correlation_matrix = newerdf[selected_cols].corr()
        trigger_species_correlations = correlation_matrix[['Trigger Species']].transpose()

        trigger_species_correlations.rename(columns={'% change since 1990': 'CO2 Emissions'}, inplace=True)
       
        plt.figure(figsize=(10, 2))
        sns.heatmap(trigger_species_correlations, annot=True, cmap='coolwarm', fmt=".2f", cbar=False)
        plt.title('Correlation of Trigger Species with Other Variables')
        st.pyplot(plt)

        # Interactive Sliders for adjustments
        st.subheader("Interactive Sliders")
        st.write("Adjust environmental factors to see their estimated impact on endangered species.")
        co2_change = st.slider("CO₂ Change (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
        mining_change = st.slider("Mining Activity Change (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
        marine_change = st.slider("Marine Protected Areas (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
        forest_change = st.slider("Forest Areas (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)
        land_change = st.slider("Terrestrial Protected Areas (%)", min_value=-50.0, max_value=50.0, value=0.0, step=1.0)

        # Estimated impact on endangered species
        st.subheader("Estimated Impact on Endangered Species")
        st.write("Based on historical trends, here's the estimated impact of your changes:")

        mining_trend = np.polyfit(newerdf['Mining'], newerdf['Trigger Species'], 1)
        mining_impact = mining_trend[0] * mining_change
        co2_trend = np.polyfit(newerdf['% change since 1990'], newerdf['Trigger Species'], 1)
        co2_impact = co2_trend[0] * co2_change
        forest_trend = np.polyfit(newerdf['Forest'], newerdf['Trigger Species'], 1)
        forest_impact = forest_trend[0] * forest_change
        marine_trend = np.polyfit(newerdf['Marine protected areas'], newerdf["Trigger Species"], 1)
        marine_impact = marine_trend[0] * marine_change
        land_trend = np.polyfit(newerdf['Terrestrial protected areas'], newerdf["Trigger Species"], 1)
        land_impact = land_trend[0] * land_change

        total_impact = mining_impact + co2_impact + forest_impact + marine_impact + land_impact
        st.write(f"**Estimated change in endangered species:** {total_impact:.2f}")