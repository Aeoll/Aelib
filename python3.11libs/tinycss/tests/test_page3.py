# coding: utf-8
"""
    Tests for the Paged Media 3 parser
    ----------------------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import pytest
from tinycss.page3 import CSSPage3Parser

from . import assert_errors
from .test_tokenizer import jsonify


@pytest.mark.parametrize(('css', 'expected_selector',
                          'expected_specificity', 'expected_errors'), [
    ('@page {}', (None, None), (0, 0, 0), []),

    ('@page :first {}', (None, 'first'), (0, 1, 0), []),
    ('@page:left{}', (None, 'left'), (0, 0, 1), []),
    ('@page :right {}', (None, 'right'), (0, 0, 1), []),
    ('@page  :blank{}', (None, 'blank'), (0, 1, 0), []),
    ('@page :last {}', None, None, ['invalid @page selector']),
    ('@page : first {}', None, None, ['invalid @page selector']),

    ('@page foo:first {}', ('foo', 'first'), (1, 1, 0), []),
    ('@page bar :left {}', ('bar', 'left'), (1, 0, 1), []),
    (r'@page \26:right {}', ('&', 'right'), (1, 0, 1), []),

    ('@page foo {}', ('foo', None), (1, 0, 0), []),
    (r'@page \26 {}', ('&', None), (1, 0, 0), []),

    ('@page foo fist {}', None, None, ['invalid @page selector']),
    ('@page foo, bar {}', None, None, ['invalid @page selector']),
    ('@page foo&first {}', None, None, ['invalid @page selector']),
])
def test_selectors(css, expected_selector, expected_specificity,
                   expected_errors):
    stylesheet = CSSPage3Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    if stylesheet.rules:
        assert len(stylesheet.rules) == 1
        rule = stylesheet.rules[0]
        assert rule.at_keyword == '@page'
        selector = rule.selector
        assert rule.specificity == expected_specificity
    else:
        selector = None
    assert selector == expected_selector


@pytest.mark.parametrize(('css', 'expected_declarations',
                          'expected_rules', 'expected_errors'), [
    ('@page {}', [], [], []),
    ('@page { foo: 4; bar: z }',
        [('foo', [('INTEGER', 4)]), ('bar', [('IDENT', 'z')])], [], []),
    ('''@page { foo: 4;
                @top-center { content: "Awesome Title" }
                @bottom-left { content: counter(page) }
                bar: z
        }''',
        [('foo', [('INTEGER', 4)]), ('bar', [('IDENT', 'z')])],
        [('@top-center', [('content', [('STRING', 'Awesome Title')])]),
         ('@bottom-left', [('content', [
             ('FUNCTION', 'counter', [('IDENT', 'page')])])])],
        []),
    ('''@page { foo: 4;
                @bottom-top { content: counter(page) }
                bar: z
        }''',
        [('foo', [('INTEGER', 4)]), ('bar', [('IDENT', 'z')])],
        [],
        ['unknown at-rule in @page context: @bottom-top']),

    ('@page{} @top-right{}', [], [], [
        '@top-right rule not allowed in stylesheet']),
    ('@page{ @top-right 4 {} }', [], [], [
        'unexpected INTEGER token in @top-right rule header']),
    # Not much error recovery tests here. This should be covered in test_css21
])
def test_content(css, expected_declarations, expected_rules, expected_errors):
    stylesheet = CSSPage3Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    def declarations(rule):
        return [(decl.name, list(jsonify(decl.value)))
                for decl in rule.declarations]

    assert len(stylesheet.rules) == 1
    rule = stylesheet.rules[0]
    assert rule.at_keyword == '@page'
    assert declarations(rule) == expected_declarations
    rules = [(margin_rule.at_keyword, declarations(margin_rule))
             for margin_rule in rule.at_rules]
    assert rules == expected_rules
