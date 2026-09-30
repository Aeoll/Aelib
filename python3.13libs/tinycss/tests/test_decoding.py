# coding: utf-8
"""
    Tests for decoding bytes to Unicode
    -----------------------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import pytest
from tinycss.decoding import decode


def params(css, encoding, use_bom=False, expect_error=False, **kwargs):
    """Nicer syntax to make a tuple."""
    return css, encoding, use_bom, expect_error, kwargs


@pytest.mark.parametrize(('css', 'encoding', 'use_bom', 'expect_error',
                          'kwargs'), [
    params('', 'utf8'),  # default to utf8
    params('𐂃', 'utf8'),
    params('é', 'latin1'),  # utf8 fails, fall back on ShiftJIS
    params('£', 'ShiftJIS', expect_error=True),
    params('£', 'ShiftJIS', protocol_encoding='Shift-JIS'),
    params('£', 'ShiftJIS', linking_encoding='Shift-JIS'),
    params('£', 'ShiftJIS', document_encoding='Shift-JIS'),
    params('£', 'ShiftJIS', protocol_encoding='utf8',
           document_encoding='ShiftJIS'),
    params('@charset "utf8"; £', 'ShiftJIS', expect_error=True),
    params('@charset "utf£8"; £', 'ShiftJIS', expect_error=True),
    params('@charset "unknown-encoding"; £', 'ShiftJIS', expect_error=True),
    params('@charset "utf8"; £', 'ShiftJIS', document_encoding='ShiftJIS'),
    params('£', 'ShiftJIS', linking_encoding='utf8',
           document_encoding='ShiftJIS'),
    params('@charset "utf-32"; 𐂃', 'utf-32-be'),
    params('@charset "Shift-JIS"; £', 'ShiftJIS'),
    params('@charset "ISO-8859-8"; £', 'ShiftJIS', expect_error=True),
    params('𐂃', 'utf-16-le', expect_error=True),  # no BOM
    params('𐂃', 'utf-16-le', use_bom=True),
    params('𐂃', 'utf-32-be', expect_error=True),
    params('𐂃', 'utf-32-be', use_bom=True),
    params('𐂃', 'utf-32-be', document_encoding='utf-32-be'),
    params('𐂃', 'utf-32-be', linking_encoding='utf-32-be'),
    params('@charset "utf-32-le"; 𐂃', 'utf-32-be',
           use_bom=True, expect_error=True),
    # protocol_encoding takes precedence over @charset
    params('@charset "ISO-8859-8"; £', 'ShiftJIS',
           protocol_encoding='Shift-JIS'),
    params('@charset "unknown-encoding"; £', 'ShiftJIS',
           protocol_encoding='Shift-JIS'),
    params('@charset "Shift-JIS"; £', 'ShiftJIS',
           protocol_encoding='utf8'),
    # @charset takes precedence over document_encoding
    params('@charset "Shift-JIS"; £', 'ShiftJIS',
           document_encoding='ISO-8859-8'),
    # @charset takes precedence over linking_encoding
    params('@charset "Shift-JIS"; £', 'ShiftJIS',
           linking_encoding='ISO-8859-8'),
    # linking_encoding takes precedence over document_encoding
    params('£', 'ShiftJIS',
           linking_encoding='Shift-JIS', document_encoding='ISO-8859-8'),
])
def test_decode(css, encoding, use_bom, expect_error, kwargs):
    # Workaround PyPy and CPython 3.0 bug: https://bugs.pypy.org/issue1094
    css = css.encode('utf16').decode('utf16')
    if use_bom:
        source = '\ufeff' + css
    else:
        source = css
    css_bytes = source.encode(encoding)
    result, result_encoding = decode(css_bytes, **kwargs)
    if expect_error:
        assert result != css, 'Unexpected unicode success'
    else:
        assert result == css, 'Unexpected unicode error'
