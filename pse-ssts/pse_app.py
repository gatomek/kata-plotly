import pandas as pd
import dash_leaflet as dl
import xml.etree.ElementTree as Xet

from dash import Dash, html


def get_param(str):
    p = str.split(":")
    return p[1]


# Preparing your data for usage *******************************************

rows = []
xmlparse = Xet.parse('db/sst-report.xml')
root = xmlparse.getroot()
for row in root.iter('row'):
    target = None
    for cell in row.iter('cell'):
        target = cell
    text = target.get('text')
    parts = text.split()

    name = get_param(parts[0])
    lat = get_param(parts[2])
    long = get_param(parts[1])
    vl_750 = get_param(parts[3])
    vl_400 = get_param(parts[4])
    vl_220 = get_param(parts[5])
    vl_110 = get_param(parts[6])
    vl_20 = get_param(parts[7])
    vl_15 = get_param(parts[8])

    rows.append({
        "name": name,
        "lat": lat,
        "long": long,
        "vl_750": vl_750,
        "vl_400": vl_400,
        "vl_220": vl_220,
        "vl_110": vl_110,
        "vl_20": vl_20,
        "vl_15": vl_15}
    )

cols = ["name", "lat", "long", "vl_750", "vl_400", "vl_220", "vl_110", "vl_20", "vl_15"]
all_ssts = pd.DataFrame(rows, columns=cols)
ssts = all_ssts[all_ssts['vl_400'] == '1']

def get_data():
    markers = []
    for index, row in ssts.iterrows():
        markers.append(
            dl.Marker(
                title=row['name'],
                position=(row['lat'], row['long']),
                children=[
                    dl.Tooltip( content="<b><h6>" + row['name'] + "</h6></b><br/>LAT: " + row['lat'] + '<br/>LONG: ' + row['long'])
                    #dl.Popup(row['name']),
                ],
            )
        )
    group = dl.LayerGroup(markers, id="layer_group")
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
            dl.MapContainer([
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
                center=[52, 19],
                zoom=6,
                style={'height': '90vh'}
            ),
            className="row "
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
