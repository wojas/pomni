#
# expand_paths.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.utils import expand_path


class ExpandPaths(Filter):

    """Fill out relative paths for src tags (e.g. img src or sound src)."""

    def run(self, text, fact):
        i = text.lower().find("src")
        while i != -1:
            start = text.find("\"", i)
            end = text.find("\"", start+1)
            if end == -1:
                break
            old_path = text[start+1:end]
            text = text[:start+1] + "file:\\\\" + expand_path(old_path) \
                   + text[end:]
            # Since text is always longer now, we can start searching
            # from the previous end tag.
            i = text.lower().find("src", end+1)
        return text
