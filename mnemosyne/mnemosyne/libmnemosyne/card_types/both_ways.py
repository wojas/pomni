#
# both_ways.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView


class BothWays(CardType):

    def __init__(self, language_name=""):
        CardType.__init__(self)
        if not language_name:
            self.id = "2"
            self.name = _("Front-to-back and back-to-front")
            self.is_language = False
        else:
            self.id = "2_" + language_name
            self.name = language_name
            self.is_language = True
            
        # List and name the keys.
        self.fields.append(("q", _("Question")))
        self.fields.append(("a", _("Answer")))
        
        # Front-to-back.
        v = FactView(1, _("Front-to-back"))
        v.q_fields = ["q"]
        v.a_fields = ["a"]
        v.required_fields = ["q"]
        self.fact_views.append(v)
        
        # Back-to-front.
        v = FactView(2, _("Back-to-front"))
        v.q_fields = ["a"]
        v.a_fields = ["q"]
        v.required_fields = ["a"]
        self.fact_views.append(v)
        
        # The question field needs to be unique. As for duplicates is the answer
        # field, these are better handled through a synonym detection plugin.
        self.unique_fields = ["q"]
        
        # CSS. TODO: read from file if exists.
        self.css = """
            <style type="text/css">
            table { margin-left: auto;
                margin-right: auto; /* Centers table, but not its contents. */
                height: 100%; }
            body {  color: black;
                background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
            q { text-align: center; } /* Align contents within the cell. */
            a { text-align: center; }
            </style>
        """
    
