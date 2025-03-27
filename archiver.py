import sqlite3, os
from datetime import datetime, timedelta
from urllib import parse
import requests
from trello import TrelloClient
import unicodedata
import re

class Query:
    def __init__(self, db_name=""):
        self.db_name = db_name
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        if exc_type is not None:
            print(f"An error occurred: {exc_val}")
            self.conn.rollback()
        self.conn.close()

SQLITE_DATABASE_PATH = os.getenv('SQLITE_DATABASE_PATH', 'trello_archive.db')
SQLITE_DATABASE_INIT_SCRIPT = '''
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    create_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    desc TEXT,
    due_date TEXT,
    completed BOOLEAN,
    list TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS labels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    name TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS path_taken (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    from_list TEXT NOT NULL,
    to_list TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    time TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS checklists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS checklist_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checklist_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    checked BOOLEAN NOT NULL,
    FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
);
'''
with Query(SQLITE_DATABASE_PATH) as (con, cur):
    cur.executescript(SQLITE_DATABASE_INIT_SCRIPT)

def backup_to_sqlite(card, cur):
    cur.execute("""
        INSERT INTO cards (name, create_date, end_date, desc, due_date, completed, list)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        card['name'],
        card['create_date'],
        card['end_date'],
        card['desc'] if card['desc'] != '' else None,
        card['due_date'],
        card['completed'],
        card['list']
    ))
    card_id = cur.lastrowid
    # Insert labels
    for label in card['labels']:
        cur.execute("INSERT INTO labels (card_id, name) VALUES (?, ?)", (card_id, label))
    # Insert path taken
    for path in card['path_taken']:
        cur.execute("""
            INSERT INTO path_taken (card_id, from_list, to_list, time)
            VALUES (?, ?, ?, ?)
        """, (card_id, path['from'], path['to'], path['time']))
    # Insert comments
    for comment in card['comments']:
        cur.execute("""
            INSERT INTO comments (card_id, text, time)
            VALUES (?, ?, ?)
        """, (card_id, comment['text'], comment['time']))
    # Insert checklists and checklist items
    for checklist in card['checklists']:
        cur.execute("INSERT INTO checklists (card_id, name) VALUES (?, ?)", (card_id, checklist['name']))
        checklist_id = cur.lastrowid
        for item in checklist['items']:
            cur.execute("""
                INSERT INTO checklist_items (checklist_id, name, checked)
                VALUES (?, ?, ?)
            """, (checklist_id, item['name'], item['checked']))
    # Insert attachments
    for attachment in card['attachments']:
        cur.execute("""
            INSERT INTO attachments (card_id, name, url)
            VALUES (?, ?, ?)
        """, (card_id, attachment['name'], attachment['url']))

def fdate(date):
  """Formats the date"""
  try:
    return date.strftime('%m:%d:%y %H:%M')
  except AttributeError:
    # Handle the case when the 'date' object doesn't have a
    # 'strftime' method or is not a valid date object.
    return None


def or_none(val, cond_for_none):
  """just a shorthand"""
  return None if cond_for_none else val


def card_to_dict(_card):
  """Turns a trello card with all it's properties into a useful dictionary"""
  return {
    'name': _card.name,
    'labels': [or_none(lab.name, lab.name == '') for lab in _card.labels],
    'create_date': fdate(_card.card_created_date),
    'end_date': fdate(_card.date_last_activity),
    'desc': _card.description,
    'due_date': or_none(fdate(_card.due_date), _card.due_date == ''),
    'completed': or_none(_card.is_due_complete, _card.due_date == ''),
    'path_taken': [{
      'from': move['source']['name'],
      'to': move['destination']['name'],
      'time': fdate(move['datetime'])
    } for move in _card.list_movements()],
    'list': _card.get_list().name,
    'comments': [{
      'text': comm['data']['text'],
      'time': fdate(comm['date'])
    } for comm in _card.comments],
    'checklists': [{
      'name': check.name,
      'items': [{
        'name': item['name'],
        'checked': item['checked']
      } for item in check.items]
    } for check in _card.checklists],
    'attachments': [{
      'name': parse.unquote(attach['name']),
      'url': attach['url']
    } for attach in _card.attachments]
  }

def slugify(value, allow_unicode=False):
  """
  Taken from https://github.com/django/django/blob/master/django/utils/text.py
  Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
  dashes to single dashes. Remove characters that aren't alphanumerics,
  underscores, or hyphens. Convert to lowercase. Also strip leading and
  trailing whitespace, dashes, and underscores.
  """
  value = str(value)
  if allow_unicode:
    value = unicodedata.normalize('NFKC', value)
  else:
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  value = re.sub(r'[^\w\s-]', '', value.lower())
  return re.sub(r'[-\s]+', '-', value).strip('-_')

def download(url, save_path, filename):
  """downloads a file from a url"""
  slug = slugify(filename)
  route = f'{save_path}/{slug}'
  # Handle duplicates
  dupes = 1
  while os.path.exists(route):
    route = f'{save_path}/d{dupes}_{slug}'
    dupes += 1
  # Download and save the file
  with open(route, 'wb') as file:
    resp = requests.get(url, allow_redirects=True, timeout=10)
    file.write(resp.content)

# This is so funny
NOW = datetime.now()

# Load the client
client = TrelloClient(
    api_key=os.getenv('TRELLO_API_KEY'),
    api_secret=os.getenv('TRELLO_API_SECRET'),
    token=os.getenv('TRELLO_API_TOKEN')
)
# Get the cards to archive
Board = client.get_board(os.getenv('BOARD_ID'))
Board_List = Board.get_list(os.getenv('LIST_ID'))
cards = [c for c in Board_List.list_cards_iter() if
            c.latestCardMove_date is None or
            c.latestCardMove_date.replace(tzinfo=None) < NOW - timedelta(days=30)
        ]

# Archive!
arch = [card_to_dict(c) for c in cards]
with Query(SQLITE_DATABASE_PATH) as (con, cur):
    for card in arch:
        backup_to_sqlite(card, cur)

# The attachments
ATTACHMENT_DIR = NOW.strftime('attach %-m-%-d-%y')
if not os.path.isdir(ATTACHMENT_DIR):
    os.mkdir(ATTACHMENT_DIR)
ATTACH_COUNT = 0
for card in arch:
    for attach in card['attachments']:
        download(attach['url'], ATTACHMENT_DIR, attach['name'])
        ATTACH_COUNT += 1

# Report!
print(f'Archived {len(arch)} cards and downloaded {ATTACH_COUNT} attachments.')

# Remove the Archived cards
# for card in cards:
#     card.set_closed(True)