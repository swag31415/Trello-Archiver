"""Search and filter components for Trello Archive UI."""
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime, timedelta


def create_search_input():
    """
    Create a search input component.

    Returns:
        dbc.Input: Search input
    """
    return dbc.Input(
        id="search-input",
        type="text",
        placeholder="Search cards by name or description...",
        className="mb-3",
        debounce=True
    )


def create_date_range_picker():
    """
    Create a date range picker (optional - no default values).

    Returns:
        html.Div: Date range picker container
    """
    return html.Div([
        html.Label("Date Range (Optional)", className="form-label fw-bold"),
        dbc.Row([
            dbc.Col([
                html.Label("From:", className="small text-muted"),
                dcc.DatePickerSingle(
                    id='start-date-picker',
                    date=None,
                    placeholder='Select start date',
                    display_format='YYYY-MM-DD',
                    className="mb-2"
                )
            ], width=6),
            dbc.Col([
                html.Label("To:", className="small text-muted"),
                dcc.DatePickerSingle(
                    id='end-date-picker',
                    date=None,
                    placeholder='Select end date',
                    display_format='YYYY-MM-DD',
                    className="mb-2"
                )
            ], width=6)
        ])
    ], className="mb-3")


def create_list_filter(lists):
    """
    Create a multi-select dropdown for filtering by list.

    Args:
        lists: List of list name dictionaries

    Returns:
        html.Div: List filter component
    """
    options = [
        {"label": list_item.get('list', 'Unknown'), "value": list_item.get('list', 'Unknown')}
        for list_item in lists
    ]

    return html.Div([
        html.Label("Filter by List", className="form-label fw-bold"),
        dcc.Dropdown(
            id="list-filter",
            options=options,
            multi=True,
            placeholder="Select lists...",
            className="mb-3"
        )
    ])


def create_label_filter(labels):
    """
    Create a multi-select dropdown for filtering by label.

    Args:
        labels: List of label dictionaries

    Returns:
        html.Div: Label filter component
    """
    options = [
        {"label": label.get('name', 'Unlabeled'), "value": label.get('name', 'Unlabeled')}
        for label in labels
        if label.get('name')
    ]

    return html.Div([
        html.Label("Filter by Label", className="form-label fw-bold"),
        dcc.Dropdown(
            id="label-filter",
            options=options,
            multi=True,
            placeholder="Select labels...",
            className="mb-3"
        )
    ])


def create_completion_filter():
    """
    Create a completion status filter.

    Returns:
        html.Div: Completion filter component
    """
    return html.Div([
        html.Label("Completion Status", className="form-label fw-bold"),
        dcc.Dropdown(
            id="completion-filter",
            options=[
                {"label": "All Cards", "value": "all"},
                {"label": "Completed Only", "value": "completed"},
                {"label": "Pending Only", "value": "pending"}
            ],
            value="all",
            clearable=False,
            className="mb-3"
        )
    ])


def create_content_filters():
    """
    Create checkboxes for filtering by content (attachments, comments, etc.).

    Returns:
        html.Div: Content filters component
    """
    return html.Div([
        html.Label("Content Filters", className="form-label fw-bold"),
        dbc.Checklist(
            id="content-filters",
            options=[
                {"label": " Has Attachments", "value": "has_attachments"},
                {"label": " Has Comments", "value": "has_comments"},
                {"label": " Has Checklists", "value": "has_checklists"},
                {"label": " Has Due Date", "value": "has_due_date"}
            ],
            value=[],
            className="mb-3"
        )
    ])


def create_sort_controls():
    """
    Create sort controls (field and order).

    Returns:
        html.Div: Sort controls component
    """
    return html.Div([
        html.Label("Sort By", className="form-label fw-bold"),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id="sort-field",
                    options=[
                        {"label": "Creation Date", "value": "create_date"},
                        {"label": "Completion Date", "value": "end_date"},
                        {"label": "Card Name", "value": "name"},
                        {"label": "List", "value": "list"}
                    ],
                    value="create_date",
                    clearable=False,
                    className="mb-2"
                )
            ], width=7),
            dbc.Col([
                dcc.Dropdown(
                    id="sort-order",
                    options=[
                        {"label": "↓ Desc", "value": "DESC"},
                        {"label": "↑ Asc", "value": "ASC"}
                    ],
                    value="DESC",
                    clearable=False,
                    className="mb-2"
                )
            ], width=5)
        ])
    ], className="mb-3")


def create_filter_panel(lists, labels):
    """
    Create a complete filter panel with all filter options.

    Args:
        lists: List of available lists
        labels: List of available labels

    Returns:
        dbc.Card: Filter panel card
    """
    return dbc.Card([
        dbc.CardHeader(
            html.H5("Search & Filter", className="mb-0")
        ),
        dbc.CardBody([
            create_search_input(),
            html.Hr(),
            create_date_range_picker(),
            html.Hr(),
            create_list_filter(lists),
            create_label_filter(labels),
            html.Hr(),
            create_completion_filter(),
            html.Hr(),
            create_content_filters(),
            html.Hr(),
            create_sort_controls(),
            html.Hr(),
            dbc.Button(
                "Clear All Filters",
                id="clear-filters-btn",
                color="secondary",
                outline=True,
                className="w-100"
            )
        ])
    ], className="shadow-sm sticky-top", style={"top": "20px"})


def create_results_header(total_results, current_page, total_pages, per_page):
    """
    Create a header showing search results information.

    Args:
        total_results: Total number of results
        current_page: Current page number
        total_pages: Total number of pages
        per_page: Results per page

    Returns:
        html.Div: Results header
    """
    start = (current_page - 1) * per_page + 1
    end = min(current_page * per_page, total_results)

    return html.Div([
        html.H5([
            f"Search Results ",
            dbc.Badge(f"{total_results}", color="primary", className="ms-2")
        ]),
        html.P(
            f"Showing {start}-{end} of {total_results} cards (Page {current_page} of {total_pages})",
            className="text-muted mb-0"
        )
    ], className="mb-3")


def create_loading_spinner():
    """
    Create a loading spinner.

    Returns:
        dbc.Spinner: Loading spinner
    """
    return dbc.Spinner(
        html.Div(id="loading-content"),
        color="primary",
        type="border",
        spinner_style={"width": "3rem", "height": "3rem"}
    )


def create_quick_filters():
    """
    Create quick filter buttons for common searches.

    Returns:
        html.Div: Quick filters
    """
    return html.Div([
        html.Label("Quick Filters", className="form-label fw-bold mb-2"),
        dbc.ButtonGroup([
            dbc.Button("All", id="quick-all", size="sm", outline=True, color="primary"),
            dbc.Button("Recent", id="quick-recent", size="sm", outline=True, color="primary"),
            dbc.Button("Completed", id="quick-completed", size="sm", outline=True, color="success"),
            dbc.Button("Pending", id="quick-pending", size="sm", outline=True, color="warning"),
        ], className="w-100 mb-3")
    ])


def create_export_options():
    """
    Create export options (for future implementation).

    Returns:
        html.Div: Export options
    """
    return html.Div([
        html.Label("Export", className="form-label fw-bold"),
        dbc.ButtonGroup([
            dbc.Button(
                [html.I(className="bi bi-file-earmark-text me-1"), "CSV"],
                id="export-csv",
                size="sm",
                outline=True,
                color="secondary",
                disabled=True
            ),
            dbc.Button(
                [html.I(className="bi bi-file-earmark-pdf me-1"), "PDF"],
                id="export-pdf",
                size="sm",
                outline=True,
                color="secondary",
                disabled=True
            ),
        ], className="w-100")
    ], className="mb-3")
