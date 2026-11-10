# coding: utf-8
"""
    Test suite for tinycss
    ----------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import sys


# Awful workaround to fix isort's "sys.setdefaultencoding('utf-8')".
if sys.version_info[0] == 2:
    reload(sys)  # noqa
    sys.setdefaultencoding('ascii')


def assert_errors(errors, expected_errors):
    """Test not complete error messages but only substrings."""
    assert len(errors) == len(expected_errors)
    for error, expected in zip(errors, expected_errors):
        assert expected in str(error)
