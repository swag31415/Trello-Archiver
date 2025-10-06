# Trello Archive UI

A comprehensive web-based interface for exploring and analyzing archived Trello data. This application provides powerful search, filtering, and analytics capabilities to help you understand your Trello card history, workflow patterns, and productivity metrics.

## Features

### 📊 **Dashboard**
- **Overview Metrics**: Total cards, completion rates, active lists
- **Completion Trends**: Historical view of card completion over time
- **List Statistics**: Card distribution and performance by list
- **Flow Analysis**: Sankey diagrams showing card movement between lists
- **Complexity Metrics**: Analysis of card complexity based on attachments, comments, and checklists

### 🔍 **Advanced Search**
- **Full-text search** across card names and descriptions
- **Date range filtering** for creation and completion dates
- **List and label filtering** with multi-select support
- **Content-based filters**: Cards with attachments, checklists, due dates, etc.
- **Completion status filtering**: Focus on completed vs. pending cards
- **Sorting and pagination**: Organize results your way

### 📇 **Card Details**
- Complete card information with descriptions
- Labels and metadata
- Comments timeline
- Checklists with completion status
- Attachments list
- Movement history (journey visualization)

## Installation

### Prerequisites
- Python 3.8 or higher
- SQLite database with Trello archive data (`trello_archive.db`)

### Setup

1. **Navigate to the project directory**:
   ```bash
   cd trello-ui
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify database location**:
   The application expects `trello_archive.db` to be in the parent directory (`../trello_archive.db`). If your database is elsewhere, update the path in `database/connection.py`.

## Running the Application

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Access the interface**:
   Open your browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

3. **Navigate the application**:
   - **Dashboard** (`/`): View analytics and overview
   - **Search** (`/search`): Search and filter cards

## Project Structure

```
trello-ui/
├── app.py                 # Main application entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── assets/               # Static assets
│   └── styles.css        # Custom CSS styling
│
├── components/           # Reusable UI components
│   ├── __init__.py
│   ├── charts.py         # Chart creation functions
│   ├── sankey.py         # Sankey diagram components
│   ├── cards.py          # Card display components
│   └── search.py         # Search and filter components
│
├── database/             # Database layer
│   ├── __init__.py
│   ├── connection.py     # Database connection management
│   └── queries.py        # SQL query functions
│
├── pages/                # Page layouts
│   ├── __init__.py
│   ├── dashboard.py      # Analytics dashboard
│   └── search_page.py    # Search interface
│
└── utils/                # Utility functions
    ├── __init__.py
    ├── helpers.py        # General helper functions
    └── data_processing.py # Data transformation utilities
```

## Database Schema

The application works with the following database structure:

- **cards**: Main card information (id, name, description, dates, completion status, list)
- **labels**: Card labels and categorization
- **path_taken**: Card movement history between lists
- **comments**: Card comments and discussions
- **checklists**: Checklist information
- **checklist_items**: Individual checklist items
- **attachments**: File attachments and links

## Customization

### Changing the Database Path
Edit `database/connection.py` and update the `DATABASE_PATH` variable:
```python
DATABASE_PATH = Path("/your/custom/path/to/trello_archive.db")
```

### Modifying Chart Settings
Chart configurations can be adjusted in `components/charts.py`:
- Colors, sizes, and themes
- Number of items displayed
- Chart types and layouts

### Adding Custom Filters
To add new filter options:
1. Add filter UI component in `components/search.py`
2. Update search query in `database/queries.py`
3. Connect filter in `app.py` callbacks

### Styling Changes
Custom CSS can be added to `assets/styles.css`:
- Bootstrap theme variables
- Component-specific styles
- Responsive design adjustments

## Performance Tips

- **Large datasets**: For databases with many thousands of cards, consider:
  - Reducing the default number of items per page
  - Adding database indexes for frequently queried columns
  - Implementing server-side caching

- **Chart rendering**: Complex charts may take a moment to render. The application includes loading states for better UX.

## Troubleshooting

### Database Connection Errors
- Verify the database file exists at the specified path
- Check file permissions
- Ensure the database schema matches the expected structure

### Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure you're using Python 3.8 or higher
- Check that the virtual environment is activated

### Port Already in Use
If port 8050 is already in use, change it in `app.py`:
```python
app.run_server(debug=True, host='127.0.0.1', port=8051)
```

## Technologies Used

- **Dash**: Python web framework for analytical applications
- **Plotly**: Interactive charting and visualization library
- **Dash Bootstrap Components**: Modern UI components with Bootstrap styling
- **Pandas**: Data manipulation and analysis
- **SQLite**: Local database for storing archived data

## License

This project is provided as-is for personal and educational use.

## Support

For issues and questions:
1. Check the browser console for JavaScript errors
2. Review the Python console output for backend errors
3. Verify database schema compatibility
4. Ensure all dependencies are correctly installed

---

**Built with ❤️ for exploring Trello archives**
