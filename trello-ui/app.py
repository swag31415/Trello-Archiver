"""Main application file for Trello Archive UI."""
import dash
from dash import html, dcc, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc

# Import database functions
from database import (
    get_completion_stats, get_cards_by_list, get_completion_over_time,
    get_card_flow_data, get_card_complexity_stats, get_all_lists,
    get_all_labels, search_cards, count_cards, get_card_by_id,
    get_card_labels, get_card_comments, get_card_checklists,
    get_checklist_items, get_card_attachments, get_card_path,
    get_completion_by_day_of_week, get_completion_by_time_of_day
)

# Import components
from components import (
    create_completion_trend_chart, create_chord_diagram, create_stats_card,
    create_filter_panel, create_card_list, create_pagination_controls,
    create_results_header, create_card_detail_modal,
    create_day_of_week_chart, create_time_of_day_chart
)

# Import pages
from pages import create_dashboard_layout, create_search_page_layout

# Import utilities
from utils import calculate_completion_rate

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP
    ],
    suppress_callback_exceptions=True
)

app.title = "Trello Archive UI"

# App layout with navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("📊 Trello Archive", href="/", className="ms-2"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/", id="nav-dashboard")),
                dbc.NavItem(dbc.NavLink("Search", href="/search", id="nav-search")),
            ], navbar=True)
        ], fluid=True),
        color="dark",
        dark=True,
        sticky="top",
        className="mb-4"
    ),

    # Page content
    html.Div(id='page-content')
])


