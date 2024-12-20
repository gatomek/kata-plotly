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
    for row in root.iter('sst'):
        vls_file = row.get('vls').split(',')
        rows.append({
                "desc": row.get('desc'),
                "geo": row.get('geo'),
                "name": row.get('name'),
                "lat": row.get('lat'),
                "lon": row.get('lon'),
                "path": row.get('path'),
                "vl_750": True if ('750' in vls_file) else False,
                "vl_400": True if ('400' in vls_file) else False,
                "vl_220": True if ('220' in vls_file) else False,
                "vl_110": True if ('110' in vls_file) else False,
                "vl_20": True if ('20' in vls_file) else False,
                "vl_15": True if ('15' in vls_file) else False
            }
        )

    cols = ["desc", "geo", "name", "lat", "lon", "path", "vl_750", "vl_400", "vl_220", "vl_110", "vl_20", "vl_15"]
    return pd.DataFrame(rows, columns=cols)

def make_markers(ssts):
    markers = []
    for index, row in ssts.iterrows():
        markers.append(
            dict(name=row["name"], lat=row["lat"], lon=row["lon"], desc=row['desc'])
        )
    return markers

# Data processing ***

all_ssts = load_data('db/pse-geo-ssts.xml')
ssts = all_ssts[ all_ssts['vl_110'] == True]
markers = make_markers(ssts)
geojson = dlx.dicts_to_geojson(
    [{**c, **dict(tooltip="<b><h6>" + c['desc'] + "</h6></b><br/>LAT: " + c['lat'] + '<br/>LON: ' + c['lon'])}
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
