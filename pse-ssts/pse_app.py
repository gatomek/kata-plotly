import pandas as pd
import dash_leaflet as dl

from dash import Dash, html

# Preparing your data for usage *******************************************

ssts = pd.read_csv("ssts.csv")

icon = {
    "iconUrl": "https://leafletjs.com/examples/custom-icons/leaf-green.png",
    "shadowUrl": "https://leafletjs.com/examples/custom-icons/leaf-shadow.png",
    "iconSize": [38, 95],  # size of the icon
    "shadowSize": [50, 64],  # size of the shadow
    "iconAnchor": [
        22,
        94,
    ],  # point of the icon which will correspond to marker's location
    "shadowAnchor": [4, 62],  # the same for the shadow
    "popupAnchor": [
        -3,
        -76,
    ],  # point from which the popup should open relative to the iconAnchor
}

def get_data():
    markers = []
    for index, row in ssts.iterrows():
        markers.append(
            dl.Marker(
                title=row['name'],
                position=(row['lat'], row['lng']),
                children=[
                    dl.Tooltip(row['name']),
                    dl.Popup(row['name']),
                ],
            )
        )
    group = dl.LayerGroup( markers, id="layer_group")
    return group

# App Layout **************************************************************

stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=stylesheets)

app.layout = html.Div(
    [
        html.Div(
            html.H1(
                "PSE Stacje", style={"textAlign": "center"}
            ),
            className="row",
        ),
        html.Div(
            dl.Map( [
                    dl.TileLayer(),
                    get_data(),
                    dl.LayersControl(
                    [
                        dl.BaseLayer(
                            dl.TileLayer(),
                            name="OpenStreetMaps",
                            checked=True,
                        ),
                        dl.BaseLayer(
                            dl.TileLayer(
                                url="https://www.ign.es/wmts/mapa-raster?request=getTile&layer=MTN&TileMatrixSet=GoogleMapsCompatible&TileMatrix={z}&TileCol={x}&TileRow={y}&format=image/jpeg",
                                attribution="IGN",
                            ),
                            name="IGN",
                            checked=False,
                        ),
                    ])
                ],
                id="pse-map",
                center=[52,19],
                zoom=6,
                style={'height': '90vh'}
            ),
            className="row "
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
