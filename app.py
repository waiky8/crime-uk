import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from configparser import ConfigParser
from datetime import datetime

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
app.title = "ENG Schools"

config = ConfigParser()
config.read("config.ini")
mapbox_access_token = config["mapbox"]["secret_token"]

'''
==============
READ CSV FILES
==============
'''

# df_pri = pd.read_csv("england_ks2final.csv")
# df_sec = pd.read_csv("england_ks4final.csv")
# df_p16 = pd.read_csv("england_ks5final.csv")

# df_eng_avg = pd.read_csv("england_gcse_alevel_averages.csv")

df_pri = pd.read_csv("https://github.com/waiky8/eng-schools/blob/main/england_ks2final.csv?raw=true")
df_sec = pd.read_csv("https://github.com/waiky8/eng-schools/blob/main/england_ks4final.csv?raw=true")
df_p16 = pd.read_csv("https://github.com/waiky8/eng-schools/blob/main/england_ks5final.csv?raw=true")

df_eng_avg = pd.read_csv("https://github.com/waiky8/eng-schools/blob/main/england_gcse_alevel_averages.csv?raw=true")

'''
======================
PARAMETERS & VARIABLES
======================
'''

# New rows used to display blank row in datatable if no rows meet selected criteria - otherwise header is malformed
new_row_pri = {"RECTYPE": "", "URN": "", "SCHNAME": "", "PCODE": "", "PCODE2": "", "TOWN": "", "READPROG": "",
               "READPROG_DESCR": "", "WRITPROG": "", "WRITPROG_DESCR": "", "MATPROG": "", "MATPROG_DESCR": "",
               "OFSTEDRATING": "", "INSPECTIONDT": "", "WEB": "", "SCHTYPE": "", "GENDER": "", "RELIGION": ""}

new_row_sec = {"RECTYPE": "", "URN": "", "SCHNAME": "", "PCODE": "", "PCODE2": "", "TOWN": "", "P8MEA": "",
               "P8_BANDING": "", "ATT8SCR": "", "PTL2BASICS_95": "", "EBACCAPS": "", "PTEBACC_E_PTQ_EE": "",
               "OFSTEDRATING": "", "INSPECTIONDT": "", "WEB": "", "SCHTYPE": "", "GENDER": "", "GRAMMAR": "",
               "RELIGION": ""}

new_row_p16 = {"RECTYPE": "", "URN": "", "SCHNAME": "", "PCODE": "", "PCODE2": "", "TOWN": "", "VA_INS_ALEV": "",
               "PROGRESS_BAND_ALEV": "", "TALLPPE_ALEV_1618": "", "TALLPPEGRD_ALEV_1618": "", "OFSTEDRATING": "",
               "INSPECTIONDT": "", "WEB": "", "SCHTYPE": "", "GENDER": "", "GRAMMAR": "", "RELIGION": ""}

# compile lists used in dropdown filters
school_list1 = sorted([str(d) for d in df_pri["SCHNAME"].unique()])
school_list2 = sorted([str(d) for d in df_sec["SCHNAME"].unique()])
school_list3 = sorted([str(d) for d in df_p16["SCHNAME"].unique()])
school_list = list(set(school_list1 + school_list2 + school_list3))
school_list.sort()

town_list = sorted([str(d) for d in df_pri["TOWN"].unique()])
postcode_list = sorted([str(d) for d in df_pri["PCODE2"].unique()])

# Used to display count of rows
pri_recs = len(df_pri.index)
sec_recs = len(df_sec.index)
p16_recs = len(df_p16.index)

datatable_rows = 10
fontsize = 15

textcol = "dimgrey"
bgcol = "white"
bgcol2 = "whitesmoke"
col_1 = "teal"
col_2 = "midnightblue"
col_3 = "mediumslateblue"
col_4 = "slateblue"

star = "👨‍🎓"  # used for ratings display

# Markdown tables used for tooltips
markdown_table = f"""
|Star|Rating|
|:-------------|:-------------|
|{star * 5}|Well Above Average|
|{star * 4}|Above Average|
|{star * 3}|Average|
|{star * 2}|Below Average|
|{star * 1}|Well Below Average|
"""

markdown_table2 = """
|Abbr|Meaning|
|:-------------|:-------------|
|LOWCONV|Low Coverage|
|NA|Not Applicable|
|NE|No Entries|
|NEW|New School|
|NP|Not Published|
|SP|Small Percentage|
|SUPP|Suppressed|
"""

'''
===================
DASH LAYOUT SECTION
===================
'''

