"""
Creates a map of holding account locations using folium library and MarkerCluster plugin.

The function loads the holding account data from a CSV file that contains the Latitude and Longitude coordinates for each location. 
It then creates an interactive map centered on the mean Latitude and Longitude of the holding accounts. 
The function adds markers to the map using the MarkerCluster plugin, which groups markers together for better visualization. 
Each marker shows information about the holding account, including the 
    National Administrator, Account Holder Name, Installation Name/Aircraft Operator Code, Main Activity Type, and City.
Finally, the function saves the map to an HTML file and returns the folium map object.

Returns:
    ma_carte: a folium map object representing the holding accounts map
"""


import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Load data
holding_coor = pd.read_csv("holding_with_coordinates.csv")
holding_coor = holding_coor.dropna(subset=["Latitude", "Longitude"])

# Define function to create map
def create_map():
    # Create empty map
    ma_carte = folium.Map(
        location=[holding_coor["Latitude"].mean(), holding_coor["Longitude"].mean()],
        zoom_start=3,
    )

    # Create marker cluster layer
    marker_cluster = MarkerCluster().add_to(ma_carte)

    # Add markers to marker cluster layer
    for index, row in holding_coor.iterrows():
        popup_text = "<b>National_Administrator:</b> {}<br><b>Account Holder Name:</b> {}<br><b>Installation Name/Aircraft Operator Code:</b> {}<br><b>Main Activity Type:</b> {}<br><b>City:</b> {}".format(
            row["National_Administrator"],
            row["Account_Holder_Name"],
            row["Installation_Name/Aircraft_Operator_Code"],
            row["Main_Activity_Type"],
            row["City"],
        )
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_text, max_width=300),
        ).add_to(marker_cluster)

    # Save map to HTML file
    ma_carte.save("holding_map.html")

    # Display map
    return ma_carte


# Call function to create map
create_map()
