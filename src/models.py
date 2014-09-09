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
                        - title: id of page title
                        - cards: list of card ids
                        - tags: list of tag ids
        """
        sql = """
            insert into page_revisions (pageid, prev, num, datetime, title)
            values (?, ?, ?, ?, ?)
            """
