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

__version__ = "$Id$"

import unittest, sys, cgi

from invenio import webinterface_handler
from invenio.config import cdslang

# Trick mod_python into believing there is already an _apache module
# available, which is used only for its parse_qs functions anyway.
class _FakeApache(object):

    def parse_qs(self, *args, **kargs):
        return cgi.parse_qs(*args, **kargs)

    def parse_qsl(self, *args, **kargs):
        return cgi.parse_qsl(*args, **kargs)

class _FakeReq(object):

    def __init__(self, q):
        self.args = q
        self.method = "GET"
        return

_current_module = sys.modules.get('_apache')

sys.modules['_apache'] = _FakeApache()
from mod_python.util import FieldStorage

if _current_module:
    sys.modules['_apache'] = _current_module
else:
    del sys.modules['_apache']


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
        
        self._check('c=Invenio', default, {'c': 'Invenio'})
        self._check('d=Invenio', default, {'c': 'default'})
        self._check('c=Invenio&c=CDSware', default, {'c': 'Invenio'})

    def test_string_list(self):
        """ webinterface - check retrieval of a list of values """

        default = {'c': (list, ['default'])}
        
        self._check('c=Invenio', default, {'c': ['Invenio']})
        self._check('c=Invenio&c=CDSware', default, {'c': ['Invenio', 'CDSware']})
        self._check('d=Invenio', default, {'c': ['default']})

    def test_int_casting(self):
        """ webinterface - check casting into an int. """

        default = {'jrec': (int, -1)}
        
        self._check('jrec=12', default, {'jrec': 12})
        self._check('jrec=', default, {'jrec': -1})
        self._check('jrec=toto', default, {'jrec': -1})
        self._check('jrec=toto&jrec=1', default, {'jrec': -1})
        self._check('jrec=12&jrec=toto', default, {'jrec': 12})


def create_test_suite():
    """Return test suite for the search engine."""
    return unittest.TestSuite((unittest.makeSuite(TestWashArgs),))

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(create_test_suite())
