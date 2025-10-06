"""Helper functions for Trello Archive UI."""
from datetime import datetime
import re


def format_date(date_str, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Format a date string to a more readable format.

    Args:
        date_str: Date string to format
        format_str: Output format string

    Returns:
        str: Formatted date string or empty string if invalid
    """
    if not date_str:
        return ""

    try:
        # Try parsing common date formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(format_str)
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def format_date_relative(date_str):
    """
    Format a date as a relative time (e.g., '2 days ago').

    Args:
        date_str: Date string to format

    Returns:
        str: Relative time string
    """
    if not date_str:
        return ""

    try:
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
            try:
                dt = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            return date_str

        now = datetime.now()
        delta = now - dt

        if delta.days == 0:
            if delta.seconds < 60:
                return "just now"
            elif delta.seconds < 3600:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.days == 1:
            return "yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif delta.days < 365:
            months = delta.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = delta.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"

    except Exception:
        return date_str


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def sanitize_html(text):
    """
    Remove or escape HTML tags from text.

    Args:
        text: Text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    # Remove HTML tags
    clean = re.sub(r'<[^>]+>', '', text)
    return clean


def calculate_completion_rate(completed, total):
    """
    Calculate completion rate as a percentage.

    Args:
        completed: Number of completed items
        total: Total number of items

    Returns:
        float: Completion rate (0-100)
    """
    if total == 0:
        return 0.0

    return round((completed / total) * 100, 1)


def parse_markdown_links(text):
    """
    Extract URLs from markdown-style links.

    Args:
        text: Text containing markdown links

    Returns:
        list: List of (link_text, url) tuples
    """
    if not text:
        return []

    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, text)
    return matches


def get_color_for_value(value, min_val, max_val, color_scale='RdYlGn'):
    """
    Get a color for a value based on a range.

    Args:
        value: Value to get color for
        min_val: Minimum value in range
        max_val: Maximum value in range
        color_scale: Plotly color scale name

    Returns:
        str: Color hex code
    """
    if max_val == min_val:
        return '#808080'  # Gray for single value

    # Normalize value to 0-1 range
    normalized = (value - min_val) / (max_val - min_val)

    # Simple color interpolation (green to red)
    if color_scale == 'RdYlGn':
        if normalized < 0.5:
            # Green to yellow
            r = int(normalized * 2 * 255)
            g = 255
        else:
            # Yellow to red
            r = 255
            g = int((1 - normalized) * 2 * 255)
        b = 0
        return f'#{r:02x}{g:02x}{b:02x}'

    return '#808080'


def sort_cards(cards, sort_by='create_date', sort_order='desc'):
    """
    Sort a list of cards.

    Args:
        cards: List of card dictionaries
        sort_by: Field to sort by
        sort_order: 'asc' or 'desc'

    Returns:
        list: Sorted cards
    """
    reverse = sort_order.lower() == 'desc'

    try:
        sorted_cards = sorted(cards, key=lambda x: x.get(sort_by, ''), reverse=reverse)
        return sorted_cards
    except Exception:
        return cards


def paginate_items(items, page=1, per_page=20):
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Current page number (1-indexed)
        per_page: Items per page

    Returns:
        tuple: (paginated_items, total_pages)
    """
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    return items[start_idx:end_idx], total_pages
