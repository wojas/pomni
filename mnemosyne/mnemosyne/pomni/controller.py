#!/usr/bin/python -tt
# vim: sw=4 ts=4 expandtab ai
#
# Pomni. Learning tool based on spaced repetition technique
#
# Copyright (C) 2008 Pomni Development Team <pomni@googlegroups.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
#

"""
MVC Controller
"""

from mnemosyne.libmnemosyne.component_manager import ui_controller_review, ui_controller_main
from mnemosyne.libmnemosyne import component_manager

class Controller:
    """ MVC pattern. Controller. Manages the model and the view.
    Get user input from the view.
    Call apropriate methods from model and view.
    Get events from the model if needed.
    """

    def __init__(self, model, view):
        self.model, self.view = model, view
        model.register(self)
        #ui_controller_main().widget = component_manager.get_current("main_widget")()
        ui_controller_review().widget = component_manager.get_current("review_widget")()

    def start(self, mode):
        """ Start the application """

        self.view.start(mode)

        #if not mode or mode == 'review':
        #    ui_controller_review().start()

    def update(self, model):
        """ This method is part of Observer pattern
            it's called by observable(Model in our case) to notify
            about its change
        """
        pass


def _test():
    """ Run doctests
    """
    import doctest
    doctest.testmod()


if __name__ == "__main__":
    _test()


# Local Variables:
# mode: python
# py-indent-offset: 4
# indent-tabs-mode nil
# tab-width 4
# End: