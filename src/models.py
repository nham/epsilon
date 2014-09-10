class WebState:
    # TODO: think harder about whether we should initialize with a "dummy
    # state" containing no pages
    @staticmethod
    def get(db, state_id):
        """Get the data of a web state object.

        Args:
            db       - sqlite connection
            state_id - id of the entry in the web_states table

        Returns:
            None if the web hasn't been initialized
            otherwise, dict with 3 keys:
              - datetime: datetime string
              - prev: id of the previous state, or None
              - page_revs: list of ids of page revisions
        """
        sql = 'select datetime, prev from web_states where id = ?'
        cur = db.execute(sql, [state_id])
        state = cur.fetchone()

        if state is None:
            return None
        else:
            state = dict(state)

        sql = 'select wsp.pagerevid from web_state_pages wsp where wsp.stateid = ?'
        cur = db.execute(sql, [state_id])
        state['page_revs'] = [rev['pagerevid'] for rev in cur.fetchall()]

        return state

    # state data contains the datetime and the set of tagged pages
    @staticmethod
    def new(db, state_data):
        """Create a new web state object.

        Args:
            db         - sqlite connection
            state_data - dict with the following data:
                           - datetime: datetime string
                           - page_revs: list of page revision ids

        """

        sql = 'select id from web_states order by id desc'
        cur = db.execute(sql, [])
        prev = cur.fetchone()
        if prev is not None:
            prev = prev['id']

        sql = 'insert into web_states (datetime, prev) values (?, ?)'
        cur = db.execute(sql, [state_data['datetime'], prev])
        stateid = cur.lastrowid

        for rev in state_data['page_revs']:
            sql = 'insert into web_state_pages (stateid, pagerevid) values (?, ?)'
            cur = db.execute(sql, [stateid, rev])

        db.commit()

    @staticmethod
    def current_id(db):
        """Returns the current state or None if uninitialized."""
        sql = 'select id from web_states order by id desc'
        cur = db.execute(sql, [])
        state = cur.fetchone()

        if state is None:
            return None
        else:
            return state['id']

    @staticmethod
    def get_current(db):
        return WebState.get(db, WebState.current_id(db))


class PageRevision:
    @staticmethod
    def get(db, rev_id):
        """Get page revision by id."""
        sql = """SELECT pageid, prev, num, datetime, title from page_revisions pr
              WHERE pr.id = ?"""
        cur = db.execute(sql, [rev_id])
        rev = cur.fetchone()
        if rev is None:
            return None

        page_rev = dict(rev)

        sql = """SELECT cardid from page_rev_cards WHERE revid = ?"""
        page_rev['cards'] = [row['cardid'] for row in cur.fetchall()]

        sql = """SELECT tagid from page_rev_tags WHERE revid = ?"""
        page_rev['tags'] = [row['tagid'] for row in cur.fetchall()]

        return page_rev


    @staticmethod
    def add(db, rev_data):
        """Create a new page revision object.

        Args:
            db - sqlite connection
            rev_data: dict with the following data:
                        - pageid: page id
                        - prev: idea of the previous page revision, or None
                        - datetime: datetime string
                        - title: page title string
                        - cards: list of card ids
                        - tags: set of tag ids

        Returns:
            int, the id of the new page revision
        """
        # get the new revision number
        next_revnum = Page.get_latest_rev_num(db, rev_data['pageid']) + 1

        sql = """
            insert into page_revisions (pageid, prev, num, datetime, title)
            values (?, ?, ?, ?, ?)
            """
        cur = db.execute(sql, [rev_data['pageid'], rev_data['prev'], next_revnum,
                               rev_data['datetime'], rev_data['title']])
        revid = cur.lastrowid

        sql = """insert into page_rev_cards (revid, cardid, num)
                 values (?, ?, ?)"""
        for i, c in enumerate(rev_data['cards']):
            db.execute(sql, [revid, c, i])

        sql = 'insert into page_rev_tags (revid, tagid) values (?, ?)'
        for t in rev_data['tags']:
            db.execute(sql, [revid, t])

        db.commit()
        return revid


class Page:
    @staticmethod
    def add(db):
        """Create a new page.

        Args:
            db - sqlite connection

        Returns:
            int, the id of the new page
        """
        cur = db.execute('insert into pages default values')
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_latest_rev_num(db, page_id):
        sql = 'select num from page_revisions where pageid = ? order by num desc'
        cur = db.execute(sql, [page_id])
        curr_revnum = curr.fetchone()
        if curr_revnum is None:
            return 0
        else:
            return curr_revnum['num']


class Tag:
    @staticmethod
    def add(db, tag_name):
        cur = db.execute('insert into tags (name) values (?)', [tag_name])
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_id(db, tag_name):
        cur = db.execute('select id from tags where name = ?', [tag_name])
        fetch = cur.fetchone()
        if fetch is not None:
            return fetch['id']
        else:
            return None

    @staticmethod
    def ensure_present(db, tag_name):
        """Insert tag if not present. Return the tag id."""
        tid = Tag.get_id(db, tag_name)
        if tid is None:
            return Tag.add(db, tag_name)
        else:
            return tid

    @staticmethod
    def get_active(db):
        """Get all tags used by most recent revisions of pages"""
        sid = WebState.current_id(db)
        if sid is None:
            return []

        sql = """SELECT t.id, t.name from web_state_pages wsp
              LEFT JOIN page_rev_tags prt ON prt.revid = wsp.pagerevid
              LEFT JOIN tags t ON t.id = prt.tagid
              WHERE wsp.stateid = ?"""
        cur = db.execute(sql, [sid])
        return [dict(row) for row in cur.fetchall()]


class Card:
    @staticmethod
    def add(db, card_content):
        cur = db.execute('insert into cards (content) values (?)', [card_content])
        db.commit()
        return cur.lastrowid

    @staticmethod
    def get_id(db, card_content):
        """Gets the id associated with some card content."""
        cur = db.execute('select id from cards where content = ?', [card_content])
        fetch = cur.fetchone()
        if fetch is not None:
            return fetch['id']
        else:
            return None

    @staticmethod
    def ensure_present(db, card_content):
        """Insert card if not present. Return the card id."""
        cid = Card.get_id(db, card_content)
        if cid is None:
            return Card.add(db, card_content)
        else:
            return cid


    @staticmethod
    def get_active(db):
        """Get all cards used by most recent revisions of pages"""
        sid = WebState.current_id(db)
        if sid is None:
            return []

        sql = """SELECT c.id, c.content from web_state_pages wsp
              LEFT JOIN page_rev_cards prc ON prc.revid = wsp.pagerevid
              LEFT JOIN cards c ON c.id = prc.cardid
              WHERE wsp.stateid = ?"""
        cur = db.execute(sql, [sid])
        return [dict(row) for row in cur.fetchall()]
