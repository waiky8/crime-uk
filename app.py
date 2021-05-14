import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import bs4 as bs
import urllib.request
from configparser import ConfigParser
import base64
import calendar
import glob
import os

'''
===========
SET-UP DASH
===========
'''

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[
                    {"name": "viewport",
                     "content": "width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,"
                     }
                ]
                )
server = app.server
app.title = "Crime UK"

config = ConfigParser()
config.read("config.ini")
mapbox_access_token = config["mapbox"]["secret_token"]

'''
==================================================
READ DATA FROM GOVUK URL & POSTCODE FROM CSV FILES
==================================================
'''

# Crime data sourced from "https://data.police.uk/data/"

crime_files = glob.glob(os.path.join("*street*.csv"))
df = pd.concat((pd.read_csv(f, dtype="str") for f in crime_files), sort=True)

'''
=================================
READ IMAGE FILES FOR BUTTON ICONS
=================================
'''

image_house = base64.b64encode(open("house.png", "rb").read())
image_car = base64.b64encode(open("car.png", "rb").read())
image_robbery = base64.b64encode(open("robbery.png", "rb").read())
image_violence = base64.b64encode(open("violence.png", "rb").read())
image_theft = base64.b64encode(open("theft.png", "rb").read())
image_others = base64.b64encode(open("others.png", "rb").read())

'''
======================
PARAMETERS & VARIABLES
======================
'''

d = df["Month"].max()
year, m = d.split("-")
month = calendar.month_abbr[int(m)]

fontsize = 15

default_area = ["Bents Green & Millhouses"]

'''
===================
DASH LAYOUT SECTION
===================
'''

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("Local Crime UK"),
                html.H3(str("(" + month + ", " + year + ")"))
            ],
            style={"text-align": "center", "font-weight": "bold"}
        ),

        html.Br(), html.Br(),

        html.Div(
            [
                html.Div(
                    [
                        html.Br(),

                        dcc.Dropdown(
                            id="msoa_drop",
                            options=[{"label": i, "value": i} for i in
                                     sorted(df["MSOA"].fillna("No Location").unique())],
                            value=default_area,
                            multi=True,
                            placeholder="Local Area (Mutli-Select)",
                            style={"font-size": fontsize, "color": "black", "background-color": "white"}
                        ),

                        html.Br(),

                        html.P("Postcode/Local Area Lookup:"),

                        dbc.Row(
                            [
                                dcc.Input(
                                    id="postcode_inp",
                                    className="col-4",
                                    placeholder="Post Code",
                                    style={"font-size": fontsize, "color": "black", "background-color": "white"}
                                ),

                                html.P(id="message", className="col-8"),
                            ]
                        ),

                        html.Br()
                    ], style={"background": "whitesmoke", "padding": "0px 30px 0px 30px"}
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(),

        html.Div(
            [
                html.P("*Defaults to 'Bents Green & Millhouses' if local area is not selected")
            ], style={"font-style": "italic", "padding": "0px 20px 0px 20px"}
        ),

        html.Br(),

html.Div(
            [
                html.Div(
                    [
                        html.Br(),

                        dbc.Row(
                            [
                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_house.decode())),
                                    id="burglary_butt", n_clicks=0, className="btn col-4",
                                ),

                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_car.decode())),
                                    id="car_butt", n_clicks=0, className="btn col-4",
                                ),

                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_robbery.decode())),
                                    id="robbery_butt", n_clicks=0, className="btn col-4",
                                )
                            ], style={"padding": "0px 30px 0px 30px"}
                        ),

                        dbc.Row(
                            [
                                html.Div(
                                    html.P("BURGLARY"),
                                    id="burglary_text",
                                    className="col-4"
                                ),

                                html.Div(
                                    html.P("VEHICLE CRIME"),
                                    id="car_text",
                                    className="col-4"
                                ),

                                html.Div(
                                    html.P("ROBBERY"),
                                    id="robbery_text",
                                    className="col-4"
                                ),
                            ], style={"padding": "0px 30px 0px 30px", "textAlign": "center"}
                        ),

                        html.Br(),

                        dbc.Row(
                            [
                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_violence.decode())),
                                    id="violent_butt", n_clicks=0, className="btn col-4",
                                ),

                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_theft.decode())),
                                    id="theft_butt", n_clicks=0, className="btn col-4",
                                ),

                                html.Button(
                                    html.Img(src="data:image/png;base64,{}".format(image_others.decode())),
                                    id="others_butt", n_clicks=0, className="btn col-4",
                                ),
                            ], style={"padding": "0px 30px 0px 30px"}
                        ),

                        dbc.Row(
                            [
                                html.Div(
                                    html.P("VIOLENT CRIME"),
                                    id="violent_text",
                                    className="col-4"
                                ),

                                html.Div(
                                    html.P("THEFT"),
                                    id="theft_text",
                                    className="col-4"
                                ),

                                html.Div(
                                    html.P("OTHER CRIME"),
                                    id="others_text",
                                    className="col-4"
                                )
                            ], style={"padding": "0px 30px 0px 30px", "textAlign": "center"}
                        ),
                    ]
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(),

        html.Div(
            dcc.Loading(
                dcc.Graph(
                    id="crime_map",
                    figure={},
                    config={"displayModeBar": False}
                )
            ), style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(), html.Br(),

        html.Div(
            html.P(
                ["Data Source: ",
                 html.A("PoliceUK", href="https://data.police.uk/data/", target="_blank")
                 ]
            ),
            style={"padding": "0px 0px 0px 50px"}
        ),

        html.Div(
            html.P(
                ["Code: ",
                 html.A("Github", href="https://github.com/waiky8/crime-uk", target="_blank")
                 ]
            ),
            style={"padding": "0px 0px 0px 50px"}
        )
    ]
)