# ============================================================================
# ROUTING CALLBACK
# ============================================================================

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to appropriate page based on URL."""
    if pathname == '/search':
        return create_search_page_layout()
    else:  # Default to dashboard
        return create_dashboard_layout()


# ============================================================================
# DASHBOARD CALLBACKS
# ============================================================================

@app.callback(
    [
        Output('total-cards-stat', 'children'),
        Output('completed-cards-stat', 'children'),
        Output('completion-rate-stat', 'children'),
        Output('total-lists-stat', 'children'),
    ],
    Input('url', 'pathname')
)
def update_dashboard_stats(pathname):
    """Update dashboard statistics cards."""
    if pathname != '/' and pathname != '':
        return [html.Div()] * 4

    stats = get_completion_stats()

    total_cards = stats.get('total_cards', 0)
    completed_cards = stats.get('completed_cards', 0)
    total_lists = stats.get('total_lists', 0)
    completion_rate = calculate_completion_rate(completed_cards, total_cards)

    return [
        create_stats_card("Total Cards", total_cards, color="primary"),
        create_stats_card("Completed", completed_cards, color="success"),
        create_stats_card("Completion Rate", f"{completion_rate}%", color="info"),
        create_stats_card("Total Lists", total_lists, color="warning"),
    ]


# ============================================================================
# CHORD DIAGRAM CALLBACKS
# ============================================================================

@app.callback(
    Output('list-filter-collapse', 'is_open'),
    Input('toggle-lists-btn', 'n_clicks'),
    State('list-filter-collapse', 'is_open'),
    prevent_initial_call=True
)
def toggle_list_filter(n_clicks, is_open):
    """Toggle the list filter collapse."""
    return not is_open


@app.callback(
    [
        Output('chord-list-filter', 'options'),
        Output('chord-list-filter', 'value'),
        Output('chord-all-lists-store', 'data')
    ],
    [
        Input('url', 'pathname'),
        Input('date-range-store', 'data')
    ]
)
def populate_chord_lists(pathname, date_range):
    """Populate chord diagram list filter options based on date range."""
    if pathname != '/' and pathname != '':
        return [], [], []

    # Extract date range if available
    start_date = None
    end_date = None
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')

    # Get all unique lists from flow data
    flow_data = get_card_flow_data(start_date=start_date, end_date=end_date)
    if not flow_data:
        return [], [], []

    sources = [item['source'] for item in flow_data]
    targets = [item['target'] for item in flow_data]
    all_lists = sorted(list(set(sources + targets)))

    # Create options for checklist
    options = [{'label': list_name, 'value': list_name} for list_name in all_lists]

    # Default selected lists
    default_lists = ['NOE', 'Done', 'Backlog', 'In waiting']
    # Only include lists that actually exist in the data
    selected_lists = [l for l in default_lists if l in all_lists]

    # If none of the default lists exist, select all
    if not selected_lists:
        selected_lists = all_lists

    return options, selected_lists, all_lists


@app.callback(
    Output('sankey-diagram', 'figure'),
    [
        Input('chord-list-filter', 'value'),
        Input('url', 'pathname'),
        Input('date-range-store', 'data')
    ]
)
def update_chord_filtered(selected_lists, pathname, date_range):
    """Update chord diagram based on selected lists and date range."""
    if pathname != '/' and pathname != '':
        return {}

    # Extract date range if available
    start_date = None
    end_date = None
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')

    # Get all flow data (filtered by date range)
    flow_data = get_card_flow_data(start_date=start_date, end_date=end_date)

    if not flow_data:
        return create_chord_diagram([])

    # Filter flow data to only include selected lists
    if selected_lists:
        filtered_data = [
            item for item in flow_data
            if item['source'] in selected_lists and item['target'] in selected_lists
        ]
    else:
        filtered_data = flow_data

    return create_chord_diagram(filtered_data)


# ============================================================================
# COMPLETION CHART ZOOM CALLBACK
# ============================================================================

@app.callback(
    [
        Output('completion-trend-chart', 'figure'),
        Output('date-range-store', 'data')
    ],
    [
        Input('url', 'pathname'),
        Input('completion-trend-chart', 'relayoutData')
    ]
)
def update_completion_chart(pathname, relayout_data):
    """Update completion chart with histogram and track date range."""
    if pathname != '/' and pathname != '':
        return {}, None

    # Get day-level data for histogram binning (all data)
    data = get_completion_over_time(interval='day')

    # Extract x-axis range from relayout data
    x_range = None
    if relayout_data:
        # Check for zoom/pan events
        if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
            x_range = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        elif 'xaxis.range' in relayout_data:
            x_range = relayout_data['xaxis.range']

    # Create chart with filtered data if range is set
    fig = create_completion_trend_chart(data, x_range=x_range)

    # Store date range for other charts
    date_range_data = None
    if x_range and len(x_range) == 2:
        import pandas as pd
        # Convert to YYYY-MM-DD format for database queries
        start_date = pd.to_datetime(x_range[0]).strftime('%Y-%m-%d')
        end_date = pd.to_datetime(x_range[1]).strftime('%Y-%m-%d')
        date_range_data = {'start': start_date, 'end': end_date}

    return fig, date_range_data


@app.callback(
    Output('day-of-week-chart', 'figure'),
    [
        Input('url', 'pathname'),
        Input('date-range-store', 'data')
    ]
)
def update_day_of_week_chart(pathname, date_range):
    """Update day of week chart with optional date filtering."""
    if pathname != '/' and pathname != '':
        return {}

    # Extract date range if available
    start_date = None
    end_date = None
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')

    data = get_completion_by_day_of_week(start_date=start_date, end_date=end_date)
    return create_day_of_week_chart(data)


@app.callback(
    Output('time-of-day-chart', 'figure'),
    [
        Input('url', 'pathname'),
        Input('date-range-store', 'data')
    ]
)
def update_time_of_day_chart(pathname, date_range):
    """Update time of day chart with optional date filtering."""
    if pathname != '/' and pathname != '':
        return {}

    # Extract date range if available
    start_date = None
    end_date = None
    if date_range:
        start_date = date_range.get('start')
        end_date = date_range.get('end')

    data = get_completion_by_time_of_day(start_date=start_date, end_date=end_date)
    return create_time_of_day_chart(data)


# ============================================================================
# SEARCH PAGE CALLBACKS
# ============================================================================

@app.callback(
    Output('list-filter', 'options'),
    Input('url', 'pathname')
)
def populate_list_filter(pathname):
    """Populate list filter options."""
    if pathname != '/search':
        return []

    lists = get_all_lists()
    return [
        {"label": list_item.get('list', 'Unknown'), "value": list_item.get('list', 'Unknown')}
        for list_item in lists
    ]


@app.callback(
    Output('label-filter', 'options'),
    Input('url', 'pathname')
)
def populate_label_filter(pathname):
    """Populate label filter options."""
    if pathname != '/search':
        return []

    labels = get_all_labels()
    return [
        {"label": label.get('name', 'Unlabeled'), "value": label.get('name', 'Unlabeled')}
        for label in labels
        if label.get('name')
    ]


@app.callback(
    [
        Output('search-results-container', 'children'),
        Output('results-header-container', 'children'),
        Output('pagination-container', 'children'),
        Output('current-page-store', 'data'),
        Output('prev-page', 'disabled'),
        Output('next-page', 'disabled'),
    ],
    [
        Input('search-input', 'value'),
        Input('start-date-picker', 'date'),
        Input('end-date-picker', 'date'),
        Input('list-filter', 'value'),
        Input('label-filter', 'value'),
        Input('completion-filter', 'value'),
        Input('content-filters', 'value'),
        Input('sort-field', 'value'),
        Input('sort-order', 'value'),
        Input({'type': 'page-btn', 'index': ALL}, 'n_clicks'),
        Input('prev-page', 'n_clicks'),
        Input('next-page', 'n_clicks'),
        Input('clear-filters-btn', 'n_clicks'),
    ],
    [
        State('current-page-store', 'data'),
        State('url', 'pathname'),
    ]
)
def update_search_results(search_text, start_date, end_date, list_filter, label_filter,
                         completion_filter, content_filters, sort_field, sort_order,
                         page_clicks, prev_click, next_click, clear_click,
                         current_page, pathname):
    """Update search results based on filters (all filters are optional)."""
    if pathname != '/search':
        return html.Div(), html.Div(), html.Div(), 1, True, True

    # Normalize empty inputs to None
    search_text = search_text if search_text and search_text.strip() else None
    start_date = start_date if start_date else None
    end_date = end_date if end_date else None
    list_filter = list_filter if list_filter and len(list_filter) > 0 else None
    label_filter = label_filter if label_filter and len(label_filter) > 0 else None
    content_filters = content_filters if content_filters and len(content_filters) > 0 else None
    sort_field = sort_field if sort_field else 'create_date'
    sort_order = sort_order if sort_order else 'DESC'

    # Determine current page
    triggered_id = ctx.triggered_id
    current_page = current_page or 1

    if triggered_id == 'clear-filters-btn':
        # Reset to page 1 when clearing filters
        current_page = 1
    elif triggered_id == 'prev-page' and current_page > 1:
        current_page -= 1
    elif triggered_id == 'next-page':
        current_page += 1
    elif isinstance(triggered_id, dict) and triggered_id.get('type') == 'page-btn':
        current_page = triggered_id.get('index', 1)

    # Reset to page 1 if filters changed
    if triggered_id not in ['prev-page', 'next-page', 'clear-filters-btn'] and \
       not (isinstance(triggered_id, dict) and triggered_id.get('type') == 'page-btn'):
        current_page = 1

    # Build filter parameters
    completed_filter_val = None
    if completion_filter and completion_filter != 'all':
        if completion_filter == 'completed':
            completed_filter_val = True
        elif completion_filter == 'pending':
            completed_filter_val = False

    has_attachments = 'has_attachments' in content_filters if content_filters else None
    has_comments = 'has_comments' in content_filters if content_filters else None
    has_checklists = 'has_checklists' in content_filters if content_filters else None
    has_due_date = 'has_due_date' in content_filters if content_filters else None

    # Clear filters if button clicked
    if triggered_id == 'clear-filters-btn':
        search_text = None
        start_date = None
        end_date = None
        list_filter = None
        label_filter = None
        completed_filter_val = None
        has_attachments = None
        has_comments = None
        has_checklists = None
        has_due_date = None

    per_page = 20
    offset = (current_page - 1) * per_page

    # Get filtered cards
    cards = search_cards(
        search_text=search_text,
        list_filter=list_filter[0] if list_filter else None,
        label_filter=label_filter[0] if label_filter else None,
        completed_filter=completed_filter_val,
        start_date=start_date,
        end_date=end_date,
        has_attachments=has_attachments,
        has_comments=has_comments,
        has_checklists=has_checklists,
        has_due_date=has_due_date,
        sort_by=sort_field,
        sort_order=sort_order,
        limit=per_page,
        offset=offset
    )

    # Get total count
    total_count = count_cards(
        search_text=search_text,
        list_filter=list_filter[0] if list_filter else None,
        label_filter=label_filter[0] if label_filter else None,
        completed_filter=completed_filter_val,
        start_date=start_date,
        end_date=end_date,
        has_attachments=has_attachments,
        has_comments=has_comments,
        has_checklists=has_checklists,
        has_due_date=has_due_date
    )

    total_pages = max(1, (total_count + per_page - 1) // per_page)

    # Ensure current page is within bounds
    current_page = max(1, min(current_page, total_pages))

    # Create results
    results_list = create_card_list(cards)
    results_header = create_results_header(total_count, current_page, total_pages, per_page)
    pagination = create_pagination_controls(current_page, total_pages)

    # Update prev/next button states
    prev_disabled = current_page <= 1
    next_disabled = current_page >= total_pages

    return results_list, results_header, pagination, current_page, prev_disabled, next_disabled


# ============================================================================
# CARD DETAIL MODAL CALLBACKS
# ============================================================================

@app.callback(
    Output('card-modal-container', 'children'),
    [Input({'type': 'view-card-btn', 'index': ALL}, 'n_clicks')],
    [State('url', 'pathname')],
    prevent_initial_call=True
)
def open_card_modal(n_clicks, pathname):
    """Open card detail modal when view button is clicked."""
    if not ctx.triggered_id or pathname != '/search':
        return html.Div()

    # Check if any button was actually clicked (not just rendered)
    if not any(n_clicks) or all(n is None for n in n_clicks):
        return html.Div()

    # Get the card ID from the triggered button
    card_id = ctx.triggered_id.get('index')

    if not card_id:
        return html.Div()

    # Fetch card data
    card = get_card_by_id(card_id)
    if not card:
        return html.Div()

    # Fetch related data
    labels = get_card_labels(card_id)
    comments = get_card_comments(card_id)
    checklists_data = get_card_checklists(card_id)
    attachments = get_card_attachments(card_id)
    path_data = get_card_path(card_id)

    # Get checklist items for each checklist
    checklists = []
    for checklist in checklists_data:
        items = get_checklist_items(checklist['id'])
        checklists.append({
            **checklist,
            'items': items
        })

    # Create modal
    modal = create_card_detail_modal(
        card, labels, comments, checklists, attachments, path_data
    )

    # Make modal open by default
    modal.is_open = True

    return modal


@app.callback(
    Output('card-detail-modal', 'is_open'),
    [Input('close-card-modal', 'n_clicks')],
    [State('card-detail-modal', 'is_open')],
    prevent_initial_call=True
)
def close_modal(n_clicks, is_open):
    """Close the card detail modal."""
    return False


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
