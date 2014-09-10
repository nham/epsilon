import os
import datetime
import sqlite3
import models

db_file = "epsilon.db"

class App:
    def __init__(self):
        self.db = connect_db()

    def teardown(self):
        self.db.close()


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
    db = connect_db()
    init_db(db)
    db.close()


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# TODO: Probably we don't want to have to pass all card content in the future,
# the client should know exactly what cards changed. so instead we'll take a
# "delta": if card is unchanged, just send hash, otherwise send content
def add_page(db, dt, title, cards, tags):
    """Add a new page to the web.

    Args:
        db - a connection to a sqlite database
        dt - a datetime string when the page was created
        title - page title
        cards - list of card content
        tags  - list of tags
    """
    # create new page in table
    pid = models.Page.add(db)

    # insert any missing cards or tags into db, get the ids
    card_ids = []
    for card in cards:
        card_ids.append(models.Card.ensure_present(card))

    tag_ids = []
    for tag in tags:
        tag_ids.append(models.Tag.ensure_present(tag))

    # create new page revision
    page_rev = {'pageid': pid,
                'prev': None,
                'datetime': dt,
                'title': title,
                'cards': card_ids,
                'tags': tag_ids}

    rev_id = models.PageRevision.add(db, page_rev)

    # create new web state
    state = models.WebState.get_current(db)
    models.WebState.new(db, {'datetime': dt,
                             'page_revs': state['page_revs'] + [rev_id]})


if __name__ == '__main__':
    app = App()
    app.teardown()
