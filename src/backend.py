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
    return h


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def page_revision_obj(rev_dt, prev, title, cards):
    """Returns the string representation of a page revision object.

    Args:
        rev_dt: datetime string of when the revision was created
        prev:   hash of the previous revision, or None (for the initial revision)
        title:  hash string of the page title
        cards:  list of hash strings of card content

    Returns:
        string. It will look like this:

            datetime <date and time of revision>
            [prev <hash of previous page revision object>]
            title <hash of page title>
            <hash of card #1>
            <hash of card #2>
            ...

      where the 'prev' line will be missing exactly when the prev parameter is None
    """
    if prev is None:
        prev_str = ""
    else:
        prev_str = "\nprev {}".format(prev)

    s = "datetime {}{}\ntitle {}\n".format(rev_dt, prev_str, title)

    for c in cards:
        s += "{}\n".format(c)

    return s



def web_state_obj(create_dt, prev, tagged_pages):
    """ Returns the string representation of a web state object.

    Args:
        create_dt:    datetime string of when the state was created
        prev:         hash string of previous state, or None if this is the initial
                      state
        tagged_pages: list of pairs where first component is hash string of page
                      revision and second component is a list of hashes of tags

    Returns:
        string. It will look like this:

            datetime <date and time the state was created>
            [prev <hash of previous state object>]
            page <hash of page #1>
            tag <hash of tag #1 for page #1>
            tag <hash of tag #2 for page #1>
            ...
            page <hash of page #2>
            tag <hash of tag #1 for page #2>
            tag <hash of tag #2 for page #2>
            ...
            ...

        where the 'prev' line will be missing exactly when the prev parameter is None

    """

    if prev is None:
        prev_str = ""
    else:
        prev_str = "\nprev {}".format(prev)

    s = "datetime {}{}\n".format(create_dt, prev_str)

    for p in tagged_pages:
        s += "page {}\n".format(p[0])
        for t in p[1]:
            s += "tag {}\n".format(t)

    return s


def get_next_rev_num(db, pid):
    cur = db.execute('select rev from page_revisions where pageid = ? order by rev desc',
            [pid])

    fetch = cur.fetchone()
    if fetch is None:
        return 1
    else:
        return fetch['num'] + 1


def set_state(state_hash):
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

    # TODO: check whether prev_page is a valid hash? 1) it may be empty in the case
    # of initial revision, but it might also be a junk hash
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

    # create web state object
    # TODO: need to append new page to list from previous state
    wso = web_state_obj(dt, prev_state, [(rev_num, tags)])
    wso_hash = insert_object(db, wso)
    set_state(wso_hash)

    db.commit()



if __name__ == '__main__':
    app = App()
    app.teardown()
