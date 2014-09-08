import hashlib
import base64
import os
import datetime

state_file = "state"
db_file = "epsilon.db"

class App:
    def __init__(self):
        self.db = connect_db()

    def teardown(self):
        self.db.close()


# returns a base64-encoded string of the hash
def hash_data(data):
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


# db is db connection, s is object string
# this inserts the object if it's not in the objects table yet and returns
# the hash
def insert_object(db, s):
    h = hash_data(bytes(s, 'utf-8'))
    cur = db.execute('select hash from objects where hash = ?', [h])

    if cur.fetchone() == None:
        cur = db.execute('insert into objects (hash, data) values (?, ?)'
                [h, s])
    return h


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Returns the bytes for a page revision object. It will look like this:
#
#   datetime <date and time of revision>
#   prev <hash of previous page revision object or empty if this is the initial revision>
#   title <hash of page title>
#   <hash of card #1>
#   <hash of card #2>
#   ...
#
# rev_dt: a datetime string,
# prev: hash of previous revision
# title: hash of the page title,
# cards: list of hashes of card content
def page_revision_obj(rev_dt, prev, title, cards):
    s = "datetime {}\nprev {}\ntitle {}\n".format(rev_dt, prev, title)

    for c in cards:
        s += "{}\n".format(c)

    return s


# Returns the bytes for a web state object. It will look like this:
#
#   datetime <date and time the state was created>
#   prev <hash of previous state object or empty if this is initial state>
#   page <hash of page #1>
#   tag <hash of tag #1 for page #1>
#   tag <hash of tag #2 for page #1>
#   ...
#   page <hash of page #2>
#   tag <hash of tag #1 for page #2>
#   tag <hash of tag #2 for page #2>
#   ...
#   ...
#
# create_dt: a datetime string
# prev: hash of previous state
# tagged_pages: list of pairs where first component is hash of page revision
#               and second component is list of hash of tags
def web_state_obj(create_dt, prev, tagged_pages):
    s = "datetime {}\nprev {}\n".format(create_dt, prev, title)

    for p in tagged_pages:
        s += "page{}\n".format(p[0])
        for t in p[1]:
            s += "tag{}\n".format(t)

    return s


def get_next_rev_num(db, pid):
    cur = db.execute('select rev from page_revisions where hash = ?', [h])

    fetch = cur.fetchone()
    if fetch is None:
        return 1
    else:
        return fetch['num'] + 1


# db is a connection to a sqlite database
# dt is a datetime string when the page was created
# page is a dictionary with the following fields:
# 
#   prev  - hash of previous page revision (missing only if this is initial revision)
#   title - page title
#   cards - list of card content
#
# prev_state  - hash of previous state (missing only if this is initial state)
# tags - list of hashes of tags
#
# TODO: Probably we don't want to have to pass all card content in the future,
# the client should know exactly what cards changed. so instead we'll take a
# "delta": if card is unchanged, just send hash, otherwise send content
def add_page(db, dt, page, prev_state, tags):
    cur = db.execute('insert into pages () values ()')
    pageid = cur.lastrowid

    # hash title, card content and insert any objects that are missing
    title_hash = insert_object(db, page['title'])
    cards = []
    for c in page['cards']:
        cards.append(insert_object(db, c))

    # TODO: check whether prev_page is a valid hash? 1) it may be empty in the case
    # of initial revision, but it might also be a junk hash
    rev = page_revision_obj(dt, page['prev'], title_hash, cards)
    rev_hash = insert_object(db, rev)

    rev_num = get_next_rev_num(db, pageid)
    # insert into page_revisions
    db.execute('insert into page_revisions (pageid, rev, hash) values (?, ?, ?)',
            [pageid, rev_num, rev_hash])

    # create web state object
    wso = web_state_obj(dt, prev_state, [(rev_num, tags)])

    # insert it
    # update current state to the new WSO


if __name__ == '__main__':
    app = App()
    app.teardown()
