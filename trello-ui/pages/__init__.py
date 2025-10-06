"""Pages package for Trello Archive UI."""
from .dashboard import create_dashboard_layout
from .search_page import create_search_page_layout

__all__ = [
    'create_dashboard_layout',
    'create_search_page_layout',
]
