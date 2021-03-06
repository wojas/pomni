#
# configuration.py <Peter.Bienstman@UGent.be>
#

import random
import os
import sys
import cPickle
import locale

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.exceptions import ConfigError, SaveError

config_py = \
"""# Mnemosyne configuration file.

# Upload server. Only change when prompted by the developers.
upload_server = "mnemosyne-proj.dyndns.org:80"

# Set to True to prevent you from accidentally revealing the answer
# when clicking the edit button.
only_editable_when_answer_shown = False

# The number of daily backups to keep. Set to -1 for no limit.
backups_to_keep = 5

# The moment the new day starts. Defaults to 3 am. Could be useful to
# change if you are a night bird. You can only set the hours, not
# minutes, and midnight corresponds to 0.
day_starts_at = 3

# Latex preamble. Note that for the pre- and postamble you need to
# use double slashes instead of single slashes here, to have them
# escaped when Python reads them in.
latex_preamble = \"\"\"\\\\documentclass[12pt]{article}
\\\\pagestyle{empty}
\\\\begin{document}\"\"\"

# Latex postamble.
latex_postamble = "\\\\end{document}"

# Latex command.
latex = "latex -interaction=nonstopmode"

# Latex dvipng command.
dvipng = "dvipng -D 200 -T tight tmp.dvi"

# path to default theme
theme_path = "/usr/share/pomni/hildon-UI/eternal"
"""

class Configuration(dict, Component):

    def set_defaults(self):
        
        """Fill the config with default values.  Is called after every load,
        since a new version of Mnemosyne might have introduced new keys."""

        for key, value in \
            {"first_run": True, 
             "path": "default.mem",
             "import_dir": self.basedir, 
             "import_format": "XML",
             "reset_learning_data_import": False,
             "export_dir": self.basedir,
             "export_format": "XML", 
             "reset_learning_data_export": False,
             "import_img_dir": self.basedir, 
             "import_sound_dir": self.basedir,
             "user_id": md5(str(random.random())).hexdigest()[0:8],
             "upload_logs": True, 
             "upload_server": "mnemosyne-proj.dyndns.org:80",
             "log_index": 1, 
             "QA_font": None,
             "list_font": None,
             "grade_0_items_at_once": 5,
             "randomise_new_cards": False,
             "last_add_vice_versa": False,
             "last_add_category": "<default>",
             "sort_column": None,
             "sort_order": None,
             "show_intervals": "never",
             "only_editable_when_answer_shown": False,
             "locale": None,
             "show_daily_tips": True,
             "tip": 0,
             "backups_to_keep": 5,
             "day_starts_at": 3, 
             "latex_preamble": "\\documentclass[12pt]{article}\n"+
                              "\\pagestyle{empty}\n\\begin{document}",
             "latex_postamble": "\\end{document}", 
             "latex": "latex -interaction=nonstopmode",
             "dvipng": "dvipng -D 200 -T tight tmp.dvi",
             "theme_path": "/usr/share/pomni/hildon-UI/eternal"
            }.items():
            
            self.setdefault(key, value)

    def load(self):
        try:
            config_file = file(os.path.join(self.basedir, "config"), 'rb')
            for key, value in cPickle.load(config_file).iteritems():
                self[key] = value
            self.set_defaults()
        except:
            raise ConfigError(stack_trace=True)

    def save(self):
        try:
            config_file = file(os.path.join(self.basedir, "config"), 'wb')
            cPickle.dump(self, config_file)
        except:
            raise SaveError
            
    def initialise(self, basedir=None):
        
        """Typical initialisation sequence. Custom applications can modify this
        as needed.
        
        """
        
        self.determine_basedir(basedir)
        self.fill_basedir()
        self.load()
        self.load_user_config()
        self.correct_config()

    def determine_basedir(self, basedir):
        self.old_basedir = None
        if basedir == None:
            home = os.path.expanduser("~")
            try:
                home = home.decode(locale.getdefaultlocale()[1])
            except:
                pass
            if sys.platform == "darwin":
                self.old_basedir = os.path.join(home, ".mnemosyne")
                self.basedir = os.path.join(home, "Library", "Mnemosyne")
                if not os.path.exists(self.basedir) \
                   and os.path.exists(self.old_basedir):
                    self.migrate_basedir(self.old_basedir, self.basedir)
            else:
                self.basedir = os.path.join(home, ".mnemosyne")
        else:
            self.basedir = basedir
            

    def fill_basedir(self):
        
        """ Fill basedir with configuration files. Do this even if basedir
        already exists, because we might have added new files since the
        last version.
        
        """
        
        # Create paths.
        if not os.path.exists(self.basedir):
            os.mkdir(self.basedir)
        for directory in ["history", "latex", "css", "plugins", \
                          "backups", "sessions"]:
            if not os.path.exists(os.path.join(self.basedir, directory)):
                os.mkdir(os.path.join(self.basedir, directory))
        # Create default configuration.
        if not os.path.exists(os.path.join(self.basedir, "config")):
            self.save()
        # Create default config.py.
        configfile = os.path.join(self.basedir, "config.py")
        if not os.path.exists(configfile):
            f = file(configfile, 'w')
            print >> f, config_py
            f.close()

    def load_user_config(self):
        sys.path.insert(0, self.basedir)
        config_file_c = os.path.join(self.basedir, "config.pyc")
        if os.path.exists(config_file_c):
            os.remove(config_file_c)
        config_file = os.path.join(self.basedir, "config.py")
        if os.path.exists(config_file):
            try:
                import config as user_config
                for var in dir(user_config):
                    if var in self:
                        self[var] = getattr(user_config, var)
            except:
                # Work around the unexplained fact that config.py cannot get 
                # imported right after it has been created.
                if self["first_run"] == True:
                    pass
                else:
                    raise ConfigError(stack_trace=True)
                
    def correct_config(self):
        # Update paths if the location has migrated.
        if self.old_basedir:
            for key in ["import_dir", "export_dir", "import_img_dir",
                        "import_sound_dir"]:
                if self[key] == self.old_basedir:
                    self[key] = self.basedir
        # Recreate user id and log index from history folder in case the
        # config file was accidentally deleted.
        if self["log_index"] == 1:
            _dir = os.listdir(unicode(os.path.join(self.basedir, "history")))
            history_files = [x for x in _dir if x[-4:] == ".bz2"]
            history_files.sort()
            if history_files:
                last = history_files[-1]
                user, index = last.split('_')
                index = int(index.split('.')[0]) + 1

    def migrate_basedir(self, old, new):
        if os.path.islink(self.old_basedir):
            print "Not migrating %s to %s because " % (old, new) \
                    + "it is a symlink."
            return
        # Migrate Mnemosyne basedir to new location and create a symlink from
        # the old one. The other way around is a bad idea, because a user
        # might decide to clean up the old obsolete directory, not realising
        # the new one is a symlink.
        print "Migrating %s to %s" % (old, new)
        try:
            os.rename(old, new)
        except OSError:
            print "Move failed, manual migration required."
            return
        # Now create a symlink for backwards compatibility.
        try:
            os.symlink(new, old)
        except OSError:
            print "Backwards compatibility symlink creation failed."
