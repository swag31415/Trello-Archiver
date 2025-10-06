"""Card display components for Trello Archive UI."""
import dash_bootstrap_components as dbc
from dash import html, dcc
from utils.helpers import format_date, truncate_text, format_date_relative


def create_card_component(card):
    """
    Create a Bootstrap card component for displaying a Trello card.

    Args:
        card: Card dictionary

    Returns:
        dbc.Card: Card component
    """
    card_id = card.get('id', 0)
    card_name = card.get('name', 'Untitled')
    card_desc = card.get('desc', '')
    card_list = card.get('list', 'Unknown')
    completed = card.get('completed', 0)
    create_date = card.get('create_date', '')
    end_date = card.get('end_date', '')
    due_date = card.get('due_date', '')

    # Status badge
    status_badge = dbc.Badge(
        "Completed" if completed else "Pending",
        color="success" if completed else "secondary",
        className="me-1"
    )

    # List badge
    list_badge = dbc.Badge(card_list, color="primary", pill=True)

    # Card header with name and badges
    card_header = dbc.CardHeader([
        html.H5(truncate_text(card_name, 60), className="mb-2"),
        html.Div([status_badge, list_badge])
    ])

    # Card body with description and dates
    card_body_content = []

    if card_desc:
        card_body_content.append(
            html.P(truncate_text(card_desc, 150), className="card-text text-muted mb-2")
        )

    # Date information
    date_info = []
    if create_date:
        date_info.append(html.Small([
            html.I(className="bi bi-calendar-plus me-1"),
            f"Created: {format_date(create_date, '%Y-%m-%d')}"
        ], className="text-muted me-3"))

    if completed and end_date:
        date_info.append(html.Small([
            html.I(className="bi bi-calendar-check me-1"),
            f"Completed: {format_date(end_date, '%Y-%m-%d')}"
        ], className="text-success me-3"))

    if due_date:
        date_info.append(html.Small([
            html.I(className="bi bi-alarm me-1"),
            f"Due: {format_date(due_date, '%Y-%m-%d')}"
        ], className="text-warning"))

    if date_info:
        card_body_content.append(html.Div(date_info, className="mt-2"))

    # View details button
    card_body_content.append(
        dbc.Button(
            "View Details",
            id={"type": "view-card-btn", "index": card_id},
            color="primary",
            size="sm",
            className="mt-3"
        )
    )

    card_body = dbc.CardBody(card_body_content)

    return dbc.Card([card_header, card_body], className="mb-3 shadow-sm")


def create_card_list(cards):
    """
    Create a list of card components.

    Args:
        cards: List of card dictionaries

    Returns:
        list: List of card components
    """
    if not cards:
        return [
            html.Div(
                dbc.Alert(
                    "No cards found matching your criteria.",
                    color="info",
                    className="text-center"
                ),
                className="mt-4"
            )
        ]

    return [create_card_component(card) for card in cards]


def create_pagination_controls(current_page, total_pages):
    """
    Create pagination controls (page number buttons only, prev/next exist in layout).

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages

    Returns:
        html.Div: Pagination component
    """
    if total_pages <= 1:
        return html.Div()

    # Page numbers to show
    pages_to_show = set()
    pages_to_show.add(1)
    pages_to_show.add(total_pages)
    pages_to_show.add(current_page)

    for i in range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)):
        pages_to_show.add(i)

    pages_list = sorted(pages_to_show)

    # Build page buttons
    page_buttons = []
    for i, page in enumerate(pages_list):
        # Add ellipsis if there's a gap
        if i > 0 and page > pages_list[i - 1] + 1:
            page_buttons.append(
                dbc.Button("...", size="sm", disabled=True, color="secondary", outline=True, className="me-1")
            )

        page_buttons.append(
            dbc.Button(
                str(page),
                id={"type": "page-btn", "index": page},
                size="sm",
                color="primary" if page == current_page else "secondary",
                outline=page != current_page,
                className="me-1"
            )
        )

    # Return only page number buttons (prev/next are in the base layout)
    return dbc.ButtonGroup(page_buttons, className="mx-2")


def create_stats_card(title, value, subtitle=None, color="primary", icon=None):
    """
    Create a statistics card.

    Args:
        title: Card title
        value: Main value to display
        subtitle: Optional subtitle
        color: Card color theme
        icon: Optional icon class name

    Returns:
        dbc.Card: Statistics card
    """
    card_content = []

    if icon:
        card_content.append(
            html.Div(
                html.I(className=f"{icon} fa-2x"),
                className="text-center mb-2"
            )
        )

    card_content.append(
        html.H6(title, className="text-muted text-uppercase mb-2")
    )

    card_content.append(
        html.H2(str(value), className="mb-0")
    )

    if subtitle:
        card_content.append(
            html.P(subtitle, className="text-muted small mb-0 mt-2")
        )

    return dbc.Card(
        dbc.CardBody(card_content, className="text-center"),
        className="shadow-sm",
        style={"border-left": f"4px solid var(--bs-{color})"}
    )


