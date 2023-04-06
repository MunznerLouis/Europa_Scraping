"""
This script generates visualizations for the 'data_holding_account.csv' file, which contains data on carbon emissions for various companies. 
The script uses the Pandas, Plotly, and Dash libraries.

Required Libraries:
- numpy (imported as np)
- dash
- plotly.express (imported as px)
- pandas (imported as pd)
- plotly.graph_objs (imported as go)

Functions:
- generate_bar_chart(year): Generates a bar chart of the top 10 most polluting sectors for a given year
- generate_ratio_chart(year): Generates a bar chart of the top 10 most polluting sectors for a given year, with an additional bar for the ratio of allocations/emissions compared to the previous year
- generate_comp_sector_chart(site): Generates a line chart of carbon emissions for a given company compared to the average emissions for that company's sector

Global Variables:
    - holding: Pandas DataFrame containing data from 'data_holding_account.csv'
    - holding_type: Pandas DataFrame containing aggregated data by Main_Activity_Type from 'holding'
    - holding_type_mean: Pandas DataFrame containing mean data by Main_Activity_Type from 'holding'
    - holding_sector: Pandas DataFrame containing aggregated data by Account_Holder_Name and Main_Activity_Type from 'holding'
    - holding_company: Pandas DataFrame containing aggregated data by Account_Holder_Name from 'holding'
    - col_indices: List of column indices for the columns in 'holding_type' corresponding to the years from 2005 to 2030
    - col_names: List of column names for the columns in 'holding_type' corresponding to the years from 2005 to 2030
    - col_indices2: List of column indices for the columns in 'holding_sector' corresponding to the years from 2005 to 2030
    - col_names2: List of column names for the columns in 'holding_sector' corresponding to the years from 2005 to 2030
    - col_indices_allowances: List of column indices for the columns in 'holding_sector' corresponding to the years from 2005 to 2030 (used in 'generate_ratio_chart')
    - col_names_allowances: List of column names for the columns in 'holding_sector' corresponding to the years from 2005 to 2030 (used in 'generate_ratio_chart')
    - list_year: List of integers representing the years from 2005 to 2030
    - sites: List of unique account names in 'holding_sector'
    - dropdown_options: List of dictionaries representing the options for the year dropdown menu in the Dash app
    - dropdown_options2: List of dictionaries representing the options for the site dropdown menu in the Dash app
    - year_filter: Dash dropdown component for selecting a year
    - site_filter: Dash dropdown component for selecting a site

To run the code, just write in the command prompt :
    python verified_emissions.py
"""

import numpy as np
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import plotly.graph_objs as go


# Load data
holding = pd.read_csv("data_holding_account.csv")


holding[holding.columns[29:]] = holding[holding.columns[29:]].replace(
    "[^0-9\.]+", "", regex=True
)

# Replace empty strings with NaN values
holding[holding.columns[29:]] = holding[holding.columns[29:]].replace("", np.nan)

# Convert columns to float
holding[holding.columns[29:]] = holding[holding.columns[29:]].astype(float)

holding_type = holding.groupby(["Main_Activity_Type"]).sum().reset_index()
holding_type_mean = holding.groupby(["Main_Activity_Type"]).mean().reset_index()

holding_sector = (
    holding.groupby(["Account_Holder_Name", "Main_Activity_Type"]).sum().reset_index()
)
holding_company = holding.groupby(["Account_Holder_Name"]).sum().reset_index()


# Create a list of column names with indices
col_indices = [(n * 6) + 5 for n in range(2031 - 2005)]
col_names = [holding_type.columns[i] for i in col_indices]

col_indices2 = [(n * 6) + 6 for n in range(2031 - 2005)]
col_names2 = [holding_sector.columns[i] for i in col_indices2]

col_indices_allowances = [(n * 6) + 4 for n in range(2031 - 2005)]
col_names_allowances = [holding_sector.columns[i] for i in col_indices2]

