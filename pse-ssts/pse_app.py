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
        vls = row.get('vls')
        vl_splits = vls.split(',')
        vl_array = []
        for vl in vl_splits:
            if (vl != ''):
                vl_array.append(float(vl))
        vl_array.sort(reverse=True)
        vl_str = []
        for vl in vl_array:
            vlf = float(vl)
            vli = int(vl)
            svl = str(vli) if vlf == vli else str(vlf)
            vl_str.append(svl)
        rows.append({
            "desc": row.get('desc'),
            "geo": row.get('geo'),
            "name": row.get('name'),
            "lat": row.get('lat'),
            "lon": row.get('lon'),
            "path": row.get('path'),
            "vls": ', '.join(vl_str),
            "vl_750": True if (750 in vl_array) else False,
            "vl_400": True if (400 in vl_array) else False,
            "vl_220": True if (220 in vl_array) else False,
            "vl_110": True if (110 in vl_array) else False,
            "vl_20": True if (20 in vl_array) else False,
            "vl_15": True if (15 in vl_array) else False,
            "vl_10": True if (10 in vl_array) else False
        }
        )

    cols = ["desc", "geo", "name", "lat", "lon", "path", "vls", "vl_750", "vl_400", "vl_220", "vl_110", "vl_20",
            "vl_15", "vl_10"]
    return pd.DataFrame(rows, columns=cols)


def make_markers(ssts):
    markers = []
    for index, row in ssts.iterrows():
        markers.append(
            dict(name=row["name"], lat=row["lat"], lon=row["lon"], desc=row['desc'], vls=row['vls'])
        )
    return markers


# Data processing ***

all_ssts = load_data('db/pse-geo-ssts.xml')
ssts = all_ssts[all_ssts['vl_220'] == True]
markers = make_markers(ssts)
geojson = dlx.dicts_to_geojson(
    [{**c, **dict(tooltip="<h6><b>" + c['desc'] + "</b><br/>" + c['vls'] + "</h6>")}
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
                style={'height': '98vh'}
            ),
            className="row "
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
