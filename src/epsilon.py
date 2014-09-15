from flask import Flask, jsonify, g
import models
import sqlite3
import datetime

DATABASE = "epsilon.db"

app = Flask(__name__)

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/states')
def all_states():
    """Returns data for all web states."""
    db = get_db()
    data = {}

    data['cards'] = {}
    for card in models.Card.get_all(db):
        data['cards'][card['id']] = {'content': card['content']}

    data['tags'] = {}
    for tag in models.Tag.get_all(db):
        data['tags'][tag['id']] = {'name': tag['name']}

    data['curr_state'] = models.WebState.current_id(db)

    data['states'] = {}
    for state in models.WebState.get_all(db):
        page_revs = {}
        for rev_id in state['page_revs']:
            page_revs[rev_id] = models.PageRevision.get(db, rev_id)

        state['page_revs'] = page_revs

        sid = state['id']
        data['states'][sid] = state


    return jsonify(data)

@app.route('/states/current')
def current_state():
    """Returns JSON data needed to populate the main interface.

    TODO: What should this return, exactly? a sensible first approach is:
      - all cards
      - all tags
      - the most recent revision of each page

    I don't think this can be a permanent solution since the number of pages
    may be very large. So maybe we should only initially send the content/tags
    of the n most recently updated pages, or whatever.

    We would probably always send the most recent revision of every page,
    meaning the content in the page_revisions table, since that contains 
    title and datetime data, which we definitely need.
    """
    db = get_db()
    state = models.WebState.get_current(db)

    if state is None:
        return jsonify({})

    page_revs = {}
    for rev_id in state['page_revs']:
        page_revs[rev_id] = models.PageRevision.get(db, rev_id)

    state['page_revs'] = page_revs

    state['cards'] = {}
    cards = models.Card.get_active(db)
    for card in cards:
        state['cards'][card['id']] = {'content': card['content']}

    state['tags'] = {}
    tags = models.Tag.get_active(db)
    for tag in tags:
        state['tags'][tag['id']] = {'name': tag['name']}

    return jsonify(state)


def connect_db():
    """Connects to the specific database. Returns the connection."""
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context. Returns the connection (new or existing).
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


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
        card_ids.append(models.Card.ensure_present(db, card))

    tag_ids = []
    for tag in tags:
        tag_ids.append(models.Tag.ensure_present(db, tag))

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
    page_revs = [] if state is None else state['page_revs']
    models.WebState.new(db, {'datetime': dt,
                             'page_revs': page_revs + [rev_id]})



if __name__ == '__main__':
    app.run(debug = True)
