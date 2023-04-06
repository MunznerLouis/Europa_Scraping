"""
This script uses the Geopy library to get latitude and longitude coordinates for addresses in a CSV file. It reads a CSV file "data_holding_account.csv" using pandas, initializes a geocoder using the Nominatim service, and defines a function to get latitude and longitude for each row in the dataframe. It then applies the function to each row using pandas apply function, and adds the resulting latitude and longitude values to the dataframe. Finally, it exports the dataframe to a new CSV file "holding_with_coordinates.csv".

Requirements:
- pandas
- geopy

Usage:
- Update the CSV file path in the script to match the location of your input file.
- Run the script in a Python environment.

Output:
- A new CSV file "holding_with_coordinates.csv" containing the original data with latitude and longitude columns added.

""" 

import pandas as pd
from geopy.geocoders import Nominatim

# Load data
holding = pd.read_csv("data_holding_account.csv")
num_rows = len(holding)

holding["Main_Adress_Line"] = holding["Main_Adress_Line"].astype(str)
holding["City"] = holding["City"].astype(str)
holding["Country"] = holding["Country"].astype(str)

# Initialize geocoder
geolocator = Nominatim(user_agent="my_application")

# Define function to get latitude and longitude
def get_lat_long(index, row):
    print(str(index + 1) + "/" + str(num_rows))
    location = geolocator.geocode(
        row["Main_Adress_Line"] + ", " + row["City"] + ", " + row["Country"],
        timeout=10,
    )

    if location:
        return pd.Series(
            {"Latitude": location.latitude, "Longitude": location.longitude}
        )
    else:
        location = geolocator.geocode(row["City"] + ", " + row["Country"], timeout=10)

        if location:
            return pd.Series(
                {"Latitude": location.latitude, "Longitude": location.longitude}
            )
        else:
            return pd.Series({"Latitude": "", "Longitude": ""})


# Get latitude and longitude for each row in the dataframe
holding[["Latitude", "Longitude"]] = holding.apply(
    lambda row: get_lat_long(row.name, row), axis=1
)


holding.to_csv("holding_with_coordinates.csv", index=False)