list_year = list(range(2005, 2031))

# Create a list of all unique account names for the site filter
sites = holding_sector["Account_Holder_Name"].unique().tolist()


# Create a dictionary of dropdown options for the filter
dropdown_options = []
for year in col_names:
    dropdown_options.append({"label": year, "value": year})

dropdown_options2 = []
for site in sites:
    dropdown_options2.append({"label": site, "value": site})


# Create a dropdown for site filtering
year_filter = dcc.Dropdown(
    id="year-filter",
    options=dropdown_options,
    value=str(col_names[0]),
    clearable=False,
)

site_filter = dcc.Dropdown(
    id="site-filter",
    options=dropdown_options2,
    value=str(sites[0]),
    clearable=False,
)


# Define a function to generate the bar chart
def generate_bar_chart(year):
    """
    Generate a Plotly bar chart showing the top 10 most polluting main activity types for a given year.

    Args:
        year (str): The year to filter the data by.

    Returns:
        A Plotly bar chart object showing the top 10 most polluting main activity types for the given year.
        The chart displays the number of carbon units per main activity type and is sorted in descending order.
    """

    holding_type_agg = holding_type.sort_values(year, ascending=False)
    holding_type_agg = holding_type_agg[:10]

    # Create the barplot chart with Plotly
    fig = px.bar(
        holding_type_agg,
        x="Main_Activity_Type",
        y=year,
        title=f"Top 10 des secteurs les plus polluants : {year}",
        template="plotly",
    )
    fig.update_xaxes(title_text="Main Activity Type")
    fig.update_yaxes(title_text="Number of Units")

    return fig


def generate_ratio_chart(year):
    """
    Generates a Plotly bar chart object showing the allocation/emission ratio for the top 10 most polluting sectors
    in a given year, compared to the previous year.

    Parameters:
        year (str): The year for which to generate the chart, in the format "YYYY". It should be a valid column name
                in the DataFrame used by the function.

    Returns:
    fig (plotly.graph_objs._figure.Figure): A Plotly bar chart object showing the allocation/emission ratio
                                             for the top 10 most polluting sectors in the given year.
    """

    year_index = holding_type.columns.get_loc(year)
    previous_column = holding_type.columns[year_index - 1]
    holding_type[previous_column] = holding_type[previous_column].astype(float)
    holding_type_agg = holding_type.sort_values(year, ascending=False)

    holding_type_agg["ratio"] = (
        holding_type_agg[previous_column] / holding_type_agg[year]
    )

    holding_type_agg = holding_type_agg[:10]

    # Create the barplot chart with Plotly
    fig = px.bar(
        holding_type_agg,
        x="Main_Activity_Type",
        y="ratio",
        title=f"Top 10 des secteurs les plus polluants : {year}",
        template="plotly",
    )
    fig.update_xaxes(title_text="Main Activity Type")
    fig.update_yaxes(title_text="Allocations/emissions")
    fig.update_layout(yaxis=dict(tickformat=".2%"))

    return fig


def generate_comp_sector_chart(site):
    """
    Generates a Plotly line chart comparing the emissions of a company to the average emissions
    of its sector over the years.

    Parameters:
        site (str): The name of the company to compare with its sector.

    Returns:
        fig : plotly.graph_objs._figure.Figure
            A Plotly line chart object showing the emissions of the company and the average emissions
            of its sector over the years.
    """

    holding_sector_agg = holding_sector[holding_sector["Account_Holder_Name"] == site]
    holding_sector_agg = holding_sector_agg.transpose().reset_index()

    values = holding_sector_agg.iloc[col_indices2, 1].values

    activity = holding_sector_agg.iloc[1, 1]

    holding_type_agg2 = (
        holding_type_mean[holding_type_mean["Main_Activity_Type"] == activity]
        .transpose()
        .reset_index()
    )
    values2 = holding_type_agg2.iloc[col_indices, 1].values

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list_year,
            y=values,
            mode="lines",
            line=dict(color="blue", width=2),
            name="Company Emissions",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=list_year,
            y=values2,
            mode="lines",
            line=dict(color="red", width=2),
            name="Sector Average Emissions",
        )
    )

    fig.update_layout(
        title=f"Emissions Vérifiées : {site} comparé au secteur : {activity}"
    )

    fig.update_xaxes(title_text="Année")
    fig.update_yaxes(title_text="Emissions Vérifiées")

    return fig


