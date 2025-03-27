# Trello Archiver
Archives Trello Cards. I initially made this to backup my own Trello cards, and the code has had many updates over the years. I'm porting it to Docker now and making it usable by others.

To use it in it's current state set up a `docker-compose.yml` that looks something like the following

```yaml
services:
  trello-archiver:
    build: ./trello_archiver
    container_name: trello_archiver
    volumes:
      - ./data:/data  # Mounts local 'data' directory for database & keys.json
    environment:
      - SQLITE_DATABASE_PATH=/data/trello_archive.db
      - KEYS_FILE_PATH=/data/keys.json
```

I know it's rough around the edges now and will likely not work for your setup. I'm improving it day by day.