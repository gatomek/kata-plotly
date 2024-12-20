import pandas as pd
import dash_leaflet as dl
import dash_leaflet.express as dlx
import xml.etree.ElementTree as Xet

from dash import Dash, html

# lib ***

def get_param(txt):
    p = txt.split(":")
    return p[1]

def load_data(filePath):
    rows = []
    xmlparse = Xet.parse(filePath)
    root = xmlparse.getroot()
    for row in root.iter('row'):
        target = None
        for cell in row.iter('cell'):
            target = cell
        text = target.get('text')
        parts = text.split()

        name = get_param(parts[0])
        lat = get_param(parts[2])
        lon = get_param(parts[1])
        vl_750 = get_param(parts[3])
        vl_400 = get_param(parts[4])
        vl_220 = get_param(parts[5])
        vl_110 = get_param(parts[6])
        vl_20 = get_param(parts[7])
        vl_15 = get_param(parts[8])

        rows.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "vl_750": vl_750,
            "vl_400": vl_400,
            "vl_220": vl_220,
            "vl_110": vl_110,
            "vl_20": vl_20,
            "vl_15": vl_15}
        )

    cols = ["name", "lat", "lon", "vl_750", "vl_400", "vl_220", "vl_110", "vl_20", "vl_15"]
    return pd.DataFrame(rows, columns=cols)

def make_markers(ssts):
    markers = []
    for index, row in ssts.iterrows():
        markers.append(
            dict(name=row["name"], lat=row["lat"], lon=row["lon"])
        )
    return markers

# Data processing ***

all_ssts = load_data('db/sst-report.xml')
ssts = all_ssts[all_ssts['vl_110'] == '1']
markers = make_markers(ssts)

geojson = dlx.dicts_to_geojson(
    [{**c, **dict(tooltip="<b><h6>" + c['name'] + "</h6></b><br/>LAT: " + c['lat'] + '<br/>LON: ' + c['lon'])}
     for c in markers])

# App Layout ***

stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, external_stylesheets=stylesheets)

app.layout = html.Div(
    [
        html.Div(
            dl.MapContainer([
                dl.TileLayer(),
                dl.GeoJSON(data=geojson, cluster=True),
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
                style={'height': '100vh'}
            ),
            className="row "
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
