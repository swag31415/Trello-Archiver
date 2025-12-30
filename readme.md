# Trello Archiver

A comprehensive Trello archiving and analytics solution that automatically backs up your Trello cards and provides a powerful web-based interface for exploring and analyzing your archived data.

## Overview

This project consists of two integrated components:

1. **Archiver**: Automatically archives Trello cards from a specified board/list to a SQLite database
2. **Web UI**: Interactive dashboard and search interface for exploring archived data with advanced analytics

## Features

### 📥 Archiver
- Automated backup of Trello cards
- Complete data preservation including:
  - Card details (name, description, dates, labels)
  - Comments and discussions
  - Checklists and checklist items
  - Attachments and files
  - Card movement history (path taken between lists)
- Optional card removal from Trello upon archival
- Environment-based configuration

### 📊 Web UI Dashboard
- **Overview Metrics**: Total cards, completion rates, active lists
- **Completion Trends**: Historical view of card completion over time
- **List Statistics**: Card distribution and performance by list
- **Flow Analysis**: Sankey diagrams showing card movement between lists
- **Complexity Metrics**: Analysis of card complexity based on attachments, comments, and checklists

### 🔍 Advanced Search
- **Full-text search** across card names and descriptions
- **Date range filtering** for creation and completion dates
- **List and label filtering** with multi-select support
- **Content-based filters**: Cards with attachments, checklists, due dates, etc.
- **Completion status filtering**: Focus on completed vs. pending cards
- **Sorting and pagination**: Organize results your way

### 📇 Card Details
- Complete card information with descriptions
- Labels and metadata
- Comments timeline
- Checklists with completion status
- Attachments list
- Movement history (journey visualization)

## Quick Start with uv

### Prerequisites
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Trello API credentials (API key, secret, and token)
- Your Trello Board ID and List ID for archiving

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/swag31415/Trello-Archiver.git
   cd Trello-Archiver
   ```

2. **Configure your credentials** in `archive.sh`:
   - Update the Trello API credentials (`TRELLO_API_KEY`, `TRELLO_API_SECRET`, `TRELLO_API_TOKEN`)
   - Set your board and list IDs (`BOARD_ID`, `LIST_ID`)
   - Adjust `REMOVE_CARDS_UPON_COMPLETION` as needed

3. **Run the archiver**:
   ```bash
   ./archive.sh
   ```

   This will:
   - Archive cards from your specified Trello list (30+ days old)
   - Download all attachments to `./data/attach [date]`
   - Launch the web UI at `http://localhost:8050`

That's it! uv handles all dependency installation automatically.

## Manual Development

### Running Components Separately

If you want to run the archiver or UI separately:

1. **Set up environment variables**:
   ```bash
   export SQLITE_DATABASE_PATH=./data/trello_archive.db
   export ATTACHMENTS_PATH=./data
   export TRELLO_API_KEY=your_key
   export TRELLO_API_SECRET=your_secret
   export TRELLO_API_TOKEN=your_token
   export BOARD_ID=your_board_id
   export LIST_ID=your_list_id
   export REMOVE_CARDS_UPON_COMPLETION=FALSE
   ```

2. **Run the archiver only**:
   ```bash
   uv run archiver.py
   ```

3. **Run the web UI only**:
   ```bash
   cd trello-ui
   uv run app.py
   ```

4. **Access the interface**: `http://127.0.0.1:8050`

## Project Structure

```
Trello-Archiver/
├── archiver.py            # Main archiving script
├── pyproject.toml         # uv project configuration
├── README.md              # This file
│
└── trello-ui/             # Web interface
    ├── app.py             # Main application entry point
    ├── assets/            # Static assets (CSS, images)
    ├── components/        # Reusable UI components
    │   ├── charts.py      # Chart creation functions
    │   ├── sankey.py      # Sankey diagram components
    │   ├── cards.py       # Card display components
    │   └── search.py      # Search and filter components
    ├── database/          # Database layer
    │   ├── connection.py  # Database connection management
    │   └── queries.py     # SQL query functions
    ├── pages/             # Page layouts
    │   ├── dashboard.py   # Analytics dashboard
    │   └── search_page.py # Search interface
    └── utils/             # Utility functions
```

## Database Schema

The SQLite database includes the following tables:

- **cards**: Main card information (id, name, description, dates, completion status, list)
- **labels**: Card labels and categorization
- **path_taken**: Card movement history between lists
- **comments**: Card comments and discussions
- **checklists**: Checklist information
- **checklist_items**: Individual checklist items
- **attachments**: File attachments and links

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SQLITE_DATABASE_PATH` | Path to SQLite database | `trello_archive.db` |
| `ATTACHMENTS_PATH` | Path to store attachments | Current directory |
| `TRELLO_API_KEY` | Your Trello API key | Required |
| `TRELLO_API_SECRET` | Your Trello API secret | Required |
| `TRELLO_API_TOKEN` | Your Trello API token | Required |
| `BOARD_ID` | Trello board to archive from | Required |
| `LIST_ID` | Trello list to archive from | Required |
| `REMOVE_CARDS_UPON_COMPLETION` | Remove cards after archiving | `FALSE` |

### Getting Trello Credentials

1. **API Key and Secret**: Visit [Trello's API key page](https://trello.com/app-key)
2. **API Token**: Generate from the same page
3. **Board ID**: Get from your board's URL or API
4. **List ID**: Get from the Trello API

## Customization

### Web UI Customization

**Database Path**: Edit `trello-ui/database/connection.py`:
```python
DATABASE_PATH = os.getenv('SQLITE_DATABASE_PATH', '/data/trello_archive.db')
```

**Chart Settings**: Modify `trello-ui/components/charts.py` for:
- Colors, sizes, and themes
- Number of items displayed
- Chart types and layouts

**Styling**: Add custom CSS to `trello-ui/assets/styles.css`

**Filters**: Add new filter options by:
1. Adding UI component in `components/search.py`
2. Updating query in `database/queries.py`
3. Connecting in page callbacks

## Troubleshooting

### Database Connection
- Verify the database file path is correct
- Check file permissions
- Ensure schema matches expected structure

### API Errors
- Verify Trello credentials are correct
- Check API rate limits
- Ensure board/list IDs are valid

### Web UI Issues
- Check browser console for errors
- Verify database is populated with data
- Ensure port 8050 is available

## Technologies Used

- **Python**: Core application language
- **uv**: Fast Python package manager
- **Dash**: Web framework for analytical applications
- **Plotly**: Interactive charting and visualization
- **Dash Bootstrap Components**: UI components
- **Pandas**: Data manipulation and analysis
- **SQLite**: Local database
- **py-trello**: Trello API client

## License

This project is provided as-is for personal and educational use. Please ensure compliance with Trello's Terms of Service and any relevant data privacy policies.

## Contributing

Contributions are welcome! Key areas for enhancement:
- Additional visualization types
- Advanced filtering options
- Export functionality
- Performance optimizations
- Mobile interface improvements

---

**Built with ❤️ for comprehensive Trello archiving and analysis**
