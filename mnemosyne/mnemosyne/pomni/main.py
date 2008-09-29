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
Main 
"""

import sys
import os

# add mnemosyne directory to Python path in debug mode
if os.path.basename(sys.argv[0]).endswith("debug"):
    sys.path.insert(0, "../")
    sys.path.insert(0, "../../")

from optparse import OptionParser

from mnemosyne import libmnemosyne
from mnemosyne.libmnemosyne.component_manager import database, scheduler

from pomni.factory import ui_factory, backend_factory
from pomni.model import Model
from pomni.controller import Controller

def parse_commandline(argv):
    """ Parse commandline, check options """

    parser = OptionParser(usage = "%prog [options]")

    parser.add_option("--ui", type="string", dest="ui", help="specify ui type")
    parser.add_option("--backend", type="string", dest="backend",
                        help="specify storage backend")
    parser.add_option("-d", "--datadir", dest="datadir", help="data directory")
    parser.add_option("--mode", type="string", dest="mode", 
                        help="specify working mode. 'input', 'review' or 'conf'")

    options, argv = parser.parse_args(argv)

    return (options, argv)

def _create_example_cards(db_name):
    """ Temporary: Create some example cards. Must be removed when ui is ready """
    
    from mnemosyne.libmnemosyne.component_manager import ui_controller_main, card_types

    c = ui_controller_main()
    c.create_new_cards({'q': 'word 1', 'a': 'translation 1'}, card_types()[0], 0, ('category1'))
    c.create_new_cards({'q': 'word 2', 'a': 'translation 2'}, card_types()[0], 0, ('category1'))
    c.create_new_cards({'q': 'word 3', 'a': 'translation 3'}, card_types()[0], 0, ('category1'))

    database().save(db_name)

def main(argv):
    """ Main """

    opts, argv = parse_commandline(argv)

    # FIXME: move this to config module
    if opts.datadir:
        datadir = os.path.abspath(options.datadir)
    elif os.path.exists(os.path.join(os.getcwdu(), ".mnemosyne")):
        datadir = os.path.abspath(os.path.join(os.getcwdu(), ".mnemosyne"))

    libmnemosyne.initialise(datadir)

    cdatabase = database()
    # FIXME: take db name from config
    db_name = os.path.join(datadir, "default.mem")

    if os.path.exists(db_name):
        cdatabase.load(db_name)

    if not cdatabase.card_count():
        _create_example_cards(db_name)

    cscheduler = scheduler()
    model = Model(cdatabase, cscheduler)
    view = ui_factory(model, opts.ui)
    
    controller = Controller(model, view)

    return controller.start(opts.mode)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

# Local Variables:
# mode: python
# py-indent-offset: 4
# indent-tabs-mode nil
# tab-width 4
# End: