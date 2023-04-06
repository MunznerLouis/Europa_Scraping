"""
Carbon Dashboard

This script is a dashboard that displays data on carbon sales and purchases. 
Users can filter the data by site using dropdown menus. 
The dashboard shows line charts for carbon sales and purchases, as well as a stacked area chart comparing sales and purchases for two sites.

The script requires the following packages:
    - numpy
    - pandas
    - plotly
    - dash
    - dash_core_components from dash
    - dash_html_components from dash

The data is loaded from a CSV file located at "data_transaction.csv".

The script defines the following functions:
    - generate_sales_line_chart(site): Generates a line chart showing the number of carbon units sold per month.
    - generate_purchases_line_chart(site): Generates a line chart showing the number of carbon units purchased per month.
    - generate_stack_area(site1, site2) : Generates a stacked area chart comparing the number of carbon units sold per month between two companies.

These functions generate the line charts and stacked area chart displayed on the dashboard.

The script defines the following variables:
    - transaction: pandas DataFrame containing transaction data
    - sales_subset: pandas DataFrame containing sales data grouped by account name and date
    - purchases_subset: pandas DataFrame containing purchases data grouped by account name and date
    - dropdown_options: a list of dictionaries containing options for a dropdown menu for site filtering of sales data
    - dropdown_options2: a list of dictionaries containing options for a dropdown menu for site filtering of purchases data
    - default_site: a string variable indicating the default value for the site filter
    - site_filter_sales: a dash_core_components Dropdown object for site filtering of sales data
    - site_filter_purchases: a dash_core_components Dropdown object for site filtering of purchases data
    - site_filter_stack: a dash_core_components Dropdown object for site filtering of stacked chart data
    - site_filter_stack2: a dash_core_components Dropdown object for site filtering of stacked chart data
    - default_site: A string representing the default site value for the site filter.

To run the code, just write in the command prompt :
    python time_series.py
"""


import numpy as np
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd


# Load data
transaction = pd.read_csv("data_transaction.csv")

# Create a new dataframe that groups the data by account name and date
sales_subset = (
    transaction.groupby(
        [
            "Transferring_Account_Holder",
            pd.to_datetime(transaction["Transaction_Date"]).dt.to_period("M"),
        ]
    )["Nb_of_Units"]
    .sum()
    .reset_index()
)
sales_subset["Transaction_Month"] = sales_subset["Transaction_Date"].dt.to_timestamp()

# Create a new dataframe that groups the data by account name and date for purchases
purchases_subset = (
    transaction.groupby(
        [
            "Acquiring_Account_Holder",
            pd.to_datetime(transaction["Transaction_Date"]).dt.to_period("M"),
        ]
    )["Nb_of_Units"]
    .sum()
    .reset_index()
)
purchases_subset["Transaction_Month"] = purchases_subset[
    "Transaction_Date"
].dt.to_timestamp()


transaction["Transaction_Month"] = pd.to_datetime(
    transaction["Transaction_Date"]
).dt.to_period("M")
transaction["Transaction_Month"] = transaction["Transaction_Month"].dt.to_timestamp()


# Create a list of all unique account names for the site filter
sites_transf = sales_subset["Transferring_Account_Holder"].unique().tolist()
sites_hold = purchases_subset["Acquiring_Account_Holder"].unique().tolist()

# Create a dictionary of dropdown options for the site filter
dropdown_options = []
for site in sites_transf:
    dropdown_options.append({"label": site, "value": site})

dropdown_options2 = []
for site in sites_hold:
    dropdown_options2.append({"label": site, "value": site})

# Add an "All sites" option to the site filter
dropdown_options.insert(0, {"label": "All sites", "value": "All sites"})
dropdown_options2.insert(0, {"label": "All sites", "value": "All sites"})

# Set the default value for the site filter
default_site = "All sites"

# Create a dropdown for site filtering
site_filter_sales = dcc.Dropdown(
    id="site-filter-sales",
    options=dropdown_options,
    value=default_site,
    clearable=False,
)


site_filter_purchases = dcc.Dropdown(
    id="site-filter-purchases",
    options=dropdown_options2,
    value=default_site,
    clearable=False,
)

site_filter_stack = dcc.Dropdown(
    id="site-filter-stack",
    options=dropdown_options,
    value=default_site,
    clearable=False,
)

site_filter_stack2 = dcc.Dropdown(
    id="site-filter-stack2",
    options=dropdown_options,
    value=default_site,
    clearable=False,
)

# Define a function to generate the line chart
def generate_sales_line_chart(site):
    """
    Generates a line chart showing the number of carbon units sold per month.

    Args:
        site (str): The name of the site to filter the data by. If 'All sites', all sites are included.

    Returns:
        fig (plotly.graph_objs.Figure): A line chart showing the number of carbon units sold per month, with an average
            line and annotations for the average value.
    """

    if site == "All sites":
        sales_agg = transaction.groupby(["Transaction_Month"], as_index=False)[
            "Nb_of_Units"
        ].sum()
        title_suffix = ""
    else:
        sales_agg = sales_subset[sales_subset["Transferring_Account_Holder"] == site]
        title_suffix = f": Ventes de carbone ({site})"

    average = sales_agg.loc[:, "Nb_of_Units"].mean()

    # Create the line chart with Plotly
    fig = px.line(
        sales_agg,
        x="Transaction_Month",
        y="Nb_of_Units",
        title=f"Toutes les ventes de carbone{title_suffix}",
        template="plotly",
    )
    fig.add_hline(
        y=average,
        line_dash="dot",
        line_color="orange",
        annotation_text=f"Average ({average:.2f})",
    )

    fig.update_xaxes(title_text="Month/Year")
    fig.update_yaxes(title_text="Number of Units")
    fig.update_traces(marker=dict(symbol="circle"))

    return fig


# Define a function to generate the purchases line chart
def generate_purchases_line_chart(site):
    """
        Generates a line chart showing the number of carbon units purchased per month.

    Args:
        site (str): The name of the site to filter the data by. If 'All sites', all sites are included.

    Returns:
        fig (plotly.graph_objs.Figure): A line chart showing the number of carbon units purchased per month, with an average
            line and annotations for the average value.
    """

    if site == "All sites":
        purchases_agg = transaction.groupby(["Transaction_Month"], as_index=False)[
            "Nb_of_Units"
        ].sum()
        title_suffix = ""
    else:
        purchases_agg = purchases_subset[
            purchases_subset["Acquiring_Account_Holder"] == site
        ]
        title_suffix = f": Achats de carbone ({site})"

    average = purchases_agg.loc[:, "Nb_of_Units"].mean()

    # Create the purchases line chart with Plotly
    fig = px.line(
        purchases_agg,
        x="Transaction_Month",
        y="Nb_of_Units",
        title=f"Tous les achats de carbone{title_suffix}",
        template="plotly",
    )
    fig.add_hline(
        y=average,
        line_dash="dot",
        line_color="orange",
        annotation_text=f"Average ({average:.2f})",
    )

    fig.update_xaxes(title_text="Month/Year")
    fig.update_yaxes(title_text="Number of Units")
    fig.update_traces(marker=dict(symbol="circle"))

    return fig


def generate_stack_area(site1, site2):
    """
        Generates a stacked area chart comparing the number of carbon units sold per month between two companies.

    Args:
        site1 (str): The name of the first company to filter the data by. If 'All sites', all sites are included.
        site2 (str): The name of the second company to filter the data by. If 'All sites', all sites are included.

    Returns:
        fig (plotly.graph_objs.Figure): A stacked area chart comparing the number of carbon units sold per month between
            two companies.
    """

    if site1 == "All sites":
        sales_agg1 = transaction.groupby(["Transaction_Month"], as_index=False)[
            "Nb_of_Units"
        ].sum()
        title_suffix = ""
    else:
        sales_agg1 = sales_subset[sales_subset["Transferring_Account_Holder"] == site1]
        title_suffix = f": Ventes de carbone ({site1})"

    if site2 == "All sites":
        sales_agg2 = transaction.groupby(["Transaction_Month"], as_index=False)[
            "Nb_of_Units"
        ].sum()
    else:
        sales_agg2 = sales_subset[sales_subset["Transferring_Account_Holder"] == site2]

    sales_agg1.rename(columns={"Nb_of_Units": site1}, inplace=True)
    sales_agg2.rename(columns={"Nb_of_Units": site2}, inplace=True)
    sales_agg1["Company"] = site1
    sales_agg2["Company"] = site2
    sales_agg = pd.concat([sales_agg1, sales_agg2])

    # Create the stacked area chart with Plotly
    fig = px.area(
        sales_agg,
        x="Transaction_Month",
        y=[site1, site2],
        title=f"Comparaison des ventes de carbone: {site1} vs {site2}",
        template="plotly",
        color="Company",
    )
    fig.update_xaxes(title_text="Month/Year")
    fig.update_yaxes(title_text="Number of Units")

    return fig


"""
Creates a Dash app that displays time series charts and a stacked area chart for carbon unit transactions.
The app layout includes filters for the transferring account holder and acquiring account holder, as well as
graph elements for a sales line chart, purchases line chart, and stack area chart.

Callbacks are defined for updating the sales line chart, purchases line chart, and stack area chart based on the
selected account holders.
"""

# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div(
    [
        html.H1("Transactions Time Series"),
        html.H4("Transferring Account Holder"),
        site_filter_sales,
        html.H4("Acquiring Account Holder"),
        site_filter_purchases,
        html.Div(
            [
                dcc.Graph(id="sales_line_chart"),
                dcc.Graph(id="purchases-line-chart"),
            ],
            style={"display": "flex", "flex-wrap": "wrap"},
        ),
        html.H1("Stack Area"),
        html.H4("Transferring Account Holder 1"),
        site_filter_stack,
        html.H4("Transferring Account Holder 2"),
        site_filter_stack2,
        html.Div(
            [
                dcc.Graph(id="stack-area"),
            ],
        ),
    ]
)

# Define the callback for the sales line chart
@app.callback(
    dash.dependencies.Output("sales_line_chart", "figure"),
    [dash.dependencies.Input("site-filter-sales", "value")],
)
def update_sales_line_chart(site):
    fig = generate_sales_line_chart(site)
    return fig


# Define the callback for the purchases line chart
@app.callback(
    dash.dependencies.Output("purchases-line-chart", "figure"),
    [dash.dependencies.Input("site-filter-purchases", "value")],
)
def update_purchases_line_chart(site):
    fig = generate_purchases_line_chart(site)
    return fig


@app.callback(
    dash.dependencies.Output("stack-area", "figure"),
    [
        dash.dependencies.Input("site-filter-stack", "value"),
        dash.dependencies.Input("site-filter-stack2", "value"),
    ],
)
def update_stack_area(site1, site2):
    fig = generate_stack_area(site1, site2)
    return fig


# Run the app
if __name__ == "__main__":
    # Start the app
    app.run_server(debug=True)
