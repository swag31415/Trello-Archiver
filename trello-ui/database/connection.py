"""Database connection management for Trello Archive."""
import sqlite3
import os
from pathlib import Path

# Database path - use environment variable or default to /data/trello_archive.db for Docker
DATABASE_PATH = os.getenv('SQLITE_DATABASE_PATH', '/data/trello_archive.db')


def get_connection():
    """
    Create and return a database connection.

    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    return conn


def execute_query(query, params=None):
    """
    Execute a query and return results.

    Args:
        query (str): SQL query to execute
        params (tuple, optional): Query parameters

    Returns:
        list: List of row dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    # Convert rows to dictionaries
    columns = [description[0] for description in cursor.description] if cursor.description else []
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conn.close()
    return results


def execute_update(query, params=None):
    """
    Execute an update/insert/delete query.

    Args:
        query (str): SQL query to execute
        params (tuple, optional): Query parameters

    Returns:
        int: Number of affected rows
    """
    conn = get_connection()
    cursor = conn.cursor()

    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    conn.commit()
    affected = cursor.rowcount
    conn.close()

    return affected
