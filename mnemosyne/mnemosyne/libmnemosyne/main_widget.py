#
# main_widget.py <Peter.Bienstman@UGent.be>
#


class MainWidget(object):
    
    """Describes the interface that the main widget needs to implement
    in order to be used by the main controller.

    """

    def information_box(self, message, OK_string):
        raise NotImplementedError
    
    def question_box(self, question, option0, option1, option2):
        raise NotImplementedError
    
    def error_box(self, event)
        raise NotImplementedError
    
    def save_file_dialog(self, path, filter, caption=""):
        raise NotImplementedError
    
    def open_file_dialog(self, path, filter, caption=""):
        raise NotImplementedError
    
    def run_add_card_dialog(self):
        raise NotImplementedError

    def run_edit_fact_dialog(self, fact):
        raise NotImplementedError
    
    def update_status_bar(self, message=None):
        raise NotImplementedError 
