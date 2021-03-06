#!/usr/bin/python -tt
# vim: sw=4 ts=4 expandtab ai
#
# sqlite.py
#
# Author: Ed Bartosh <bartosh@gmail.com>
#
# Sun Dec 28 09:23:54 UTC 2008 

"""Sqlite backend."""

SCHEMA = """
    create table facts(
        id integer primary key,
        guid,
        facttype_id int,
        ctime timestamp,
        mtime timestamp
    );

    create table factdata(
        id integer primary key,
        fact_id int,
        key text,
        value text
    );

    create table facttypes(
        id,
        name varchar(20) UNIQUE NOT NULL,
        enabled default 1
    );

    create table views(
        id,
        facttype_id int,
        name varchar(20) UNIQUE NOT NULL,
        enabled boolean default 1
    );

    create table reviewstats(
        id,
        fact_id int,
        view_id int,
        grade int,
        easiness real,
        lapses int,
        acq_reps int,
        acq_reps_since_lapse int,
        last_rep int,
        next_rep int,
        unseen boolean default 0
    );

    create table categories(
        id integer primary key,
        parent_id int default 0,
        name varchar(20) UNIQUE NOT NULL,
        enabled boolean default 1
    );

    create table fact_categories(
        id integer primary key,
        category_id int,
        fact_id int
    );

    create table reviews(
        card_id int,
        time timestamp,
        number int,
        prev int,
        client_guid int
    );

    create table meta(
        id integer primary key,
        key,
        value
    );
"""

from datetime import datetime
import sqlite3 as sqlite

from mnemosyne.libmnemosyne.start_date import StartDate
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component_manager import config, log
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import card_types
from mnemosyne.libmnemosyne.database import Database
from mnemosyne.libmnemosyne.category import Category
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.fact_view import FactView


