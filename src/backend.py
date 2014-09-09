import hashlib
import base64
import os
import datetime
import sqlite3

state_file = "state"
db_file = "epsilon.db"

class App:
    def __init__(self):
        self.db = connect_db()

    def teardown(self):
        self.db.close()


def hash_data(data):
    """Make a hash string from some data.

    Args:
        data: byte sequence to be hashed

    Returns:
        a string which is the base64-encoded representation of the sha-256 hash
        of the data
    """
    hash_ob = hashlib.sha256(data)
    digest = hash_ob.digest()
    hashstr = base64.b64encode(digest).decode('utf-8')
    return hashstr


def connect_db():
    """Connects to the database. Returns the connection."""
    rv = sqlite3.connect(db_file)
    rv.row_factory = sqlite3.Row
    return rv

# db is a connection to a sqlite database
def init_db(db):
    with open('schema.sql', 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def init():
    if not os.path.exists(state_file):
        open(state_file, 'a').close()

    db = connect_db()
    init_db(db)
    db.close()


def insert_object(db, s):
    """Hashes data. Inserts it into the database if it's not there already

    Args:
        db: connection to a sqlite database
        s:  string

    Returns:
        string. base64 representation of the sha-256 hash of the string
    """
    h = hash_data(bytes(s, 'utf-8'))
    cur = db.execute('select hash from objects where hash = ?', [h])

    if cur.fetchone() == None:
        cur = db.execute('insert into objects (hash, data) values (?, ?)',
                [h, s])
        db.commit()

    return h


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def write_state_file(state_hash):
    with open(state_file, 'w') as f:
        f.write(state_hash)


# db is a connection to a sqlite database
# dt is a datetime string when the page was created
# page is a dictionary with the following fields:
# 
#   prev  - hash of previous page revision (missing only if this is initial revision)
#   title - page title
#   cards - list of card content
#   tags  - list of tags
#
# prev_state  - hash of previous state or None if this is initial state
#
# TODO: Probably we don't want to have to pass all card content in the future,
# the client should know exactly what cards changed. so instead we'll take a
# "delta": if card is unchanged, just send hash, otherwise send content
def add_page(db, dt, page, prev_state):
    cur = db.execute('insert into pages default values')
    pageid = cur.lastrowid

    # hash title, card content and insert any objects that are missing
    title_hash = insert_object(db, page['title'])
    cards = []
    for c in page['cards']:
        cards.append(insert_object(db, c))

    tags = []
    for t in page['tags']:
        tags.append(insert_object(db, t))

    # TODO: check whether prev_page is a valid hash?
    if 'prev' in page:
        prev_rev = page['prev']
    else:
        prev_rev = None

    rev = page_revision_obj(dt, prev_rev, title_hash, cards)
    rev_hash = insert_object(db, rev)

    rev_num = get_next_rev_num(db, pageid)
    # insert into page_revisions
    db.execute('insert into page_revisions (pageid, rev, hash) values (?, ?, ?)',
            [pageid, rev_num, rev_hash])

    # TODO: need to append new page to list from previous state
    set_state(db, dt, prev_state, [(rev_num, tags)])



def set_state(db, create_dt, prev, tagged_pages):
    """Create web state object and write it to the database and state file.
    """

    wso = web_state_obj(create_dt, prev, tagged_pages)
    wso_hash = insert_object(db, wso)
    write_state_file(wso_hash)


if __name__ == '__main__':
    app = App()
    app.teardown()
