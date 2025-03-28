# Trello Archiver
Archives Trello Cards. I initially made this to backup my own Trello cards, and the code has had many updates over the years. I'm porting it to Docker now and making it usable by others.

To use it in it's current state set up a `docker-compose.yml` that looks something like the following

```yaml
services:
  trello-archiver:
    build: https://github.com/swag31415/Trello-Archiver.git
    container_name: trello_archiver
    volumes:
      - ./data:/data
    environment:
      - SQLITE_DATABASE_PATH=/data/trello_archive.db
      - ATTACHMENTS_PATH=/data
      - TRELLO_API_KEY=***
      - TRELLO_API_SECRET=***
      - TRELLO_API_TOKEN=***
      - BOARD_ID=***
      - LIST_ID=***
      - REMOVE_CARDS_UPON_COMPLETION=FALSE
```

Fill in the keys and ids with your own values and then run `docker compose up`