# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the archiver script
COPY archiver.py /app/

# Copy the trello-ui directory
COPY trello-ui /app/trello-ui

# Expose port for web UI
EXPOSE 8050

# Copy startup script
COPY startup.sh /app/
RUN chmod +x /app/startup.sh

# Run the startup script
CMD ["/app/startup.sh"]