'''
==============================
CALLBACK FOR SUMMARY BOX & MAP
==============================
'''


@app.callback(
    [
        Output("crime_map", "figure"),
        Output("burglary_text", "className"),
        Output("car_text", "className"),
        Output("robbery_text", "className"),
        Output("violent_text", "className"),
        Output("theft_text", "className"),
        Output("others_text", "className"),
    ],

    [
        Input("msoa_drop", "value"),
        Input("burglary_butt", "n_clicks"),
        Input("car_butt", "n_clicks"),
        Input("robbery_butt", "n_clicks"),
        Input("violent_butt", "n_clicks"),
        Input("theft_butt", "n_clicks"),
        Input("others_butt", "n_clicks"),
    ]
)
def return_summary(selected_area, selected_burglary, selected_car_crime, selected_robbery, selected_violent_crime,
                   selected_theft, selected_other_crime):
    df1 = df.copy()

    '''
    -----------
    SUMMARY BOX
    -----------
    '''
    if selected_area is None or selected_area == []:
        df1 = df1[df1["MSOA"].isin(default_area)]
    else:
        df1 = df1[df1["MSOA"].isin(selected_area)]

    lat_mean_saved = pd.to_numeric(df1["Latitude"]).mean()
    lon_mean_saved = pd.to_numeric(df1["Longitude"]).mean()

    crime_type = []
    burglary_class = car_class = robbery_class = violent_class = theft_class = others_class = "col-4"

    if (selected_burglary % 2) == 1:
        crime_type.append("Burglary")
        burglary_class = "col-4 font-weight-bold text-danger"

    if (selected_car_crime % 2) == 1:
        crime_type.append("Vehicle crime")
        car_class = "col-4 font-weight-bold text-danger"

    if (selected_robbery % 2) == 1:
        crime_type.append("Robbery")
        robbery_class = "col-4 font-weight-bold text-danger"

    if (selected_violent_crime % 2) == 1:
        crime_type.append("Violence and sexual offences")
        violent_class = "col-4 font-weight-bold text-danger"

    if (selected_theft % 2) == 1:
        crime_type.append("Bicycle theft")
        crime_type.append("Other theft")
        crime_type.append("Shoplifting")
        crime_type.append("Theft from the person")
        theft_class = "col-4 font-weight-bold text-primary"

    if (selected_other_crime % 2) == 1:
        crime_type.append("Anti-social behaviour")
        crime_type.append("Criminal damage and arson")
        crime_type.append("Drugs")
        crime_type.append("Possession of weapons")
        others_class = "col-4 font-weight-bold text-primary"

    if crime_type:
        df1 = df1[df1["Crime type"].isin(crime_type)]

    '''
    ----------------
    MAP WITH MARKERS
    ----------------
    '''

    if df1.empty:
        lat_mean = lat_mean_saved
        lon_mean = lon_mean_saved
    else:
        lat_mean = pd.to_numeric(df1["Latitude"]).mean()
        lon_mean = pd.to_numeric(df1["Longitude"]).mean()

    df1.loc[(pd.isna(df1["Last outcome category"])), "Last outcome category"] = ""

    fig = go.Figure(
        go.Scattermapbox(
            lat=df1["Latitude"],
            lon=df1["Longitude"],
            mode="text+markers",
            marker={"color": df1["COLOUR"], "size": 14},
            name="",
            text="",
            textposition='top center',
            customdata=np.stack(
                (
                    df1["Falls within"],
                    df1["MSOA"],
                    df1["Location"],
                    df1["Crime type"],
                    df1["Last outcome category"]
                ),
                axis=-1
            ),
            hovertemplate="<br><b>Police Force</b>: %{customdata[0]}" + \
                          "<br><b>Local Area</b>: %{customdata[1]}" + \
                          "<br><b>Location</b>: %{customdata[2]}" + \
                          "<br><b>Crime type</b>: %{customdata[3]}" + \
                          "<br><b>Outcome</b>: %{customdata[4]}"
        )
    )

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat_mean,
                lon=lon_mean
            ),
            pitch=0,
            zoom=12,
            style="streets"  # satellite, outdoors, light, dark
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        ),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig, burglary_class, car_class, robbery_class, violent_class, theft_class, others_class,


'''
=================================
CALLBACK FOR POSTCODE/MSOA LOOKUP
=================================
'''


@app.callback(
    Output("message", "children"),
    [
        Input("postcode_inp", "n_submit"),
        Input("postcode_inp", "n_blur")
    ],
    State("postcode_inp", "value")
)
def return_datatable(ns, nb, selected_postcode):
    message = ""

    if selected_postcode is None or selected_postcode == "":
        pass
    else:
        neighbourhood = get_data(selected_postcode.upper())
        if neighbourhood == "":
            message = "Please enter valid full postcode"
        else:
            message = neighbourhood

    return message


'''
=================================
MAP POSTCODE TO LOCAL AREA (MSOA)
=================================
'''


def get_data(pcode):
    area = ""

    url = ("https://www.doogal.co.uk/ShowMap.php?postcode=" + pcode).replace(" ", "%20")

    try:
        source = urllib.request.urlopen(url)
        soup = bs.BeautifulSoup(source, 'lxml')
        tables = soup.find_all("table")

        for tb in tables:
            table_rows = tb.find_all("tr")

            for tr in table_rows:
                thd = tr.find_all(["th", "td"])
                row = [i.text for i in thd]
                if row[0] == "Middle layer super output area":
                    area = row[1]
                    break

    except urllib.request.HTTPError as err:
        print("HTTP Error: (postcode ", pcode, ")", err.code)

    return area


if __name__ == "__main__":
    app.run_server(debug=True)
