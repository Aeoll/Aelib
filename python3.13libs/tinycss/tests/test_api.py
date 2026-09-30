# coding: utf-8
"""
    Tests for the public API
    ------------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

from pytest import raises
from tinycss import make_parser
from tinycss.page3 import CSSPage3Parser


def test_make_parser():
    class MyParser(object):
        def __init__(self, some_config):
            self.some_config = some_config

    parsers = [
        make_parser(),
        make_parser('page3'),
        make_parser(CSSPage3Parser),
        make_parser(MyParser, some_config=42),
        make_parser(CSSPage3Parser, MyParser, some_config=42),
        make_parser(MyParser, 'page3', some_config=42),
    ]

    for parser, exp in zip(parsers, [False, True, True, False, True, True]):
        assert isinstance(parser, CSSPage3Parser) == exp

    for parser, exp in zip(parsers, [False, False, False, True, True, True]):
        assert isinstance(parser, MyParser) == exp

    for parser in parsers[3:]:
        assert parser.some_config == 42

    # Extra or missing named parameters
    raises(TypeError, make_parser, some_config=4)
    raises(TypeError, make_parser, 'page3', some_config=4)
    raises(TypeError, make_parser, MyParser)
    raises(TypeError, make_parser, MyParser, some_config=4, other_config=7)
