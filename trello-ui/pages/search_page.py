"""Search page layout for Trello Archive UI."""
import dash_bootstrap_components as dbc
from dash import html, dcc
from components.search import create_filter_panel


def create_search_page_layout():
    """
    Create the search page layout.

    Returns:
    html.Div: Search page layout
    """
    return html.Div([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H2("Search Cards", className="mb-2"),
                html.P("Find and filter your archived Trello cards",
                      className="text-muted")
            ])
        ], className="mb-4"),

        # Main content: Filter sidebar + Results
        dbc.Row([
            # Left column: Filters
            dbc.Col([
                create_filter_panel([], [])  # Will be populated with actual data
            ], width=12, lg=3, className="mb-4"),

            # Right column: Search results
            dbc.Col([
                # Results header
                html.Div(id="results-header-container", className="mb-3"),

                # Loading state
                dcc.Loading(
                    id="loading-search-results",
                    type="default",
                    children=[
                        # Card results
                        html.Div(id="search-results-container")
                    ]
                ),

                # Pagination controls
                html.Div([
                    dbc.ButtonGroup([
                        dbc.Button("‹ Previous", id="prev-page", size="sm", color="secondary", outline=True, disabled=True),
                        html.Div(id="pagination-container", className="d-inline-block"),
                        dbc.Button("Next ›", id="next-page", size="sm", color="secondary", outline=True, disabled=True),
                    ])
                ], className="d-flex justify-content-center mt-4")
            ], width=12, lg=9)
        ]),

        # Card detail modal placeholder
        html.Div(id="card-modal-container"),

        # Store components for state management
        dcc.Store(id="current-page-store", data=1),
        dcc.Store(id="search-filters-store", data={}),
    ], className="container-fluid p-4")
