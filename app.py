import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import plotly.graph_objects as go
import bs4 as bs
import urllib.request
import datetime
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

'''
==================================================
READ DATA FROM GOVUK URL & POSTCODE FROM CSV FILES
==================================================
'''

# Crime data sourced from "https://data.police.uk/data/"

crime_files = glob.glob(os.path.join("*street*.csv"))
df = pd.concat((pd.read_csv(f, dtype="str") for f in crime_files), sort=True)

mapbox_access_token = "enter token here"

'''
======================
PARAMETERS & VARIABLES
======================
'''

d = df["Month"].max()
year, m = d.split("-")
month = calendar.month_abbr[int(m)]

datatable_rows = 10  # rows per page of datatable
fontsize = 15

textcol = "dimgrey"  # text colour
bgcol = "white"  # background colour of charts, table etc.
col_1 = "teal"
col_2 = "midnightblue"
col_3 = "mediumslateblue"
col_4 = "slateblue"
grid_col = "gainsboro"

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

                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="crime_type",
                                            options=[
                                                {"label": "Anti-social Behaviour", "value": "Anti-social behaviour"},
                                                {"label": "Bicycle Theft", "value": "Bicycle theft"},
                                                {"label": "Burglary", "value": "Burglary"},
                                                {"label": "Criminal Damage & Arson",
                                                 "value": "Criminal damage and arson"},
                                                {"label": "Drugs", "value": "Drugs"},
                                                {"label": "Other Crime", "value": "Other crime"},
                                                {"label": "Other Theft", "value": "Other theft"},
                                                {"label": "Possession of Weapons", "value": "Possession of weapons"},
                                                {"label": "Public Order", "value": "Public order"},
                                                {"label": "Robbery", "value": "Robbery"},
                                                {"label": "Shoplifting", "value": "Shoplifting"},
                                                {"label": "Theft from the Person", "value": "Theft from the person"},
                                                {"label": "Vehicle Crime", "value": "Vehicle crime"},
                                                {"label": "Violence & Sexual Offences",
                                                 "value": "Violence and sexual offences"},

                                            ],
                                            value=[],
                                            labelStyle={"display": "block"},
                                            inputStyle={"margin-right": "10px"}
                                        )
                                    ],
                                    className="col-9",
                                    style={"padding": "0px 30px 0px 30px"}
                                ),

                                dbc.Col(
                                    [
                                        html.H5(id="anti_social"),
                                        html.H5(id="bike_theft"),
                                        html.H5(id="burglary"),
                                        html.H5(id="damage_arson"),
                                        html.H5(id="drugs"),
                                        html.H5(id="other_crime"),
                                        html.H5(id="other_theft"),
                                        html.H5(id="possession_weapons"),
                                        html.H5(id="public_order"),
                                        html.H5(id="robbery"),
                                        html.H5(id="shoplifting"),
                                        html.H5(id="theft_person"),
                                        html.H5(id="vehicle_crime"),
                                        html.H5(id="violence_sexual")
                                    ],
                                    className="font-weight-bold text-right",
                                    style={"padding": "0px 30px 0px 30px"}
                                )
                            ]
                        )
                    ], style={"background": "ghostwhite", "border-style": "groove"}
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(),

        html.Div(
            dcc.Loading(
                dcc.Graph(
                    id="crime_map",
                    figure={},
                    config={"displayModeBar": False}
                )
            ), style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(),

        html.Div(
            [
                html.P("*Defaults to 'Bents Green & Millhouses' if local area is not selected")
            ], style={"font-style": "italic", "padding": "0px 20px 0px 20px"}
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
                    ], style={"background": "ghostwhite", "border-style": "groove", "padding": "0px 30px 0px 30px"}
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(),

        html.Div(
            [
                dcc.Loading(
                    dash_table.DataTable(
                        id="datatable",

                        columns=[
                            {
                                "id": "Row",
                                "name": "Row",
                                "type": "numeric"
                            },
                            {
                                "id": "MSOA",
                                "name": "Local Area",
                                "type": "text"
                            },
                            {
                                "id": "Falls within",
                                "name": "Local Constabulary",
                                "type": "text"
                            },
                            {
                                "id": "Crime type",
                                "name": "Crime Type",
                                "type": "text"
                            },
                            {
                                "id": "Location",
                                "name": "Location",
                                "type": "text"
                            },
                            {
                                "id": "Last outcome category",
                                "name": "Outcome",
                                "type": "text"
                            }
                        ],

                        sort_action="native",
                        sort_mode="single",
                        filter_action="none",
                        page_action="native",
                        page_current=0,
                        page_size=datatable_rows,
                        fixed_rows={"headers": True},
                        fixed_columns={"headers": True, "data": 2},

                        style_table={
                            "overflowX": "auto",
                            "overflowY": "auto",
                            "minWidth": "100%",
                            "height": "500px"
                        },

                        style_header={
                            "bold": True,
                            "color": "black",
                            "backgroundColor": "lightgrey",
                            "whiteSpace": "normal",
                            "height": "72px"
                        },

                        style_cell={
                            "color": textcol,
                            "backgroundColor": bgcol,
                            "font-family": "Verdana",
                            "font_size": fontsize,
                            "minWidth": 64,
                            "maxWidth": 160,
                            "padding": "0px 10px 0px 10px"
                        },

                        style_cell_conditional=[
                            {
                                "if": {
                                    "column_id": "Row"
                                },
                                "width": "5px"
                            },
                            {"if": {"column_id": "MSOA"}, "textAlign": "left"},
                            {"if": {"column_id": "Falls within"}, "textAlign": "left"},
                            {"if": {"column_id": "Crime type"}, "textAlign": "left"},
                            {"if": {"column_id": "Location"}, "textAlign": "left"},
                            {"if": {"column_id": "Last outcome category"}, "textAlign": "left"}
                        ],

                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto"
                        },

                        css=[
                            {
                                "selector": ".row",
                                "rule": "margin: 0; flex-wrap: nowrap"
                            }
                        ]
                    )
                )
            ], style={"padding": "0px 20px 0px 20px"}
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
======================
CALLBACK FOR DATATABLE
======================
'''


@app.callback(
    Output("datatable", "data"),
    [
        Input("msoa_drop", "value"),
        Input("crime_type", "value")
    ]
)
def return_datatable(selected_area, selected_crime_type):
    print(str(datetime.datetime.now()), "[1] start update_datatable...")

    df1 = df.copy()

    if selected_area is None or selected_area == []:
        df1 = df1[df1["MSOA"].isin(default_area)]
    else:
        df1 = df1[df1["MSOA"].isin(selected_area)]

    if selected_crime_type is None or selected_crime_type == []:
        pass
    else:
        df1 = df1[df1["Crime type"].isin(selected_crime_type)]

    df1["Row"] = df1.reset_index().index
    df1["Row"] += 1

    print(str(datetime.datetime.now()), "[1] finish update_datatable...")

    return df1.to_dict("records")


'''
========================
CALLBACK FOR SUMMARY BOX
========================
'''


@app.callback(
    [
        Output("anti_social", "children"),
        Output("bike_theft", "children"),
        Output("burglary", "children"),
        Output("damage_arson", "children"),
        Output("drugs", "children"),
        Output("other_crime", "children"),
        Output("other_theft", "children"),
        Output("possession_weapons", "children"),
        Output("public_order", "children"),
        Output("robbery", "children"),
        Output("shoplifting", "children"),
        Output("theft_person", "children"),
        Output("vehicle_crime", "children"),
        Output("violence_sexual", "children")
    ],
    [
        Input("msoa_drop", "value"),
        Input("crime_type", "value")
    ]
)
def return_summary(selected_area, selected_crime_type):
    df1 = df.copy()

    if selected_area is None or selected_area == []:
        df1 = df1[df1["MSOA"].isin(default_area)]
    else:
        df1 = df1[df1["MSOA"].isin(selected_area)]

    if selected_crime_type is None or selected_crime_type == []:
        pass
    else:
        df1 = df1[df1["Crime type"].isin(selected_crime_type)]

    anti_social = format(int(df1[df1["Crime type"] == "Anti-social behaviour"].shape[0]), ",d")
    bike_theft = format(int(df1[df1["Crime type"] == "Bicycle theft"].shape[0]), ",d")
    burglary = format(int(df1[df1["Crime type"] == "Burglary"].shape[0]), ",d")
    damage_arson = format(int(df1[df1["Crime type"] == "Criminal damage and arson"].shape[0]), ",d")
    drugs = format(int(df1[df1["Crime type"] == "Drugs"].shape[0]), ",d")
    other_crime = format(int(df1[df1["Crime type"] == "Other crime"].shape[0]), ",d")
    other_theft = format(int(df1[df1["Crime type"] == "Other theft"].shape[0]), ",d")
    possession_weapons = format(int(df1[df1["Crime type"] == "Possession of weapons"].shape[0]), ",d")
    public_order = format(int(df1[df1["Crime type"] == "Public order"].shape[0]), ",d")
    robbery = format(int(df1[df1["Crime type"] == "Robbery"].shape[0]), ",d")
    shoplifting = format(int(df1[df1["Crime type"] == "Shoplifting"].shape[0]), ",d")
    theft_person = format(int(df1[df1["Crime type"] == "Theft from the person"].shape[0]), ",d")
    vehicle_crime = format(int(df1[df1["Crime type"] == "Vehicle crime"].shape[0]), ",d")
    violence_sexual = format(int(df1[df1["Crime type"] == "Violence and sexual offences"].shape[0]), ",d")

    return anti_social, bike_theft, burglary, damage_arson, drugs, other_crime, other_theft, possession_weapons, \
           public_order, robbery, shoplifting, theft_person, vehicle_crime, violence_sexual


'''
================
CALLBACK FOR MAP
================
'''


@app.callback(
    Output("crime_map", "figure"),
    [
        Input("msoa_drop", "value"),
        Input("crime_type", "value")
    ]
)
def return_map(selected_area, selected_crime_type):
    df1 = df.copy()

    if selected_area is None or selected_area == []:
        df1 = df1[df1["MSOA"].isin(default_area)]
    else:
        df1 = df1[df1["MSOA"].isin(selected_area)]

    if selected_crime_type is None or selected_crime_type == []:
        pass
    else:
        df1 = df1[df1["Crime type"].isin(selected_crime_type)]

    lat_mean = pd.to_numeric(df1["Latitude"]).mean()
    lon_mean = pd.to_numeric(df1["Longitude"]).mean()

    fig = go.Figure(
        go.Scattermapbox(
            lat=df1["Latitude"],
            lon=df1["Longitude"],
            mode="markers",
            marker={"color": df1["COLOUR"], "size": 14},
            name="Crime Type",
            text=df1["Location"],
            customdata=df1["Crime type"],
            hovertemplate="%{text}<br>%{customdata}"
        )
    )

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat_mean,  # 53.3568326,
                lon=lon_mean  # -1.5198966
            ),
            pitch=0,
            zoom=12,
            style="streets"  # satellite, outdoors, light, dark
        ),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig


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