class Sqlite(Database):

    """Sqlite database backend class."""

    def __init__(self):
        self._connection = None
        self.path = None
        self.start_date = None
        self.load_failed = False
        self.start_date = None
        self.filter = ""

    @property
    def conn(self):
        """Connect to the database. Lazy."""

        if not self._connection:
            self._connection = sqlite.connect(self.path,
                detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
            self._connection.row_factory = sqlite.Row

        return self._connection

    def new(self, path):
        """ Create new database """

        self.path = path

        if self.is_loaded():
            self.unload()

        self.start_date = StartDate()
        config()["path"] = path
        log().new_database()

        # create tables according to schema
        self.conn.executescript(SCHEMA)

        # save start_date
        self.conn.execute("insert into meta(key, value) values(?,?)",
        ("start_date", datetime.strftime(self.start_date.start,
                                         '%Y-%m-%d %H:%M:%S')))

        self.save()

    def save(self, path=None):
        """Commit changes."""

        # Saving to another file not implemented
        if path and path != self.path:
            raise NotImplementedError

        self.conn.commit()

    def backup(self):
        """Backup database. Not Implemented."""

        # FIXME: wait for pickle implementation, then implement
        pass

    def load(self, fname):
        """Load database from file."""

        # Unload opened database if exists
        self.unload()

        self.path = expand_path(fname, config().basedir)
        try:
            res = self.conn.execute("select value from meta where key=?",
                ("start_date", )).fetchone()
            self.load_failed = False
            self.set_start_date(StartDate(datetime.strptime(res["value"],
                "%Y-%m-%d %H:%M:%S")))
            self.load_failed = False
        except sqlite.OperationalError:
            self.load_failed = True

    def unload(self):
        """Commit changes and close connection to the database."""

        if self._connection:
            self._connection.commit()
            self._connection.close()
            self._connection = None
            self.load_failed = False

    def is_loaded(self):
        """Is connection set?"""

        return bool(self._connection)

    # Get objects from the database

    def get_view(self, view_id):
        """Get view object by id."""

        res = self.conn.execute("select name from views where id=?",
            (view_id, )).fetchone()

        fact_view = FactView(view_id, res["name"])

        # Find fact view in registered card_types and copy
        # *fields attributes from it
        for card_type in card_types():
            for view in card_type.fact_views:
                if view.name == res["name"]:
                    fact_view.q_fields = view.q_fields
                    fact_view.a_fields = view.a_fields
                    fact_view.required_fields = view.required_fields
                    return fact_view

        raise RuntimeError("Wrong view(id=%d) found in the database" % view_id)

    def get_fact(self, guid=None, fact_id=None):
        """Get fact object by guid."""

        # Get fact by id or guid
        if guid:
            fact = self.conn.execute("select * from facts where guid=?",
                (guid, )).fetchone()
        elif fact_id:
            fact = self.conn.execute("select * from facts where id=?",
                            (fact_id, )).fetchone()
        else:
            raise RuntimeError("get_fact: No guid nor fact_id provided")

        # Get fact data by fact id
        cursor = self.conn.execute("""select * from factdata
            where fact_id=?""", (fact["id"], ))

        data = dict([(item["key"], item["value"]) for item in cursor])

        categories = [Category(cat["name"]) for cat in
            self.conn.execute("""select cat.name from categories as cat,
            fact_categories as f_cat where f_cat.category_id=cat.id and
            f_cat.fact_id=?""", (fact["id"], ))]

        card_type = card_type_by_id(str(fact["facttype_id"]))

        return Fact(data, card_type, categories,
                    uid=fact['guid'], added=fact['ctime'])

    @staticmethod
    def get_card(fact, view, sql_res):
        """Get card object from fact, view and query result."""

        card = Card(fact, view)
        for attr in ("id", "grade", "lapses", "easiness", "acq_reps",
                     "acq_reps_since_lapse", "last_rep", "next_rep", "unseen"):
            setattr(card, attr, sql_res[attr])

        return card

    # Start date.

    def set_start_date(self, start_date_obj):
        """Setter for start_date attribute."""

        self.start_date = start_date_obj

    def days_since_start(self):
        """Return amount of days since start_date."""

        return self.start_date.days_since_start()

    # Adding, modifying and deleting categories, facts and cards.

    def add_category(self, category):
        """Add new category."""

        self.conn.execute("insert into categories(name) values(?)",
            (category.name, ))

    def delete_category(self, category):
        """Delete category."""

        self.conn.execute("delete from categories were name=?",
            (category.name, ))

    def get_or_create_category_with_name(self, name):
        """Try to get category from the database
            create if not found.
        """
        
        category = self.conn.execute("""select *
            from categories where name=?""", (name, )).fetchone()
        if category:
            return Category(category["name"])

        self.conn.execute("""insert into categories(name)
            values(?)""", (name, ))
        self.conn.commit()

        return Category(name)

    def add_fact(self, fact):
        """Add new fact."""

        # Add record into fact types if needed
        if self.conn.execute("""select count() from facttypes where
            name=?""", (fact.card_type.name, )).fetchone()[0] == 0:
            self.conn.execute("""insert into facttypes(id, name)
                    values(?,?)""", (fact.card_type.id, fact.card_type.name, ))

        # Add fact to facts and factdata tables
        fact_id = self.conn.execute("""insert into facts(guid,
            facttype_id, ctime) values(?,?,?)""", (fact.uid, fact.card_type.id,
            fact.added)).lastrowid

        self.conn.executemany("""insert into factdata(fact_id,key,value)
            values(?,?,?)""", ((fact_id, key, value)
                for key, value in fact.data.items()))

        # Link fact to its categories
        for cat in fact.cat:
            cat_id = self.conn.execute("""select id from categories
                where name=?""", (cat.name, )).fetchone()[0]
            self.conn.execute("""insert into fact_categories(category_id,
                fact_id) values(?,?)""", (cat_id, fact_id))

        self.conn.commit()

    def update_fact(self, fact):
        """Update fact."""

        # update factdata
        self.conn.executemany("""update factdata set value=?
            where fact_id=? and key=?""", ((value, fact.uid, key)
                for key, value in fact.data.items()))

        # update timestamp
        self.conn.execute("update facts set mtime=? where guid=?",
            (datetime.now(), fact.uid))

    def add_fact_view(self, fact_view, card):
        """Add new view."""

        fact = self.get_fact(card.fact.uid)

        self.conn.execute("""insert into views(id, facttype_id, name)
           values(?,?,?)""", (fact_view.id, fact.card_type.id, fact_view.name))

    def update_fact_view(self, fact_view):
        """Update view."""

        self.conn.execute("update views set name=? where id=?",
            (fact_view.name, fact_view.id))

    def add_card(self, card):
        """Add new card and its fact_view."""

        self.conn.execute("""insert into reviewstats(id, fact_id,
            view_id, grade, lapses, easiness, acq_reps, acq_reps_since_lapse,
            last_rep, next_rep, unseen) values(?,?,?,?,?,?,?,?,?,?,?)""",
            (card.id, card.fact.uid, card.fact_view.id, card.grade,
            card.lapses, card.easiness, card.acq_reps,
            card.acq_reps_since_lapse, card.last_rep, card.next_rep,
            card.unseen))

        # Add view if doesn't exist
        if not self.conn.execute("select count() from views where id=?",
                (card.fact_view.id, )).fetchone()[0]:
            self.add_fact_view(card.fact_view, card)

        log().new_card(card)

    def update_card(self, card):
        """Update card."""

        self.conn.execute("""update reviewstats set grade=?, easiness=?,
            lapses = ?, acq_reps=?, acq_reps_since_lapse=?, last_rep=?,
            next_rep=?, unseen=? where id=?""", (card.grade, card.easiness,
            card.lapses, card.acq_reps, card.acq_reps_since_lapse,
            card.last_rep, card.next_rep, card.unseen, card.id))

    def cards_from_fact(self, fact):
        """Generate cards related to fact."""

        cursor = self.conn.execute("""select * from reviewstats
            where fact_id=?""", (fact.uid, ))

        return (self.get_card(fact, self.get_view(res['view_id']), res)
            for res in cursor)

    def delete_fact_and_related_data(self, fact):
        """Delete fact and all relations to it."""

        # Get fact id by uid
        fact_id = self.conn.execute("select id from facts where guid=?",
            (fact.uid, )).fetchone()["id"]

        # Delete related records from other tables (linked by id)
        for table in ("factdata", "fact_categories"):
            self.conn.execute("delete from %s where fact_id=?" % table,
                (fact_id, ))

        # Delete from reviewstats (linked by uid)
        self.conn.execute("delete from reviewstats where fact_id=?",
                (fact.uid, ))

        # Delete record from facts table
        self.conn.execute("delete from facts were guid=?",
                    (fact.uid, ))

    # Queries.

    def category_names(self):
        """Generate categories' names."""

        return (res[0] for res in
            self.conn.execute("select name from categories"))

    def has_fact_with_data(self, fact_data):
        """Check if there is already the fact with fact_data."""

        fact_ids = set()
        for key, value in fact_data.items():
            item_fact_ids = set()
            # if key and value from fact_data isn't in the database
            # we don't have such a fact
            if not self.conn.execute("""select count() from factdata
                where key=? and value=?""", (key, value)).fetchone()[0]:
                return False

            for res in self.conn.execute("""select fact_id from factdata
                where key=? and value=?""", (key, value)):
                item_fact_ids.add(res["fact_id"])

            # save fact_ids found on the first run
            if not fact_ids:
                fact_ids = item_fact_ids
            else:
                # assign common ids to fact_ids
                fact_ids = fact_ids.intersection(item_fact_ids)
                # if there is no common fact_ids we don't have
                # fact with fact_data
                if not fact_ids:
                    return False
        return True

    def duplicates_for_fact(self, fact):
        """Return list of facts with the same key."""

        # find duplicate fact data
        duplicates = []
        for value in fact.data.values():
            for res in self.conn.execute("""select * from factdata
                where value=?""", (value, )):
                fact_db = self.get_fact(fact_id=res['fact_id'])
                # Filter out facts from other categories
                for cat in fact_db.cat:
                    if cat in fact.cat:
                        duplicates.append(fact_db)
                        break
        return duplicates

    def fact_count(self):
        """Get total of facts."""

        return self.conn.execute("select count() from facts").fetchone()[0]

    def card_count(self):
        """Get total number of cards."""

        return self.conn.execute("select count() from reviewstats").\
                fetchone()[0]

    def non_memorised_count(self):
        """Get number of non memorised cards."""

        return self.conn.execute("""select count() from reviewstats
            where grade < 2""").fetchone()[0]

    def scheduled_count(self, days=0):
        """Get number of cards scheduled within 'days' days."""

        count = self.conn.execute("""select count() from reviewstats
            where grade >=2 and ? >= next_rep - ?""",
            (self.days_since_start(), days)).fetchone()[0]
        return count

    def active_count(self):
        """Get number of cards in an active category."""

        return self.conn.execute("""select count() from fact_categories,
                categories where category_id = categories.id and
                categories.enabled=1""").fetchone()[0]

    def average_easiness(self):
        """Get average easiness of cards."""

        average = self.conn.execute("""select sum(easiness)/count()
            from reviewstats""").fetchone()[0]
        if average:
            return average
        else:
            return 2.5

    # Filter is a SQL filter, used e.g. to filter out inactive categories.

    def set_filter(self, attr):
        """Set filter for category attribute.
           See below methods for details
        """

        self.filter = attr

    def cards_due_for_ret_rep(self, sort_key="id"):
        """Generate cards due for repetition."""

        if sort_key == "interval":
            sort_key = "next_rep - last_rep"

        return(self.get_card(self.get_fact(res["fact_id"]),
               self.get_view(res["view_id"]), res) for res in
               self.conn.execute("""select * from reviewstats
                where grade >=2 and ? >= next_rep order by %s""" % sort_key,
                (self.start_date.days_since_start(), )))

    def cards_due_for_final_review(self, grade, sort_key="random()"):
        """Generate cards for final review."""

        return (self.get_card(self.get_fact(res["fact_id"]),
                self.get_view(res["view_id"]), res) for res in
                self.conn.execute("""select * from reviewstats where grade = ?
                    and lapses > 0 order by %s""" % sort_key, (grade, )))

    def cards_new_memorising(self, grade, sort_key="random()"):
        """Generate cards for new memorising (lapses=0 and unseen=0)."""

        return (self.get_card(self.get_fact(res["fact_id"]),
               self.get_view(res["view_id"]), res) for res in
               self.conn.execute("""select * from reviewstats
               where grade = ? and lapses = 0 and unseen = 0
               order by %s""" % sort_key, (grade, )))

    def cards_unseen(self, sort_key="id", randomise=False):
        """Generate unseen cards."""
    
        if randomise:
            sort_key = "random()"
        
        return (self.get_card(self.get_fact(res["fact_id"]),
                self.get_view(res["view_id"]), res) for res in
                self.conn.execute("""select * from reviewstats
                where unseen = 1 order by %s""" % sort_key))
        
    def cards_learn_ahead(self, sort_key="id"):
        """Generate cards for learning ahead."""

        return(self.get_card(self.get_fact(res["fact_id"]),
               self.get_view(res["view_id"]), res) for res in
               self.conn.execute("""select * from reviewstats
               where grade >=2 and ? < next_rep order by %s""" % sort_key,
               (self.start_date.days_since_start(), )))


# Local Variables:
# mode: python
# py-indent-offset: 4
# indent-tabs-mode nil
# tab-width 4
# End:
