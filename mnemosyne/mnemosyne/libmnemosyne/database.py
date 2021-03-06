#
# database.py <Peter.Bienstman@UGent.be>
#

from component import Component


#  TODO: load_failed mechanism, to prevent overwriting a database which
#  failed to load.

class Database(Component):

    """Interface class describing the functions to be implemented by the
    actual database classes.

    """

    # Creating, loading and saving the entire database.

    def new(self, path):
        raise NotImplementedError

    def save(self, path):
        raise NotImplementedError

    def backup(self):
        raise NotImplementedError

    def load(self, path):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def is_loaded():
        raise NotImplementedError

    # Start date.

    def set_start_date(self, start_date_obj):
        raise NotImplementedError

    def days_since_start(self):
        raise NotImplementedError

    # Adding, modifying and deleting categories, facts and cards.

    def add_category(self, category):
        raise NotImplementedError

    def modify_category(self, modified_category):
        raise NotImplementedError

    def delete_category(self, category):
        raise NotImplementedError

    def get_or_create_category_with_name(self, name):
        raise NotImplementedError

    def remove_category_if_unused(self, cat):
        raise NotImplementedError

    def add_fact(self, fact):
        raise NotImplementedError

    def update_fact(self, fact):
        raise NotImplementedError
        
    def add_fact_view(self, fact_view, card):
        raise NotImplementedError

    def update_fact_view(self, fact_view):
        raise NotImplementedError

    def add_card(self, card):
        raise NotImplementedError

    def update_card(self, card):
        raise NotImplementedError
        
    def cards_from_fact(self, fact):
        raise NotImplementedError
        
    def delete_fact_and_related_data(self, fact):
        raise NotImplementedError
        
    # Queries.

    def category_names(self):
        raise NotImplementedError

    def has_fact_with_data(self, fact_data):
        raise NotImplementedError

    def duplicates_for_fact(self, fact):

        """Returns list of facts which have the same unique key."""

        raise NotImplementedError

    def fact_count(self):
        raise NotImplementedError

    def card_count(self):
        raise NotImplementedError

    def non_memorised_count(self):
        raise NotImplementedError

    def scheduled_count(self, days=0):
        raise NotImplementedError

    def active_count(self):
        raise NotImplementedError

    def average_easiness(self):
        raise NotImplementedError

    # Filter is a SQL filter, used e.g. to filter out inactive categories.

    def set_filter(self, filter):
        raise NotImplementedError

    # The following functions should return an iterator, in order to 
    # save memory. sort_key is an attribute of card to be used for sorting.
    # (Note that this is different from the sort key used to sort lists in
    # the Python itself, in order to allow easier interfacing with SQL.)

    def cards_due_for_ret_rep(self, sort_key=""):
        raise NotImplementedError

    def cards_due_for_final_review(self, grade, sort_key=""):
        raise NotImplementedError

    def cards_new_memorising(self, grade, sort_key=""):
        raise NotImplementedError

    def cards_unseen(self, sort_key=""):
        raise NotImplementedError
    
    def cards_learn_ahead(self, sort_key=""):
        raise NotImplementedError

