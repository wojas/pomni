#
# ui_controller_main.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UiControllerMain(Component):

    """A collection of logic used by the main Mnemosyne window and some related
    widgets.  The logic related to the review process is split out in a
    separated controller class, to allow that to be swapped out easily.

    """

    def __init__(self, name="", description=""):    
        self.name = None
        self.description = None
        self.widget = None
        
    def add_cards(self):
        raise NotImplementedError
    
    def edit_current_card(self):
        raise NotImplementedError
    
    def create_new_cards(self, fact_data, card_type, grade, cat_names):
        raise NotImplementedError
    
    def update_related_cards(self, fact, new_fact_data, new_card_type, \
                             new_cat_names):
        raise NotImplementedError
    
    def file_new(self):
        raise NotImplementedError
    
    def file_open(self):
        raise NotImplementedError
    
    def file_save(self):
        raise NotImplementedError
    
    def file_save_as(self):
        raise NotImplementedError
