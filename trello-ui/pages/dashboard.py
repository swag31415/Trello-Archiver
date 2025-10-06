"""Dashboard page layout for Trello Archive UI."""
import dash_bootstrap_components as dbc
from dash import html, dcc
from components.cards import create_stats_card


def create_dashboard_layout():
    """
    Create the dashboard page layout.

    Returns:
        html.Div: Dashboard layout
    """
    return html.Div([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H2("Trello Archive Dashboard", className="mb-2"),
                html.P("Overview and analytics of your archived Trello data",
                      className="text-muted")
            ])
        ], className="mb-4"),

        # Statistics cards row
        dbc.Row([
            dbc.Col(
                html.Div(id="total-cards-stat"),
                width=12, lg=3, className="mb-3"
            ),
            dbc.Col(
                html.Div(id="completed-cards-stat"),
                width=12, lg=3, className="mb-3"
            ),
            dbc.Col(
                html.Div(id="completion-rate-stat"),
                width=12, lg=3, className="mb-3"
            ),
            dbc.Col(
                html.Div(id="total-lists-stat"),
                width=12, lg=3, className="mb-3"
            ),
        ], className="mb-4"),

        # Charts row 1: Completion trend (full width)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Card Completion Over Time", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="completion-trend-chart", config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], width=12, className="mb-4"),
        ]),

        # Charts row 2: Day of week and time of day
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Completions by Day of Week", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="day-of-week-chart", config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], width=12, lg=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Completions by Time of Day", className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(id="time-of-day-chart", config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], width=12, lg=6, className="mb-4"),
        ]),

        # Charts row 3: Chord diagram with list filter
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.Row([
                            dbc.Col(html.H5("Card Flow Between Lists", className="mb-0"), width="auto"),
                            dbc.Col([
                                dbc.Button(
                                    "Toggle Lists",
                                    id="toggle-lists-btn",
                                    color="primary",
                                    size="sm",
                                    outline=True
                                )
                            ], width="auto", className="ms-auto")
                        ], align="center")
                    ]),
                    dbc.CardBody([
                        dbc.Collapse([
                            dbc.Card([
                                dbc.CardBody([
                                    html.Label("Select Lists to Display:", className="fw-bold mb-2"),
                                    dcc.Checklist(
                                        id="chord-list-filter",
                                        options=[],
                                        value=[],
                                        inline=False,
                                        labelStyle={'display': 'block', 'margin-bottom': '5px'}
                                    )
                                ], className="p-2")
                            ], className="mb-3")
                        ], id="list-filter-collapse", is_open=False),
                        dcc.Graph(id="sankey-diagram", config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], width=12, className="mb-4"),
        ]),

        # Hidden stores for state management
        dcc.Store(id='chord-all-lists-store', data=[]),
        dcc.Store(id='date-range-store', data=None)
    ], className="container-fluid p-4")
