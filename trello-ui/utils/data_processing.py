"""Data processing utilities for Trello Archive UI."""
import pandas as pd
from datetime import datetime


def process_completion_data(completion_data):
    """
    Process completion data for time series charts.

    Args:
        completion_data: Raw completion data from database

    Returns:
        pd.DataFrame: Processed DataFrame with dates and counts
    """
    if not completion_data:
        return pd.DataFrame(columns=['period', 'count'])

    df = pd.DataFrame(completion_data)
    return df


def process_list_stats(list_data):
    """
    Process list statistics data.

    Args:
        list_data: Raw list data from database

    Returns:
        pd.DataFrame: Processed DataFrame with list stats
    """
    if not list_data:
        return pd.DataFrame(columns=['list', 'card_count', 'completed_count'])

    df = pd.DataFrame(list_data)

    # Calculate completion rate
    df['completion_rate'] = (df['completed_count'] / df['card_count'] * 100).round(1)

    return df


def process_sankey_data(flow_data):
    """
    Process card flow data for Sankey diagram.

    Args:
        flow_data: Raw flow data from database

    Returns:
        dict: Processed data with source, target, value, and node labels
    """
    if not flow_data:
        return {
            'source': [],
            'target': [],
            'value': [],
            'labels': []
        }

    df = pd.DataFrame(flow_data)

    # Get unique nodes (all source and target lists)
    all_nodes = list(set(df['source'].tolist() + df['target'].tolist()))
    node_dict = {node: idx for idx, node in enumerate(all_nodes)}

    # Map source and target to indices
    source_indices = [node_dict[source] for source in df['source']]
    target_indices = [node_dict[target] for target in df['target']]
    values = df['value'].tolist()

    return {
        'source': source_indices,
        'target': target_indices,
        'value': values,
        'labels': all_nodes
    }


def process_complexity_data(complexity_data):
    """
    Process card complexity data.

    Args:
        complexity_data: Raw complexity data from database

    Returns:
        pd.DataFrame: Processed DataFrame with complexity metrics
    """
    if not complexity_data:
        return pd.DataFrame(columns=['name', 'complexity_score'])

    df = pd.DataFrame(complexity_data)

    # Calculate complexity score (weighted sum of attachments, comments, checklists)
    df['complexity_score'] = (
        df['attachment_count'] * 1 +
        df['comment_count'] * 2 +
        df['checklist_count'] * 3
    )

    # Sort by complexity score
    df = df.sort_values('complexity_score', ascending=False)

    return df


def aggregate_cards_by_date(cards, date_field='create_date', interval='day'):
    """
    Aggregate cards by date interval.

    Args:
        cards: List of card dictionaries
        date_field: Date field to aggregate by
        interval: 'day', 'week', 'month', or 'year'

    Returns:
        pd.DataFrame: Aggregated data
    """
    if not cards:
        return pd.DataFrame(columns=['period', 'count'])

    df = pd.DataFrame(cards)

    # Parse dates
    try:
        df[date_field] = pd.to_datetime(df[date_field])
    except Exception:
        return pd.DataFrame(columns=['period', 'count'])

    # Group by interval
    if interval == 'day':
        df['period'] = df[date_field].dt.strftime('%Y-%m-%d')
    elif interval == 'week':
        df['period'] = df[date_field].dt.strftime('%Y-W%W')
    elif interval == 'month':
        df['period'] = df[date_field].dt.strftime('%Y-%m')
    elif interval == 'year':
        df['period'] = df[date_field].dt.strftime('%Y')
    else:
        df['period'] = df[date_field].dt.strftime('%Y-%m')

    # Count cards per period
    result = df.groupby('period').size().reset_index(name='count')

    return result


def calculate_cycle_time(cards):
    """
    Calculate average cycle time (time from creation to completion).

    Args:
        cards: List of completed card dictionaries

    Returns:
        float: Average cycle time in days
    """
    if not cards:
        return 0.0

    df = pd.DataFrame(cards)

    # Filter completed cards
    df = df[df['completed'] == 1]

    if df.empty:
        return 0.0

    try:
        df['create_date'] = pd.to_datetime(df['create_date'])
        df['end_date'] = pd.to_datetime(df['end_date'])

        # Calculate cycle time in days
        df['cycle_time'] = (df['end_date'] - df['create_date']).dt.total_seconds() / 86400

        # Return average
        return round(df['cycle_time'].mean(), 1)
    except Exception:
        return 0.0


def get_top_cards_by_metric(complexity_data, metric='complexity_score', top_n=10):
    """
    Get top N cards by a specific metric.

    Args:
        complexity_data: DataFrame with complexity data
        metric: Metric to sort by
        top_n: Number of top cards to return

    Returns:
        pd.DataFrame: Top N cards
    """
    if complexity_data.empty:
        return pd.DataFrame()

    return complexity_data.nlargest(top_n, metric)


def calculate_label_distribution(cards_with_labels):
    """
    Calculate distribution of labels across cards.

    Args:
        cards_with_labels: List of (card, labels) tuples

    Returns:
        dict: Label name to count mapping
    """
    label_counts = {}

    for card, labels in cards_with_labels:
        for label in labels:
            label_name = label.get('name', 'Unlabeled')
            label_counts[label_name] = label_counts.get(label_name, 0) + 1

    return label_counts


def filter_date_range(cards, start_date=None, end_date=None, date_field='create_date'):
    """
    Filter cards by date range.

    Args:
        cards: List of card dictionaries
        start_date: Start date string
        end_date: End date string
        date_field: Date field to filter by

    Returns:
        list: Filtered cards
    """
    if not cards:
        return []

    df = pd.DataFrame(cards)

    try:
        df[date_field] = pd.to_datetime(df[date_field])

        if start_date:
            start = pd.to_datetime(start_date)
            df = df[df[date_field] >= start]

        if end_date:
            end = pd.to_datetime(end_date)
            df = df[df[date_field] <= end]

        return df.to_dict('records')
    except Exception:
        return cards
