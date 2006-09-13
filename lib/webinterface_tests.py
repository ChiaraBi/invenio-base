## $Id$
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.  
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Unit tests for the webinterface module."""

__revision__ = "$Id$"

import unittest, sys, cgi

# SLIPPERY SLOPE AHEAD
#
# Trick mod_python into believing there is already an _apache module
# available, which is used only for its parse_qs functions anyway.
#
# This must be done early, as many imports somehow end up importing
# apache in turn, which makes the trick useless.

class _FakeApache(object):

    SERVER_RETURN = 'RETURN'
    
    def __init__(self):
        self.table = None
        self.log_error = None
        self.table = None
        self.config_tree = None
        self.server_root = None
        self.mpm_query = None

    def parse_qs(self, *args, **kargs):
        return cgi.parse_qs(*args, **kargs)

    def parse_qsl(self, *args, **kargs):
        return cgi.parse_qsl(*args, **kargs)

class _FakeReq(object):

    def __init__(self, q):
        self.args = q
        self.method = "GET"
        return

_current_module = sys.modules.get('mod_python._apache')

sys.modules['mod_python._apache'] = _FakeApache()

from mod_python.util import FieldStorage

if _current_module:
    sys.modules['mod_python._apache'] = _current_module
else:
    del sys.modules['mod_python._apache']


# --------------------------------------------------

from invenio import webinterface_handler
from invenio.config import cdslang


class TestWashArgs(unittest.TestCase):
    """webinterface - Test for washing of URL query arguments"""

    def _check(self, query, default, expected):
        req = _FakeReq(query)
        form = FieldStorage(req, keep_blank_values=True)
        result = webinterface_handler.wash_urlargd(form, default)

        if not 'ln' in expected:
            expected['ln'] = cdslang
            
        self.failUnlessEqual(result, expected)

    def test_single_string(self):
        """ webinterface - check retrieval of a single string field """

        default = {'c': (str, 'default')}
        
        self._check('c=Test1', default, {'c': 'Test1'})
        self._check('d=Test1', default, {'c': 'default'})
        self._check('c=Test1&c=Test2', default, {'c': 'Test1'})

    def test_string_list(self):
        """ webinterface - check retrieval of a list of values """

        default = {'c': (list, ['default'])}
        
        self._check('c=Test1', default, {'c': ['Test1']})
        self._check('c=Test1&c=Test2', default, {'c': ['Test1', 'Test2']})
        self._check('d=Test1', default, {'c': ['default']})

    def test_int_casting(self):
        """ webinterface - check casting into an int. """

        default = {'jrec': (int, -1)}
        
        self._check('jrec=12', default, {'jrec': 12})
        self._check('jrec=', default, {'jrec': -1})
        self._check('jrec=foo', default, {'jrec': -1})
        self._check('jrec=foo&jrec=1', default, {'jrec': -1})
        self._check('jrec=12&jrec=foo', default, {'jrec': 12})


def create_test_suite():
    """Return test suite for the search engine."""
    return unittest.TestSuite((unittest.makeSuite(TestWashArgs),))

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(create_test_suite())
