class WebState:
    @staticmethod
    def get(db, state_id):
        """Get the data of a web state object.

        Args:
            db       - sqlite connection
            state_id - id of the entry in the web_states table

        Returns:
            dict with 3 keys:
              - datetime: datetime string
              - prev: id of the previous state, or None
              - pagerevs: list of ids of page revisions
        """
        sql = 'select datetime, prev from web_states where id = ?'
        cur = db.execute(sql, [state_id])
        state = cur.fetchone()
        state = dict(state)

        sql = 'select wsp.pagerevid from web_state_pages wsp where wsp.stateid = ?'
        cur = db.execute(sql, [state_id])
        state['pagerevs'] = [rev['pagerevid'] for rev in cur.fetchall()]

        return state

    # state data contains the datetime and the set of tagged pages
    @staticmethod
    def new(db, state_data):
        """Create a new web state object.

        Args:
            db         - sqlite connection
            state_data - dict with the following data:
                           - datetime: datetime string
                           - pagerevs: list of page revision ids

        """

        sql = 'select id from web_states order by id desc'
        cur = db.execute(sql, [])
        prev = cur.fetchone()
        if prev is not None:
            prev = prev['id']

        sql = 'insert into web_states (datetime, prev) values (?, ?)'
        cur = db.execute(sql, [state_data['datetime'], prev])
        stateid = cur.lastrowid

        for rev in state_data['pagerevs']:
            sql = 'insert into web_state_pages (stateid, pagerevid) values (?, ?)'
            cur = db.execute(sql, [stateid, rev])

        db.commit()


class PageRevision:
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

class Card:
    @staticmethod
    def add(db, card_content):
        cur = db.execute('insert into cards (content) values (?)', [card_content])
        db.commit()
        return cur.lastrowid