def create_card_detail_modal(card, labels=None, comments=None, checklists=None,
                             attachments=None, path_data=None):
    """
    Create a modal for displaying detailed card information.

    Args:
        card: Card dictionary
        labels: List of label dictionaries
        comments: List of comment dictionaries
        checklists: List of checklist dictionaries with items
        attachments: List of attachment dictionaries
        path_data: Card movement history

    Returns:
        dbc.Modal: Card detail modal
    """
    if not card:
        return dbc.Modal(
            dbc.ModalBody("Card not found"),
            id="card-detail-modal",
            size="lg"
        )

    card_name = card.get('name', 'Untitled')
    card_desc = card.get('desc', 'No description')
    card_list = card.get('list', 'Unknown')
    completed = card.get('completed', 0)
    create_date = card.get('create_date', '')
    end_date = card.get('end_date', '')
    due_date = card.get('due_date', '')

    # Modal header
    modal_header = dbc.ModalHeader([
        html.H4(card_name, className="mb-2"),
        html.Div([
            dbc.Badge(
                "Completed" if completed else "Pending",
                color="success" if completed else "secondary",
                className="me-2"
            ),
            dbc.Badge(card_list, color="primary", pill=True)
        ])
    ])

    # Modal body sections
    body_sections = []

    # Description section
    body_sections.append(
        html.Div([
            html.H5("Description", className="border-bottom pb-2 mb-3"),
            html.P(card_desc or "No description provided", className="text-muted")
        ], className="mb-4")
    )

    # Dates section
    dates_content = []
    if create_date:
        dates_content.append(
            html.Div([
                html.Strong("Created: "),
                html.Span(format_date(create_date, '%Y-%m-%d %H:%M'))
            ], className="mb-2")
        )
    if end_date:
        dates_content.append(
            html.Div([
                html.Strong("Completed: "),
                html.Span(format_date(end_date, '%Y-%m-%d %H:%M'))
            ], className="mb-2")
        )
    if due_date:
        dates_content.append(
            html.Div([
                html.Strong("Due Date: "),
                html.Span(format_date(due_date, '%Y-%m-%d'), className="text-warning")
            ], className="mb-2")
        )

    if dates_content:
        body_sections.append(
            html.Div([
                html.H5("Dates", className="border-bottom pb-2 mb-3"),
                html.Div(dates_content)
            ], className="mb-4")
        )

    # Labels section
    if labels:
        label_badges = [
            dbc.Badge(label.get('name', 'Unlabeled'), className="me-1 mb-1")
            for label in labels
        ]
        body_sections.append(
            html.Div([
                html.H5("Labels", className="border-bottom pb-2 mb-3"),
                html.Div(label_badges)
            ], className="mb-4")
        )

    # Comments section
    if comments:
        comment_items = [
            html.Div([
                html.Div([
                    html.Small(format_date_relative(comment.get('time', '')), className="text-muted")
                ], className="mb-1"),
                html.P(comment.get('text', ''), className="mb-2")
            ], className="border-left pl-3 mb-3")
            for comment in comments
        ]
        body_sections.append(
            html.Div([
                html.H5(f"Comments ({len(comments)})", className="border-bottom pb-2 mb-3"),
                html.Div(comment_items)
            ], className="mb-4")
        )

    # Checklists section
    if checklists:
        checklist_items = []
        for checklist in checklists:
            items = checklist.get('items', [])
            if items:
                item_list = [
                    html.Div([
                        html.I(
                            className="bi bi-check-square me-2" if item.get('checked')
                            else "bi bi-square me-2"
                        ),
                        html.Span(
                            item.get('name', ''),
                            className="text-decoration-line-through" if item.get('checked') else ""
                        )
                    ], className="mb-1")
                    for item in items
                ]
                checklist_items.append(
                    html.Div([
                        html.H6(checklist.get('name', 'Checklist'), className="mb-2"),
                        html.Div(item_list)
                    ], className="mb-3")
                )

        if checklist_items:
            body_sections.append(
                html.Div([
                    html.H5("Checklists", className="border-bottom pb-2 mb-3"),
                    html.Div(checklist_items)
                ], className="mb-4")
            )

    # Attachments section
    if attachments:
        attachment_links = [
            html.Div([
                html.A(
                    [html.I(className="bi bi-paperclip me-2"), att.get('name', 'Attachment')],
                    href=att.get('url', '#'),
                    target="_blank",
                    className="text-decoration-none"
                )
            ], className="mb-2")
            for att in attachments
        ]
        body_sections.append(
            html.Div([
                html.H5(f"Attachments ({len(attachments)})", className="border-bottom pb-2 mb-3"),
                html.Div(attachment_links)
            ], className="mb-4")
        )

    # Journey visualization
    if path_data:
        from components.state_diagram import create_journey_state_diagram
        journey_fig = create_journey_state_diagram(path_data, card_name)
        body_sections.append(
            html.Div([
                html.H5("Card Journey", className="border-bottom pb-2 mb-3"),
                dcc.Graph(figure=journey_fig, config={'displayModeBar': False})
            ], className="mb-4")
        )

    modal_body = dbc.ModalBody(body_sections)

    modal_footer = dbc.ModalFooter(
        dbc.Button("Close", id="close-card-modal", className="ms-auto")
    )

    return dbc.Modal(
        [modal_header, modal_body, modal_footer],
        id="card-detail-modal",
        size="xl",
        scrollable=True
    )
