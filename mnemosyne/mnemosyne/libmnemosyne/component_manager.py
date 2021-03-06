#
# component_manager.py <Peter.Bienstman@UGent.be>
#


class ComponentManager(object):

    """Manages the different components. Each component belongs to a type
    (database, scheduler, card_type, card_type_widget, ...).

    The component manager can also store relationships between components,
    e.g. a card_type_widget is used for a certain card_type.

    For certain components, many can be active at the same time (card types,
    filters, function hooks, ...). For others, there can be only on active
    at the same time, like schedule, database ... The idea is that the last
    one registered takes preference. This means that e.g. the default
    scheduler needs to be registered first.

    Managed components:

       ======================   ===============================
       "config"                 configuration instance
       "log"                    logger instance
       "database"               database instance
       "scheduler"              scheduler instance
       "filter"                 filter instance
       "card_type"              card_type instance
       "card_type_widget"       card_type_widget class,
                                used_for card_type class name
       "renderer"               renderer instance,
                                used_for card_type class name
       "ui_controller_main"     ui_controller_main instance
       "ui_controller_review"   ui_controller_review instance
       "review_widget"          review_widget class
       "plugin"                 plugin instance
       "function_hook"          function hook instance
                                used_for hookpoint_name
       ======================   ===============================
       
    Note: for widgets we store the class name as opposed to an instance,
    since creating widgets can be time consuming, and we want to create
    e.g. card type widgets only when they are really needed.

    """
    
    # TODO KW: investigate inheritance in the context of used_for.
        
    def __init__(self):
        self.components = {} # { used_for : {type : [component]} }
        self.card_type_by_id = {}

    def register(self, type, component, used_for=None):
        """For type, component and used_for, see the table above."""
        
        if type not in ["config", "log", "database", "scheduler", "filter",
                        "card_type", "card_type_widget", "renderer",
                        "ui_controller_main", "ui_controller_review", 
                        "review_widget", "ui_controller_input", "plugin"]:
           raise KeyError("Invalid component type % s.", type)
        if not self.components.has_key(used_for):
            self.components[used_for] = {}
        if not self.components[used_for].has_key(type):
            self.components[used_for][type] = [component]
        else:
            if component not in self.components[used_for][type]:
                self.components[used_for][type].append(component)
        if type == "card_type":
            self.card_type_by_id[component.id] = component

    def unregister(self, type, component, used_for=None):
        self.components[used_for][type].remove(component)

    def get_all(self, type, used_for=None):

        """For components for which there can be many active at once."""

        try:
            return self.components[used_for][type]
        except:
            return []
        
    def get_current(self, type, used_for=None):

        """For component for which there can be only one active at one time."""

        try:
            return self.components[used_for][type][-1]
        except:
            return None


# The component manager needs to be accessed by many different parts of the
# library, so we hold it in a global variable.

component_manager = ComponentManager()


# Convenience functions, for easier access from the outside world.

def config():
    return component_manager.get_current("config")
    
def log():
    return component_manager.get_current("log")
    
def database():
    return component_manager.get_current("database")

def scheduler():
    return component_manager.get_current("scheduler")

def ui_controller_main():
    return component_manager.get_current("ui_controller_main")

def ui_controller_review():
    return component_manager.get_current("ui_controller_review")

def ui_controller_input():
    return component_manager.get_current("ui_controller_input")

def card_types():
    return component_manager.get_all("card_type")

def card_type_by_id(id):
    # TODO KW: use named components for this.
    return component_manager.card_type_by_id[id]

def filters():
    return component_manager.get_all("filter")