app.layout = html.Div(
    [
        html.Div(
            [
                html.H1("ENG Schools"),
                html.H3("(2018/19)")
            ],
            style={"text-align": "center", "font-weight": "bold"}
        ),

        html.Br(),

        html.Div(
            dbc.Col(
                [
                    html.P("Filters:"),

                    dcc.Dropdown(
                        id="school_drop",
                        options=[{"label": i, "value": i} for i in school_list],
                        multi=True,
                        placeholder="Select School",
                        style={"font-size": fontsize, "color": "black", "background-color": bgcol2}
                    ),

                    html.Br(),

                    dcc.Dropdown(
                        id="town_drop",
                        options=[{"label": i, "value": i} for i in town_list],
                        multi=True,
                        placeholder="Select Town",
                        style={"font-size": fontsize, "color": "black", "background-color": bgcol2}
                    ),

                    html.Br(),

                    dcc.Dropdown(
                        id="postcode_drop",
                        options=[{"label": i, "value": i} for i in postcode_list],
                        multi=True,
                        placeholder="Select Postcode District",
                        style={"font-size": fontsize, "color": "black", "background-color": bgcol2}
                    ),

                    html.Br(),

                ],
            ), style={"padding": "0px 18px 0px 18px"}
        ),

        html.Br(),

        html.Div(
            [
                dbc.Col(
                    [
                        html.P("School Type:"),

                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Checklist(
                                        id="school_type",
                                        options=[
                                            {"label": "Independent", "value": "Independent school"},
                                            {"label": "Maintained", "value": "Maintained school"},
                                            {"label": "Academy", "value": "Academy"},
                                            {"label": "College", "value": "College"},
                                            {"label": "Special", "value": "Special school"}
                                        ],
                                        value=[],
                                        labelStyle={"display": "block"},
                                        inputStyle={"margin-right": "10px"}
                                    )
                                ),

                                dbc.Col(
                                    [
                                        dcc.Checklist(
                                            id="grammar_sch",
                                            options=[
                                                {"label": "Grammar", "value": "GS"},
                                            ],
                                            value=[],
                                            inputStyle={"margin-right": "10px"}
                                        ),

                                        dcc.Checklist(
                                            id="gender",
                                            options=[
                                                {"label": "Boys", "value": "Boys"},
                                                {"label": "Girls", "value": "Girls"},
                                                {"label": "Mixed", "value": "Mixed"}
                                            ],
                                            value=[],
                                            labelStyle={"display": "block"},
                                            inputStyle={"margin-right": "10px"}
                                        ),

                                        dcc.Checklist(
                                            id="religion",
                                            options=[
                                                {"label": "Religion", "value": "Religion"}
                                            ],
                                            value=[],
                                            labelStyle={"display": "block"},
                                            inputStyle={"margin-right": "10px"}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(),

        html.Div(
            dcc.Loading(
                dcc.Graph(
                    id="school_map",
                    figure={},
                    config={"displayModeBar": False}
                )
            ), style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(),

        html.Div(
            html.H6("* hover over table headings for legend"),
            style={"text-align": "left", "font-style": "italic", "padding": "0px 0px 0px 20px"}
        ),

        html.Div(
            dbc.Row(
                [
                    dbc.Col(html.H4("PRIMARY"), style={"text-align": "center", "font-weight": "bold"}),
                    dbc.Col(html.H5("Total: "), style={"text-align": "right", "font-weight": "bold"}),
                    dbc.Col(html.H5(pri_recs), id="pri_recs", style={"text-align": "left", "font-weight": "bold"})
                ], style={"background": bgcol2}
            ), style={"padding": "0px 30px 0px 30px"}
        ),

        html.Br(),

        html.Div(
            [
                dcc.Loading(
                    dash_table.DataTable(
                        id="datatable_pri",

                        columns=[
                            {
                                "id": "SCHNAME",
                                "name": ["School"],
                                "type": "text"
                            },
                            {
                                "id": "READPROG_DESCR",
                                "name": ["📗Reading"],
                                "type": "text"
                            },
                            {
                                "id": "WRITPROG_DESCR",
                                "name": ["✏️Writing"],
                                "type": "text"
                            },
                            {
                                "id": "MATPROG_DESCR",
                                "name": ["📐Maths"],
                                "type": "text"
                            },
                            {
                                "id": "OFSTEDRATING",
                                "name": ["Ofsted Rating"],
                                "type": "text"
                            },
                            {
                                "id": "INSPECTIONDT",
                                "name": ["Last Inspected"],
                                "type": "datetime"
                            },
                            {
                                "id": "URN",
                                "name": ["URN"],
                                "type": "text"
                            },
                            {
                                "id": "SCHTYPE",
                                "name": ["School Type"],
                                "type": "text"
                            },
                            {
                                "id": "GENDER",
                                "name": ["Gender"],
                                "type": "text"
                            },
                            {
                                "id": "RELIGION",
                                "name": ["Religion"],
                                "type": "text"
                            },
                            {
                                "id": "TOWN",
                                "name": ["Town"],
                                "type": "text"
                            },
                            {
                                "id": "PCODE",
                                "name": ["Post Code"],
                                "type": "text"
                            },
                            {
                                "id": "WEBLINK",
                                "name": ["Website"],
                                "type": "text",
                                "presentation": "markdown"
                            }
                        ],

                        sort_action="native",
                        sort_mode="single",
                        filter_action="none",
                        page_action="native",
                        page_current=0,
                        page_size=datatable_rows,
                        fixed_rows={"headers": True},
                        fixed_columns={"headers": True, "data": 1},

                        style_table={
                            "overflowX": "auto",
                            "minWidth": "100%",
                            "height": "800px"
                        },

                        style_header={
                            "bold": True,
                            "color": "black",
                            "backgroundColor": "lightgrey",
                            "whiteSpace": "normal",
                            "height": "64px"
                        },

                        style_header_conditional=[
                            {
                                "if": {"column_id": col},
                                "textDecoration": "underline",
                                "textDecorationStyle": "dotted",
                            } for col in ["READPROG_DESCR", "WRITPROG_DESCR", "MATPROG_DESCR"]
                        ],

                        tooltip_header={
                            "READPROG_DESCR": {"value": markdown_table, "type": "markdown"},
                            "WRITPROG_DESCR": {"value": markdown_table, "type": "markdown"},
                            "MATPROG_DESCR": {"value": markdown_table, "type": "markdown"}
                        },

                        tooltip_delay=0,
                        tooltip_duration=None,

                        style_cell={
                            "color": textcol,
                            "backgroundColor": bgcol,
                            "font-family": "Verdana",
                            "font_size": fontsize,
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "minWidth": 88,
                            "maxWidth": 140,
                            "padding": "0px 10px 0px 10px"
                        },

                        style_cell_conditional=[
                            {"if": {"column_id": "SCHNAME"}, "textAlign": "left"},
                            {"if": {"column_id": "READPROG_DESCR"}, "textAlign": "left"},
                            {"if": {"column_id": "WRITPROG_DESCR"}, "textAlign": "left"},
                            {"if": {"column_id": "MATPROG_DESCR"}, "textAlign": "left"},
                            {"if": {"column_id": "OFSTEDRATING"}, "textAlign": "center"},
                            {"if": {"column_id": "INSPECTIONDT"}, "textAlign": "center"},
                            {"if": {"column_id": "URN"}, "textAlign": "center"},
                            {"if": {"column_id": "SCHTYPE"}, "textAlign": "left"},
                            {"if": {"column_id": "TOWN"}, "textAlign": "left"},
                            {"if": {"column_id": "PCODE"}, "textAlign": "left"},
                        ],

                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto"
                        },

                        css=[{"selector": ".row", "rule": "margin: 0; flex-wrap: nowrap"}],
                    )
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(), html.Br(),

        html.Div(
            dbc.Row(
                [
                    dbc.Col(html.H4("SECONDARY"), style={"text-align": "center", "font-weight": "bold"}),
                    dbc.Col(html.H5("Total: "), style={"text-align": "right", "font-weight": "bold"}),
                    dbc.Col(html.H5(sec_recs), id="sec_recs", style={"text-align": "left", "font-weight": "bold"})
                ], style={"background": bgcol2}
            ), style={"padding": "0px 30px 0px 30px"}
        ),

        html.Br(),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("GCSE Attainment 8", className="card-title"),
                            html.H5(
                                id="gcse_att8_avg",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_1,
                            "text-align": "center"
                        }
                    )
                ),

                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("Eng/Maths Grade5+", className="card-title"),
                            html.H5(
                                id="gcse_eng_maths_grade5_pct",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_2,
                            "text-align": "center"
                        }
                    )
                )
            ],
            className="mb-3",
            style={"padding": "0px 20px 0px 20px"}
        ),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("GCSE Entering EBacc", className="card-title"),
                            html.H5(
                                id="gcse_entering_ebacc",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_3,
                            "text-align": "center"
                        }
                    )
                ),

                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("GCSE EBacc Score", className="card-title"),
                            html.H5(
                                id="gcse_ebacc_score",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_4,
                            "text-align": "center"
                        }
                    )
                )
            ],
            className="mb-3",
            style={"padding": "0px 20px 0px 20px"}
        ),

        html.Div(
            [
                dcc.Loading(
                    dash_table.DataTable(
                        id="datatable_sec",

                        columns=[
                            {
                                "id": "SCHNAME",
                                "name": ["School"],
                                "type": "text"
                            },
                            {
                                "id": "P8_BANDING",
                                "name": ["Progress8"],
                                "type": "text"
                            },
                            {
                                "id": "P8MEA",
                                "name": ["Prog8 Score"],
                                "type": "text"
                            },
                            {
                                "id": "ATT8SCR",
                                "name": ["Attain8 Score"],
                                "type": "text"
                            },
                            {
                                "id": "PTL2BASICS_95",
                                "name": ["Eng/Maths"],
                                "type": "text"
                            },
                            {
                                "id": "PTEBACC_E_PTQ_EE",
                                "name": ["Enter EBacc"],
                                "type": "text"
                            },
                            {
                                "id": "EBACCAPS",
                                "name": ["EBacc Score"],
                                "type": "text"
                            },
                            {
                                "id": "OFSTEDRATING",
                                "name": ["Ofsted Rating"],
                                "type": "text"
                            },
                            {
                                "id": "INSPECTIONDT",
                                "name": ["Last Inspected"],
                                "type": "text"
                            },
                            {
                                "id": "URN",
                                "name": ["URN"],
                                "type": "text"
                            },
                            {
                                "id": "SCHTYPE",
                                "name": ["School Type"],
                                "type": "text"
                            },
                            {
                                "id": "GRAMMAR",
                                "name": ["Grammar"],
                                "type": "text"
                            },
                            {
                                "id": "GENDER",
                                "name": ["Gender"],
                                "type": "text"
                            },
                            {
                                "id": "RELIGION",
                                "name": ["Religion"],
                                "type": "text"
                            },
                            {
                                "id": "TOWN",
                                "name": ["Town"],
                                "type": "text"
                            },
                            {
                                "id": "PCODE",
                                "name": ["Post Code"],
                                "type": "text"
                            },
                            {
                                "id": "WEBLINK",
                                "name": ["Website"],
                                "type": "text",
                                "presentation": "markdown"
                            }
                        ],

                        sort_action="native",
                        sort_mode="single",
                        filter_action="none",
                        page_action="native",
                        page_current=0,
                        page_size=datatable_rows,
                        fixed_rows={"headers": True},
                        fixed_columns={"headers": True, "data": 1},

                        style_table={
                            "overflowX": "auto", "overflowY": "auto",
                            "minWidth": "100%",
                            "height": "800px"},

                        style_header={
                            "bold": True,
                            "color": "black",
                            "backgroundColor": "lightgrey",
                            "whiteSpace": "normal",
                            "height": "64px"
                        },

                        style_header_conditional=[
                            {
                                "if": {"column_id": col},
                                "textDecoration": "underline",
                                "textDecorationStyle": "dotted"
                            } for col in
                            ["P8_BANDING", "P8MEA", "ATT8SCR", "PTL2BASICS_95", "PTEBACC_E_PTQ_EE", "EBACCAPS"]
                        ],

                        tooltip_header={
                            "P8_BANDING": {"value": markdown_table, "type": "markdown"},
                            "P8MEA": {"value": markdown_table2, "type": "markdown"},
                            "ATT8SCR": {"value": markdown_table2, "type": "markdown"},
                            "PTL2BASICS_95": {"value": markdown_table2, "type": "markdown"},
                            "PTEBACC_E_PTQ_EE": {"value": markdown_table2, "type": "markdown"},
                            "EBACCAPS": {"value": markdown_table2, "type": "markdown"},
                        },

                        tooltip_delay=0,
                        tooltip_duration=None,

                        style_cell={
                            "color": textcol,
                            "backgroundColor": bgcol,
                            "font-family": "Verdana",
                            "font_size": fontsize,
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "minWidth": 88,
                            "maxWidth": 140,
                            "padding": "0px 10px 0px 10px"
                        },

                        style_cell_conditional=[
                            {"if": {"column_id": "SCHNAME"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "P8_BANDING"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "P8MEA"},
                             "textAlign": "center"},
                            {"if": {"column_id": "ATT8SCR"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_1
                             },
                            {"if": {"column_id": "PTL2BASICS_95"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_2
                             },
                            {"if": {"column_id": "PTEBACC_E_PTQ_EE"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_3
                             },
                            {"if": {"column_id": "EBACCAPS"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_4
                             },
                            {"if": {"column_id": "OFSTEDRATING"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "INSPECTIONDT"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "URN"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "SCHTYPE"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "GRAMMAR"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "TOWN"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "PCODE"},
                             "textAlign": "left"
                             },
                        ],

                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto"
                        },

                        css=[{"selector": ".row", "rule": "margin: 0; flex-wrap: nowrap"}],
                    )
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(), html.Br(),

        html.Div(
            dbc.Row(
                [
                    dbc.Col(html.H4("POST 16"), style={"text-align": "center", "font-weight": "bold"}),
                    dbc.Col(html.H5("Total: "), style={"text-align": "right", "font-weight": "bold"}),
                    dbc.Col(html.H5(p16_recs), id="p16_recs", style={"text-align": "left", "font-weight": "bold"})
                ], style={"background": bgcol2}
            ), style={"padding": "0px 30px 0px 30px"}
        ),

        html.Br(),

        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("Average A-Level Grade", className="card-title"),
                            html.H5(
                                id="alevel_grade_avg",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_1,
                            "text-align": "center"
                        }
                    )
                ),

                dbc.Col(
                    dbc.Card(
                        [
                            html.H6("Average A-Level Score", className="card-title"),
                            html.H5(
                                id="alevel_score_avg",
                                className="card-value",
                                style={"font-weight": "bold"}
                            )
                        ],
                        style={
                            "color": "white",
                            "background": col_2,
                            "text-align": "center"
                        }
                    )
                )
            ],
            className="mb-3",
            style={"padding": "0px 20px 0px 20px"}
        ),

        html.Div(
            [
                dcc.Loading(
                    dash_table.DataTable(
                        id="datatable_p16",

                        columns=[
                            {
                                "id": "SCHNAME",
                                "name": ["School"],
                                "type": "text"
                            },
                            {
                                "id": "PROGRESS_BAND_ALEV",
                                "name": ["Progress"],
                                "type": "text"
                            },
                            {
                                "id": "TALLPPEGRD_ALEV_1618",
                                "name": ["Avg Grade"],
                                "type": "text"
                            },
                            {
                                "id": "TALLPPE_ALEV_1618",
                                "name": ["Avg Points"],
                                "type": "text"
                            },
                            {
                                "id": "OFSTEDRATING",
                                "name": ["Ofsted Rating"],
                                "type": "text"
                            },
                            {
                                "id": "INSPECTIONDT",
                                "name": ["Last Inspected"],
                                "type": "text"
                            },
                            {
                                "id": "URN",
                                "name": ["URN"],
                                "type": "text"
                            },
                            {
                                "id": "SCHTYPE",
                                "name": ["School Type"],
                                "type": "text"
                            },
                            {
                                "id": "GRAMMAR",
                                "name": ["Grammar"],
                                "type": "text"
                            },
                            {
                                "id": "GENDER",
                                "name": ["Gender"],
                                "type": "text"
                            },
                            {
                                "id": "RELIGION",
                                "name": ["Religion"],
                                "type": "text"
                            },
                            {
                                "id": "TOWN",
                                "name": ["Town"],
                                "type": "text"
                            },
                            {
                                "id": "PCODE",
                                "name": ["Post Code"],
                                "type": "text"
                            },
                            {
                                "id": "WEBLINK",
                                "name": ["Website"],
                                "type": "text",
                                "presentation": "markdown"
                            }
                        ],

                        sort_action="native",
                        sort_mode="single",
                        filter_action="none",
                        page_action="native",
                        page_current=0,
                        page_size=datatable_rows,
                        fixed_rows={"headers": True},
                        fixed_columns={"headers": True, "data": 1},

                        style_table={
                            "overflowX": "auto", "overflowY": "auto",
                            "minWidth": "100%",
                            "height": "800px"
                        },

                        style_header={
                            "bold": True,
                            "color": "black",
                            "backgroundColor": "lightgrey",
                            "whiteSpace": "normal",
                            "height": "64px"
                        },

                        style_header_conditional=[
                            {
                                "if": {"column_id": col},
                                "textDecoration": "underline",
                                "textDecorationStyle": "dotted",
                            } for col in ["PROGRESS_BAND_ALEV", "TALLPPEGRD_ALEV_1618", "TALLPPE_ALEV_1618"]
                        ],

                        tooltip_header={
                            "PROGRESS_BAND_ALEV": {"value": markdown_table, "type": "markdown"},
                            "TALLPPEGRD_ALEV_1618": {"value": markdown_table2, "type": "markdown"},
                            "TALLPPE_ALEV_1618": {"value": markdown_table2, "type": "markdown"}
                        },

                        tooltip_delay=0,
                        tooltip_duration=None,

                        style_cell={
                            "color": textcol,
                            "backgroundColor": bgcol,
                            "font-family": "Verdana",
                            "font_size": fontsize,
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "minWidth": 88,
                            "maxWidth": 140,
                            "padding": "0px 10px 0px 10px"
                        },

                        style_cell_conditional=[
                            {"if": {"column_id": "SCHNAME"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "PROGRESS_BAND_ALEV"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "TALLPPEGRD_ALEV_1618"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_1
                             },
                            {"if": {"column_id": "TALLPPE_ALEV_1618"},
                             "textAlign": "center",
                             "color": "white",
                             "backgroundColor": col_2
                             },
                            {"if": {"column_id": "OFSTEDRATING"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "INSPECTIONDT"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "URN"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "SCHTYPE"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "GRAMMAR"},
                             "textAlign": "center"
                             },
                            {"if": {"column_id": "TOWN"},
                             "textAlign": "left"
                             },
                            {"if": {"column_id": "PCODE"},
                             "textAlign": "left"
                             },
                        ],

                        style_data={
                            "whiteSpace": "normal",
                            "height": "auto"
                        },

                        css=[{"selector": ".row", "rule": "margin: 0; flex-wrap: nowrap"}],
                    )
                )
            ], style={"padding": "0px 20px 0px 20px"}
        ),

        html.Br(), html.Br(), html.Br(),

        html.Div(
            html.P(
                ["Data Source: ",
                 html.A("GovUK",
                        href="https://www.compare-school-performance.service.gov.uk/download-data", target="_blank"
                        )
                 ]
            ),
            style={"padding": "0px 0px 0px 50px"}
        ),

        html.Div(
            html.P(
                ["Code: ",
                 html.A("Github", href="https://github.com/waiky8/eng-schools",
                        target="_blank")
                 ]
            ),
            style={"padding": "0px 0px 0px 50px"}
        ),

        # dummy DIV to trigger average_scores callback
        html.Div(
            id="dummy",
            children=[],
            style={"display": "none"}
        )
    ]
)

'''
============================
CALLBACK FOR DATATABLE & MAP
============================
'''


@app.callback(
    [
        Output("datatable_pri", "data"),
        Output("datatable_sec", "data"),
        Output("datatable_p16", "data"),
        Output("pri_recs", "children"),
        Output("sec_recs", "children"),
        Output("p16_recs", "children"),
        Output("school_map", "figure")
    ],
    [
        Input("school_drop", "value"),
        Input("town_drop", "value"),
        Input("postcode_drop", "value"),
        Input("school_type", "value"),
        Input("grammar_sch", "value"),
        Input("gender", "value"),
        Input("religion", "value")
    ]
)
def return_datatable(selected_school, selected_area, selected_postcode, selected_schtype, selected_grammar,
                     selected_gender, selected_religion):
    # print(str(datetime.now()), "[1] start apply filters...")

    '''
    ---------
    DATATABLE
    ---------
    '''

    # Check for selected school filter
    if selected_school is None or selected_school == []:
        df1_pri = df_pri.copy()
        df1_sec = df_sec.copy()
        df1_p16 = df_p16.copy()
    else:
        df1_pri = df_pri[df_pri["SCHNAME"].isin(selected_school)]
        df1_sec = df_sec[df_sec["SCHNAME"].isin(selected_school)]
        df1_p16 = df_p16[df_p16["SCHNAME"].isin(selected_school)]

    # Check for selected town filter
    if selected_area is None or selected_area == []:
        pass
    else:
        df1_pri = df1_pri[df1_pri["TOWN"].isin(selected_area)]
        df1_sec = df1_sec[df1_sec["TOWN"].isin(selected_area)]
        df1_p16 = df1_p16[df1_p16["TOWN"].isin(selected_area)]

    # Check for selected postcode filter
    if selected_postcode is None or selected_postcode == []:
        pass
    else:
        df1_pri = df1_pri[df1_pri["PCODE2"].isin(selected_postcode)]
        df1_sec = df1_sec[df1_sec["PCODE2"].isin(selected_postcode)]
        df1_p16 = df1_p16[df1_p16["PCODE2"].isin(selected_postcode)]

    # Check for selected independent school filter
    if selected_schtype is None or selected_schtype == []:
        pass
    else:
        df1_pri = df1_pri[df1_pri["SCHTYPE"].isin(selected_schtype)]
        df1_sec = df1_sec[df1_sec["SCHTYPE"].isin(selected_schtype)]
        df1_p16 = df1_p16[df1_p16["SCHTYPE"].isin(selected_schtype)]

    # Check for selected grammar school filter
    if selected_grammar is None or selected_grammar == []:
        pass
    else:
        df1_pri = df1_pri[df1_pri["SCHTYPE"].isin(["dummy!"])]
        df1_sec = df1_sec[df1_sec["GRAMMAR"].isin(["Yes"])]
        df1_p16 = df1_p16[df1_p16["GRAMMAR"].isin(["Yes"])]

    # Check for selected gender filter
    if selected_gender is None or selected_gender == []:
        pass
    else:
        df1_pri = df1_pri[df1_pri["GENDER"].isin(selected_gender)]
        df1_sec = df1_sec[df1_sec["GENDER"].isin(selected_gender)]
        df1_p16 = df1_p16[df1_p16["GENDER"].isin(selected_gender)]

    # Check for selected religion filter
    if selected_religion is None or selected_religion == []:
        pass
    else:
        df1_pri = df1_pri[~df1_pri["RELIGION"].isin(["Does not apply", "None", ""])]
        df1_sec = df1_sec[~df1_sec["RELIGION"].isin(["Does not apply", "None", ""])]
        df1_p16 = df1_p16[~df1_p16["RELIGION"].isin(["Does not apply", "None", ""])]

    df_pri_filtered = df1_pri.copy().sort_values(by=["SCHNAME"])
    df_sec_filtered = df1_sec.copy().sort_values(by=["SCHNAME"])
    df_p16_filtered = df1_p16.copy().sort_values(by=["SCHNAME"])

    # print(str(datetime.now()), "[2] start map rating to stars...")

    if len(df_pri_filtered) == 0:
        pass

    else:
        # Map reading progress to stars
        df_pri_filtered.loc[(df_pri_filtered.READPROG_DESCR == "1"), "READPROG_DESCR"] = star * 5
        df_pri_filtered.loc[(df_pri_filtered.READPROG_DESCR == "2"), "READPROG_DESCR"] = star * 4
        df_pri_filtered.loc[(df_pri_filtered.READPROG_DESCR == "3"), "READPROG_DESCR"] = star * 3
        df_pri_filtered.loc[(df_pri_filtered.READPROG_DESCR == "4"), "READPROG_DESCR"] = star * 2
        df_pri_filtered.loc[(df_pri_filtered.READPROG_DESCR == "5"), "READPROG_DESCR"] = star

        # Map writing progress to stars
        df_pri_filtered.loc[(df_pri_filtered.WRITPROG_DESCR == "1"), "WRITPROG_DESCR"] = star * 5
        df_pri_filtered.loc[(df_pri_filtered.WRITPROG_DESCR == "2"), "WRITPROG_DESCR"] = star * 4
        df_pri_filtered.loc[(df_pri_filtered.WRITPROG_DESCR == "3"), "WRITPROG_DESCR"] = star * 3
        df_pri_filtered.loc[(df_pri_filtered.WRITPROG_DESCR == "4"), "WRITPROG_DESCR"] = star * 2
        df_pri_filtered.loc[(df_pri_filtered.WRITPROG_DESCR == "5"), "WRITPROG_DESCR"] = star

        # Map maths progress to stars
        df_pri_filtered.loc[(df_pri_filtered.MATPROG_DESCR == "1"), "MATPROG_DESCR"] = star * 5
        df_pri_filtered.loc[(df_pri_filtered.MATPROG_DESCR == "2"), "MATPROG_DESCR"] = star * 4
        df_pri_filtered.loc[(df_pri_filtered.MATPROG_DESCR == "3"), "MATPROG_DESCR"] = star * 3
        df_pri_filtered.loc[(df_pri_filtered.MATPROG_DESCR == "4"), "MATPROG_DESCR"] = star * 2
        df_pri_filtered.loc[(df_pri_filtered.MATPROG_DESCR == "5"), "MATPROG_DESCR"] = star

    if len(df_sec_filtered) == 0:
        pass

    else:
        # Map progress 8 to stars
        df_sec_filtered.loc[(df_sec_filtered.P8_BANDING == "1"), "P8_BANDING"] = star * 5
        df_sec_filtered.loc[(df_sec_filtered.P8_BANDING == "2"), "P8_BANDING"] = star * 4
        df_sec_filtered.loc[(df_sec_filtered.P8_BANDING == "3"), "P8_BANDING"] = star * 3
        df_sec_filtered.loc[(df_sec_filtered.P8_BANDING == "4"), "P8_BANDING"] = star * 2
        df_sec_filtered.loc[(df_sec_filtered.P8_BANDING == "5"), "P8_BANDING"] = star

    if len(df_p16_filtered) == 0:
        pass

    else:
        # Map progress to stars
        df_p16_filtered.loc[(df_p16_filtered.PROGRESS_BAND_ALEV == "1"), "PROGRESS_BAND_ALEV"] = star * 5
        df_p16_filtered.loc[(df_p16_filtered.PROGRESS_BAND_ALEV == "2"), "PROGRESS_BAND_ALEV"] = star * 4
        df_p16_filtered.loc[(df_p16_filtered.PROGRESS_BAND_ALEV == "3"), "PROGRESS_BAND_ALEV"] = star * 3
        df_p16_filtered.loc[(df_p16_filtered.PROGRESS_BAND_ALEV == "4"), "PROGRESS_BAND_ALEV"] = star * 2
        df_p16_filtered.loc[(df_p16_filtered.PROGRESS_BAND_ALEV == "5"), "PROGRESS_BAND_ALEV"] = star

    df_pri_filtered["INSPECTIONDT"] = pd.to_datetime(df_pri_filtered["INSPECTIONDT"].astype(str),
                                                     format="%Y%m%d").dt.date
    df_sec_filtered["INSPECTIONDT"] = pd.to_datetime(df_sec_filtered["INSPECTIONDT"].astype(str),
                                                     format="%Y%m%d").dt.date
    df_p16_filtered["INSPECTIONDT"] = pd.to_datetime(df_p16_filtered["INSPECTIONDT"].astype(str),
                                                     format="%Y%m%d").dt.date

    pri_rows = len(df_pri_filtered.index)
    sec_rows = len(df_sec_filtered.index)
    p16_rows = len(df_p16_filtered.index)

    if pri_rows == 0:
        df_pri_filtered = df_pri_filtered.append(new_row_pri, ignore_index=True)

    if sec_rows == 0:
        df_sec_filtered = df_sec_filtered.append(new_row_sec, ignore_index=True)

    if p16_rows == 0:
        df_p16_filtered = df_p16_filtered.append(new_row_p16, ignore_index=True)

    df_pri_filtered["WEBLINK"] = df_pri_filtered.apply(format_url, axis=1)
    df_sec_filtered["WEBLINK"] = df_sec_filtered.apply(format_url, axis=1)
    df_p16_filtered["WEBLINK"] = df_p16_filtered.apply(format_url, axis=1)

    df_pri_updated = df_pri_filtered.to_dict("records")
    df_sec_updated = df_sec_filtered.to_dict("records")
    df_p16_updated = df_p16_filtered.to_dict("records")

    '''
    ----------------
    MAP WITH MARKERS
    ----------------
    '''
    df1 = df_pri_filtered.copy()[
        [
            "SCHNAME", "URN", "PHASE", "SCHTYPE", "OFSTEDRATING", "INSPECTIONDT", "LATITUDE", "LONGITUDE", "COLOUR1",
            "GENDER", "RELIGION"
        ]
    ]
    df2 = df_sec_filtered.copy()[
        [
            "SCHNAME", "URN", "PHASE", "SCHTYPE", "OFSTEDRATING", "INSPECTIONDT", "LATITUDE", "LONGITUDE", "COLOUR1",
            "GENDER", "RELIGION"
        ]
    ]
    df3 = df_p16_filtered.copy()[
        [
            "SCHNAME", "URN", "PHASE", "SCHTYPE", "OFSTEDRATING", "INSPECTIONDT", "LATITUDE", "LONGITUDE", "COLOUR1",
            "GENDER", "RELIGION"
        ]
    ]
    df_all = pd.concat([df1, df2, df3])
    df_all = df_all.drop_duplicates(subset=["URN"])
    df_all.loc[(pd.isna(df_all.OFSTEDRATING)), "OFSTEDRATING"] = "Not Available"
    df_all.loc[(pd.isna(df_all.INSPECTIONDT)), "INSPECTIONDT"] = ""

    lat_mean = pd.to_numeric(df_all["LATITUDE"]).mean()
    lon_mean = pd.to_numeric(df_all["LONGITUDE"]).mean()

    fig = go.Figure(
        go.Scattermapbox(
            lat=df_all["LATITUDE"],
            lon=df_all["LONGITUDE"],
            mode="markers",
            marker={"color": df_all["COLOUR1"], "size": 14},
            name="",
            text=df_all["SCHNAME"],
            customdata=np.stack(
                (
                    df_all["PHASE"],
                    df_all["SCHTYPE"],
                    df_all["GENDER"],
                    df_all["OFSTEDRATING"],
                    df_all["INSPECTIONDT"],
                    df_all["RELIGION"]
                ),
                axis=-1
            ),
            hovertemplate="<br><b>School</b>: %{text}" + \
                          "<br><b>Phase</b>: %{customdata[0]}" + \
                          "<br><b>School Type</b>: %{customdata[1]}" + \
                          "<br><b>Gender</b>: %{customdata[2]}" + \
                          "<br><b>Ofsted Rating</b>: %{customdata[3]}" + \
                          "<br><b>Inspection Date</b>: %{customdata[4]}" + \
                          "<br><b>Religion</b>: %{customdata[5]}"
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
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        ),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    # print(str(datetime.now()), "[3] done...")

    return df_pri_updated, df_sec_updated, df_p16_updated, pri_rows, sec_rows, p16_rows, fig


'''
================================================
CALLBACK FOR AVERAGE GCSE & A-LEVEL PERFORMANCES
================================================
'''


@app.callback(
    [
        Output("gcse_att8_avg", "children"),
        Output("gcse_eng_maths_grade5_pct", "children"),
        Output("gcse_entering_ebacc", "children"),
        Output("gcse_ebacc_score", "children"),
        Output("alevel_grade_avg", "children"),
        Output("alevel_score_avg", "children")
    ],
    Input("dummy", "children")
)
def return_scores(none):
    gcse_att8 = df_eng_avg["GCSEATT8"][0]
    gcse_eng_maths_grade5 = df_eng_avg["GCSEENGMAT5"][0]
    gcse_enter_ebaccs = df_eng_avg["EBACCENT"][0]
    gcse_ebaccs_score = df_eng_avg["EBACCSCORE"][0]
    alevel_grade = df_eng_avg["ALGRADE"][0]
    alevel_score = df_eng_avg["ALSCORE"][0]

    return gcse_att8, gcse_eng_maths_grade5, gcse_enter_ebaccs, gcse_ebaccs_score, alevel_grade, alevel_score


'''
==============================================
FORMAT WEB LINK TO BE 'CLICKABLE' IN DATATABLE
==============================================
'''


def format_url(row):
    if str(row["WEB"]).startswith("http"):
        return "[{0}]({0})".format(row["WEB"])
    else:
        return ""


if __name__ == "__main__":
    app.run_server(debug=True)