def generate_comp_chart(site):
    """
    Generates a Plotly line chart object showing the verified emissions and allowances in allocation for a given company.

    Args:
    - site (str): The name of the company to display the chart for.

    Returns:
    - fig (plotly.graph_objs._figure.Figure):
        A Plotly line chart object showing the verified emissions and allowances in allocation for the given company.
    """

    holding_company_agg = holding_company[
        holding_company["Account_Holder_Name"] == site
    ]
    holding_company_agg = holding_company_agg.transpose().reset_index()

    values = holding_company_agg.iloc[col_indices, 1].values

    values3 = holding_company_agg.iloc[col_indices_allowances, 1].values

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list_year,
            y=values,
            mode="lines",
            line=dict(color="blue", width=2),
            name="Verified Emissions",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=list_year,
            y=values3,
            mode="lines",
            line=dict(color="green", width=2),
            name="Allowances in Allocation",
        )
    )

    fig.update_layout(
        title=f"Emissions Vérifiées : {site} par rapport aux quotas accordés"
    )

    fig.update_xaxes(title_text="Année")
    fig.update_yaxes(title_text="Emissions Vérifiées")

    return fig


"""
Creates a Dash app that displays various time series charts and comparisons for carbon emissions data. 
The app layout includes filters for selecting the year and company to display, as well as 
    graph elements for a verified emissions line chart, an allocation-to-emission ratio chart, 
    and two comparison charts between a company's emissions and sector averages, and a company's emissions and allowances.

Callbacks are defined for updating each chart based on the selected year or company.
"""

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        html.H2("Year"),
        year_filter,
        html.H1("Verified Emissions by Sector by Year"),
        html.Div(
            [dcc.Graph(id="bar-chart")],
        ),
        html.H1("Allocation to Emission Ratio in Top Polluting Sectors"),
        html.Div(
            [dcc.Graph(id="ratio-chart")],
        ),
        html.H2("Company"),
        site_filter,
        html.H1(
            "Comparison between company's emissions and the sector's average emissions"
        ),
        html.Div(
            [dcc.Graph(id="sector-comp-chart")],
        ),
        html.H1("Comparison between company's emissions and his allowances"),
        html.Div(
            [dcc.Graph(id="comp-chart")],
        ),
    ]
)


# Define the callback for the barplot chart
@app.callback(
    dash.dependencies.Output("bar-chart", "figure"),
    [dash.dependencies.Input("year-filter", "value")],
)
def update_bar_chart(year):
    fig = generate_bar_chart(year)
    return fig


# Define the callback for the ratio chart
@app.callback(
    dash.dependencies.Output("ratio-chart", "figure"),
    [dash.dependencies.Input("year-filter", "value")],
)
def update_ratio_chart(year):
    fig = generate_ratio_chart(year)
    return fig


# Define the callback for the comp chart
@app.callback(
    dash.dependencies.Output("sector-comp-chart", "figure"),
    [dash.dependencies.Input("site-filter", "value")],
)
def update_comp_sector_chart(site):
    fig = generate_comp_sector_chart(site)
    return fig


# Define the callback for the comp chart
@app.callback(
    dash.dependencies.Output("comp-chart", "figure"),
    [dash.dependencies.Input("site-filter", "value")],
)
def update_comp_chart(site):
    fig = generate_comp_chart(site)
    return fig


# Run the app
if __name__ == "__main__":
    # Start the app
    app.run_server(debug=True)
