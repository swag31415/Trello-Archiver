#!/bin/bash

# Run the archiver first
echo "Running Trello archiver..."
python /app/archiver.py

# Start the web UI
echo "Starting Trello UI web server..."
python /app/trello-ui/app.py
