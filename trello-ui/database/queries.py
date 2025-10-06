"""Database query functions for Trello Archive."""
from .connection import execute_query


def get_all_cards(limit=None, offset=0):
    """Get all cards with optional pagination."""
    query = """
        SELECT id, name, create_date, end_date, desc, due_date, completed, list
        FROM cards
        ORDER BY create_date DESC
    """
    if limit:
        query += f" LIMIT {limit} OFFSET {offset}"

    return execute_query(query)


def get_card_by_id(card_id):
    """Get a single card by ID."""
    query = """
        SELECT id, name, create_date, end_date, desc, due_date, completed, list
        FROM cards
        WHERE id = ?
    """
    results = execute_query(query, (card_id,))
    return results[0] if results else None


def search_cards(search_text=None, list_filter=None, completed_filter=None,
                 start_date=None, end_date=None, has_attachments=None,
                 has_comments=None, has_checklists=None, has_due_date=None,
                 label_filter=None, sort_by='create_date', sort_order='DESC',
                 limit=None, offset=0):
    """
    Search cards with various filters.

    Args:
        search_text: Text to search in card name and description
        list_filter: List name to filter by
        completed_filter: Boolean for completed status
        start_date: Filter cards created after this date
        end_date: Filter cards created before this date
        has_attachments: Filter cards with/without attachments
        has_comments: Filter cards with/without comments
        has_checklists: Filter cards with/without checklists
        has_due_date: Filter cards with/without due dates
        label_filter: Label name to filter by
        sort_by: Column to sort by
        sort_order: 'ASC' or 'DESC'
        limit: Max number of results
        offset: Offset for pagination

    Returns:
        list: Filtered cards
    """
    query = """
        SELECT DISTINCT c.id, c.name, c.create_date, c.end_date, c.desc, c.due_date, c.completed, c.list
        FROM cards c
    """

    joins = []
    conditions = []
    params = []

    # Add joins if needed
    if has_attachments is not None:
        joins.append("LEFT JOIN attachments a ON c.id = a.card_id")
    if has_comments is not None:
        joins.append("LEFT JOIN comments co ON c.id = co.card_id")
    if has_checklists is not None:
        joins.append("LEFT JOIN checklists ch ON c.id = ch.card_id")
    if label_filter:
        joins.append("LEFT JOIN labels l ON c.id = l.card_id")

    # Build WHERE conditions
    if search_text:
        conditions.append("(c.name LIKE ? OR c.desc LIKE ?)")
        search_pattern = f"%{search_text}%"
        params.extend([search_pattern, search_pattern])

    if list_filter:
        conditions.append("c.list = ?")
        params.append(list_filter)

    if completed_filter is not None:
        conditions.append("c.completed = ?")
        params.append(1 if completed_filter else 0)

    if start_date:
        conditions.append("c.create_date >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("c.create_date <= ?")
        params.append(end_date)

    if has_due_date is not None:
        if has_due_date:
            conditions.append("c.due_date IS NOT NULL")
        else:
            conditions.append("c.due_date IS NULL")

    if has_attachments is not None:
        if has_attachments:
            conditions.append("a.id IS NOT NULL")
        else:
            conditions.append("a.id IS NULL")

    if has_comments is not None:
        if has_comments:
            conditions.append("co.id IS NOT NULL")
        else:
            conditions.append("co.id IS NULL")

    if has_checklists is not None:
        if has_checklists:
            conditions.append("ch.id IS NOT NULL")
        else:
            conditions.append("ch.id IS NULL")

    if label_filter:
        conditions.append("l.name = ?")
        params.append(label_filter)

    # Construct full query
    if joins:
        query += " " + " ".join(joins)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Add sorting
    valid_sort_columns = ['create_date', 'end_date', 'name', 'list', 'completed']
    if sort_by in valid_sort_columns:
        query += f" ORDER BY c.{sort_by} {sort_order}"
    else:
        query += " ORDER BY c.create_date DESC"

    # Add pagination
    if limit:
        query += f" LIMIT {limit} OFFSET {offset}"

    return execute_query(query, tuple(params))


def count_cards(search_text=None, list_filter=None, completed_filter=None,
                start_date=None, end_date=None, has_attachments=None,
                has_comments=None, has_checklists=None, has_due_date=None,
                label_filter=None):
    """Count cards matching the given filters."""
    query = "SELECT COUNT(DISTINCT c.id) as count FROM cards c"

    joins = []
    conditions = []
    params = []

    # Same logic as search_cards for joins and conditions
    if has_attachments is not None:
        joins.append("LEFT JOIN attachments a ON c.id = a.card_id")
    if has_comments is not None:
        joins.append("LEFT JOIN comments co ON c.id = co.card_id")
    if has_checklists is not None:
        joins.append("LEFT JOIN checklists ch ON c.id = ch.card_id")
    if label_filter:
        joins.append("LEFT JOIN labels l ON c.id = l.card_id")

    if search_text:
        conditions.append("(c.name LIKE ? OR c.desc LIKE ?)")
        search_pattern = f"%{search_text}%"
        params.extend([search_pattern, search_pattern])

    if list_filter:
        conditions.append("c.list = ?")
        params.append(list_filter)

    if completed_filter is not None:
        conditions.append("c.completed = ?")
        params.append(1 if completed_filter else 0)

    if start_date:
        conditions.append("c.create_date >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("c.create_date <= ?")
        params.append(end_date)

    if has_due_date is not None:
        if has_due_date:
            conditions.append("c.due_date IS NOT NULL")
        else:
            conditions.append("c.due_date IS NULL")

    if has_attachments is not None:
        if has_attachments:
            conditions.append("a.id IS NOT NULL")
        else:
            conditions.append("a.id IS NULL")

    if has_comments is not None:
        if has_comments:
            conditions.append("co.id IS NOT NULL")
        else:
            conditions.append("co.id IS NULL")

    if has_checklists is not None:
        if has_checklists:
            conditions.append("ch.id IS NOT NULL")
        else:
            conditions.append("ch.id IS NULL")

    if label_filter:
        conditions.append("l.name = ?")
        params.append(label_filter)

    if joins:
        query += " " + " ".join(joins)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    results = execute_query(query, tuple(params))
    return results[0]['count'] if results else 0


def get_card_labels(card_id):
    """Get all labels for a specific card."""
    query = """
        SELECT id, name
        FROM labels
        WHERE card_id = ?
    """
    return execute_query(query, (card_id,))


def get_card_path(card_id):
    """Get the movement history for a card."""
    query = """
        SELECT id, from_list, to_list, time
        FROM path_taken
        WHERE card_id = ?
        ORDER BY time ASC
    """
    return execute_query(query, (card_id,))


def get_card_comments(card_id):
    """Get all comments for a specific card."""
    query = """
        SELECT id, text, time
        FROM comments
        WHERE card_id = ?
        ORDER BY time DESC
    """
    return execute_query(query, (card_id,))


def get_card_checklists(card_id):
    """Get all checklists for a specific card."""
    query = """
        SELECT id, name
        FROM checklists
        WHERE card_id = ?
    """
    return execute_query(query, (card_id,))


def get_checklist_items(checklist_id):
    """Get all items for a specific checklist."""
    query = """
        SELECT id, name, checked
        FROM checklist_items
        WHERE checklist_id = ?
    """
    return execute_query(query, (checklist_id,))


def get_card_attachments(card_id):
    """Get all attachments for a specific card."""
    query = """
        SELECT id, name, url
        FROM attachments
        WHERE card_id = ?
    """
    return execute_query(query, (card_id,))


def get_all_lists():
    """Get all unique list names."""
    query = """
        SELECT DISTINCT list
        FROM cards
        ORDER BY list
    """
    return execute_query(query)


def get_all_labels():
    """Get all unique label names."""
    query = """
        SELECT DISTINCT name
        FROM labels
        WHERE name IS NOT NULL
        ORDER BY name
    """
    return execute_query(query)


def get_completion_stats():
    """Get overall completion statistics."""
    query = """
        SELECT
            COUNT(*) as total_cards,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_cards,
            COUNT(DISTINCT list) as total_lists
        FROM cards
    """
    results = execute_query(query)
    return results[0] if results else {}


def get_cards_by_list():
    """Get card counts grouped by list."""
    query = """
        SELECT
            list,
            COUNT(*) as card_count,
            SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_count
        FROM cards
        GROUP BY list
        ORDER BY card_count DESC
    """
    return execute_query(query)


def get_completion_over_time(interval='month'):
    """
    Get card completion counts over time (based on movement to 'Done' list).

    Args:
        interval: 'day', 'week', 'month', or 'year'

    Returns:
        list: Completion data grouped by time interval
    """
    # Date format in DB is MM:DD:YY HH:MM
    # Completion is defined as when card moved to 'Done' list

    if interval == 'month':
        query = """
            SELECT
                '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) as period,
                COUNT(DISTINCT card_id) as count
            FROM path_taken
            WHERE to_list = 'Done' AND time IS NOT NULL
            GROUP BY period
            ORDER BY period
        """
    elif interval == 'year':
        query = """
            SELECT
                '20' || substr(time, 7, 2) as period,
                COUNT(DISTINCT card_id) as count
            FROM path_taken
            WHERE to_list = 'Done' AND time IS NOT NULL
            GROUP BY period
            ORDER BY period
        """
    elif interval == 'day':
        query = """
            SELECT
                '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) as period,
                COUNT(DISTINCT card_id) as count
            FROM path_taken
            WHERE to_list = 'Done' AND time IS NOT NULL
            GROUP BY period
            ORDER BY period
        """
    else:  # Default to month
        query = """
            SELECT
                '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) as period,
                COUNT(DISTINCT card_id) as count
            FROM path_taken
            WHERE to_list = 'Done' AND time IS NOT NULL
            GROUP BY period
            ORDER BY period
        """

    return execute_query(query)


def get_card_flow_data(start_date=None, end_date=None):
    """
    Get data for Sankey diagram showing card movement between lists.

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        list: Card flow data
    """
    query = """
        SELECT
            from_list as source,
            to_list as target,
            COUNT(*) as value
        FROM path_taken
        WHERE 1=1
    """

    params = []
    if start_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) <= ?"
        params.append(end_date)

    query += """
        GROUP BY from_list, to_list
        HAVING COUNT(*) > 0
        ORDER BY value DESC
    """

    return execute_query(query, tuple(params) if params else ())


def get_card_complexity_stats():
    """Get statistics about card complexity (attachments, comments, checklists)."""
    query = """
        SELECT
            c.id,
            c.name,
            COUNT(DISTINCT a.id) as attachment_count,
            COUNT(DISTINCT co.id) as comment_count,
            COUNT(DISTINCT ch.id) as checklist_count
        FROM cards c
        LEFT JOIN attachments a ON c.id = a.card_id
        LEFT JOIN comments co ON c.id = co.card_id
        LEFT JOIN checklists ch ON c.id = ch.card_id
        GROUP BY c.id, c.name
    """
    return execute_query(query)


def get_completion_by_day_of_week(start_date=None, end_date=None):
    """
    Get card completion counts by day of week (based on movement to 'Done' list).

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        list: Completion counts for each day of week (0=Sunday, 6=Saturday)
    """
    query = """
        SELECT
            CASE CAST(strftime('%w', '20' || substr(time, 7, 2) || '-' ||
                     substr(time, 1, 2) || '-' || substr(time, 4, 2)) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END as day_name,
            CAST(strftime('%w', '20' || substr(time, 7, 2) || '-' ||
                 substr(time, 1, 2) || '-' || substr(time, 4, 2)) AS INTEGER) as day_number,
            COUNT(DISTINCT card_id) as count
        FROM path_taken
        WHERE to_list = 'Done' AND time IS NOT NULL
    """

    params = []
    if start_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) <= ?"
        params.append(end_date)

    query += """
        GROUP BY day_number
        ORDER BY day_number
    """

    return execute_query(query, tuple(params) if params else ())


def get_completion_by_time_of_day(start_date=None, end_date=None):
    """
    Get card completion counts by hour of day (based on movement to 'Done' list).

    Args:
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)

    Returns:
        list: Completion counts for each hour (0-23)
    """
    query = """
        SELECT
            CAST(substr(time, 10, 2) AS INTEGER) as hour,
            COUNT(DISTINCT card_id) as count
        FROM path_taken
        WHERE to_list = 'Done' AND time IS NOT NULL
    """

    params = []
    if start_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) >= ?"
        params.append(start_date)
    if end_date:
        query += " AND '20' || substr(time, 7, 2) || '-' || substr(time, 1, 2) || '-' || substr(time, 4, 2) <= ?"
        params.append(end_date)

    query += """
        GROUP BY hour
        ORDER BY hour
    """

    return execute_query(query, tuple(params) if params else ())
