# coding: utf-8
"""
    Tests for the CSS 2.1 parser
    ----------------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import io
import os
import tempfile

import pytest
from tinycss.css21 import CSS21Parser

from . import assert_errors
from .test_tokenizer import jsonify


def parse_bytes(css_bytes, kwargs):
    return CSS21Parser().parse_stylesheet_bytes(css_bytes, **kwargs)


def parse_bytesio_file(css_bytes, kwargs):
    css_file = io.BytesIO(css_bytes)
    return CSS21Parser().parse_stylesheet_file(css_file, **kwargs)


def parse_filename(css_bytes, kwargs):
    css_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        css_file.write(css_bytes)
        # Windows can not open the filename a second time while
        # it is still open for writing.
        css_file.close()
        return CSS21Parser().parse_stylesheet_file(css_file.name, **kwargs)
    finally:
        os.remove(css_file.name)


@pytest.mark.parametrize(('css_bytes', 'kwargs', 'expected_result', 'parse'), [
    params + (parse,)
    for parse in [parse_bytes, parse_bytesio_file, parse_filename]
    for params in [
        ('@import "é";'.encode('utf8'), {}, 'é'),
        ('@import "é";'.encode('utf16'), {}, 'é'),  # with a BOM
        ('@import "é";'.encode('latin1'), {}, 'é'),
        ('@import "£";'.encode('Shift-JIS'), {}, '\x81\x92'),  # lat1 mojibake
        ('@charset "Shift-JIS";@import "£";'.encode('Shift-JIS'), {}, '£'),
        (' @charset "Shift-JIS";@import "£";'.encode('Shift-JIS'), {},
            '\x81\x92'),
        ('@import "£";'.encode('Shift-JIS'),
            {'document_encoding': 'Shift-JIS'}, '£'),
        ('@import "£";'.encode('Shift-JIS'),
            {'document_encoding': 'utf8'}, '\x81\x92'),
        ('@charset "utf8"; @import "£";'.encode('utf8'),
            {'document_encoding': 'latin1'}, '£'),
        # Mojibake yay!
        (' @charset "utf8"; @import "é";'.encode('utf8'),
            {'document_encoding': 'latin1'}, 'Ã©'),
        ('@import "é";'.encode('utf8'), {'document_encoding': 'latin1'}, 'Ã©'),
    ]
])
def test_bytes(css_bytes, kwargs, expected_result, parse):
    stylesheet = parse(css_bytes, kwargs)
    assert stylesheet.rules[0].at_keyword == '@import'
    assert stylesheet.rules[0].uri == expected_result


@pytest.mark.parametrize(('css_source', 'expected_rules', 'expected_errors'), [
    (' /* hey */\n', 0, []),
    ('foo {}', 1, []),
    ('foo{} @lipsum{} bar{}', 2,
        ['unknown at-rule in stylesheet context: @lipsum']),
    ('@charset "ascii"; foo {}', 1, []),
    (' @charset "ascii"; foo {}', 1, [
        'mis-placed or malformed @charset rule']),
    ('@charset ascii; foo {}', 1, ['mis-placed or malformed @charset rule']),
    ('foo {} @charset "ascii";', 1, ['mis-placed or malformed @charset rule']),
])
def test_at_rules(css_source, expected_rules, expected_errors):
    # Pass 'encoding' to allow @charset
    stylesheet = CSS21Parser().parse_stylesheet(css_source, encoding='utf8')
    assert_errors(stylesheet.errors, expected_errors)
    result = len(stylesheet.rules)
    assert result == expected_rules


@pytest.mark.parametrize(('css_source', 'expected_rules', 'expected_errors'), [
    (' /* hey */\n', [], []),

    ('foo{} /* hey */\n@bar;@baz{}',
        [('foo', []), ('@bar', [], None), ('@baz', [], [])], []),

    ('@import "foo.css"/**/;', [
        ('@import', [('STRING', 'foo.css')], None)], []),

    ('@import "foo.css"/**/', [
        ('@import', [('STRING', 'foo.css')], None)], []),

    ('@import "foo.css', [
        ('@import', [('STRING', 'foo.css')], None)], []),

    ('{}', [], ['empty selector']),

    ('a{b:4}', [('a', [('b', [('INTEGER', 4)])])], []),

    ('@page {\t b: 4; @margin}', [('@page', [], [
        ('S', '\t '), ('IDENT', 'b'), (':', ':'), ('S', ' '), ('INTEGER', 4),
        (';', ';'), ('S', ' '), ('ATKEYWORD', '@margin'),
    ])], []),

    ('foo', [], ['no declaration block found']),

    ('foo @page {} bar {}', [('bar', [])],
        ['unexpected ATKEYWORD token in selector']),

    ('foo { content: "unclosed string;\n color:red; ; margin/**/\n: 2cm; }',
        [('foo', [('margin', [('DIMENSION', 2)])])],
        ['unexpected BAD_STRING token in property value']),

    ('foo { 4px; bar: 12% }',
        [('foo', [('bar', [('PERCENTAGE', 12)])])],
        ['expected a property name, got DIMENSION']),

    ('foo { bar! 3cm auto ; baz: 7px }',
        [('foo', [('baz', [('DIMENSION', 7)])])],
        ["expected ':', got DELIM"]),

    ('foo { bar ; baz: {("}"/* comment */) {0@fizz}} }',
        [('foo', [('baz', [('{', [
            ('(', [('STRING', '}')]), ('S', ' '),
            ('{', [('INTEGER', 0), ('ATKEYWORD', '@fizz')])
        ])])])],
        ["expected ':'"]),

    ('foo { bar: ; baz: not(z) }',
        [('foo', [('baz', [('FUNCTION', 'not', [('IDENT', 'z')])])])],
        ['expected a property value']),

    ('foo { bar: (]) ; baz: U+20 }',
        [('foo', [('baz', [('UNICODE-RANGE', 'U+20')])])],
        ['unmatched ] token in (']),
])
def test_core_parser(css_source, expected_rules, expected_errors):
    class CoreParser(CSS21Parser):
        """A parser that always accepts unparsed at-rules."""
        def parse_at_rule(self, rule, stylesheet_rules, errors, context):
            return rule

    stylesheet = CoreParser().parse_stylesheet(css_source)
    assert_errors(stylesheet.errors, expected_errors)
    result = [
        (rule.at_keyword, list(jsonify(rule.head)),
            list(jsonify(rule.body))
            if rule.body is not None else None)
        if rule.at_keyword else
        (rule.selector.as_css(), [
            (decl.name, list(jsonify(decl.value)))
            for decl in rule.declarations])
        for rule in stylesheet.rules
    ]
    assert result == expected_rules


@pytest.mark.parametrize(('css_source', 'expected_declarations',
                          'expected_errors'), [
    (' /* hey */\n', [], []),

    ('b:4', [('b', [('INTEGER', 4)])], []),

    ('{b:4}', [], ['expected a property name, got {']),

    ('b:4} c:3', [], ['unmatched } token in property value']),

    (' 4px; bar: 12% ',
        [('bar', [('PERCENTAGE', 12)])],
        ['expected a property name, got DIMENSION']),

    ('bar! 3cm auto ; baz: 7px',
        [('baz', [('DIMENSION', 7)])],
        ["expected ':', got DELIM"]),

    ('foo; bar ; baz: {("}"/* comment */) {0@fizz}}',
        [('baz', [('{', [
            ('(', [('STRING', '}')]), ('S', ' '),
            ('{', [('INTEGER', 0), ('ATKEYWORD', '@fizz')])
        ])])],
        ["expected ':'", "expected ':'"]),

    ('bar: ; baz: not(z)',
        [('baz', [('FUNCTION', 'not', [('IDENT', 'z')])])],
        ['expected a property value']),

    ('bar: (]) ; baz: U+20',
        [('baz', [('UNICODE-RANGE', 'U+20')])],
        ['unmatched ] token in (']),
])
def test_parse_style_attr(css_source, expected_declarations, expected_errors):
    declarations, errors = CSS21Parser().parse_style_attr(css_source)
    assert_errors(errors, expected_errors)
    result = [(decl.name, list(jsonify(decl.value)))
              for decl in declarations]
    assert result == expected_declarations


@pytest.mark.parametrize(('css_source', 'expected_declarations',
                          'expected_errors'), [
    (' /* hey */\n', [], []),

    ('a:1; b:2',
        [('a', [('INTEGER', 1)], None), ('b', [('INTEGER', 2)], None)], []),

    ('a:1 important; b: important',
        [('a', [('INTEGER', 1), ('S', ' '), ('IDENT', 'important')], None),
            ('b', [('IDENT', 'important')], None)],
        []),

    ('a:1 !important; b:2',
        [('a', [('INTEGER', 1)], 'important'), ('b', [('INTEGER', 2)], None)],
        []),

    ('a:1!\t Im\\50 O\\RTant; b:2',
        [('a', [('INTEGER', 1)], 'important'), ('b', [('INTEGER', 2)], None)],
        []),

    ('a: !important; b:2',
        [('b', [('INTEGER', 2)], None)],
        ['expected a value before !important']),

])
def test_important(css_source, expected_declarations, expected_errors):
    declarations, errors = CSS21Parser().parse_style_attr(css_source)
    assert_errors(errors, expected_errors)
    result = [(decl.name, list(jsonify(decl.value)), decl.priority)
              for decl in declarations]
    assert result == expected_declarations


@pytest.mark.parametrize(('css_source', 'expected_rules', 'expected_errors'), [
    (' /* hey */\n', [], []),
    ('@import "foo.css";', [('foo.css', ['all'])], []),
    ('@import url(foo.css);', [('foo.css', ['all'])], []),
    ('@import "foo.css" screen, print;',
        [('foo.css', ['screen', 'print'])], []),
    ('@charset "ascii"; @import "foo.css"; @import "bar.css";',
        [('foo.css', ['all']), ('bar.css', ['all'])], []),
    ('foo {} @import "foo.css";',
        [], ['@import rule not allowed after a ruleset']),
    ('@page {} @import "foo.css";',
        [], ['@import rule not allowed after an @page rule']),
    ('@import ;',
        [], ['expected URI or STRING for @import rule']),
    ('@import foo.css;',
        [], ['expected URI or STRING for @import rule, got IDENT']),
    ('@import "foo.css" {}',
        [], ["expected ';', got a block"]),
])
def test_at_import(css_source, expected_rules, expected_errors):
    # Pass 'encoding' to allow @charset
    stylesheet = CSS21Parser().parse_stylesheet(css_source, encoding='utf8')
    assert_errors(stylesheet.errors, expected_errors)

    result = [
        (rule.uri, rule.media)
        for rule in stylesheet.rules
        if rule.at_keyword == '@import'
    ]
    assert result == expected_rules


@pytest.mark.parametrize(('css', 'expected_result', 'expected_errors'), [
    ('@page {}', (None, (0, 0), []), []),
    ('@page:first {}', ('first', (1, 0), []), []),
    ('@page :left{}', ('left', (0, 1), []), []),
    ('@page\t\n:right {}', ('right', (0, 1), []), []),
    ('@page :last {}', None, ['invalid @page selector']),
    ('@page : right {}', None, ['invalid @page selector']),
    ('@page table:left {}', None, ['invalid @page selector']),

    ('@page;', None, ['invalid @page rule: missing block']),
    ('@page { a:1; ; b: 2 }',
        (None, (0, 0), [('a', [('INTEGER', 1)]), ('b', [('INTEGER', 2)])]),
        []),
    ('@page { a:1; c: ; b: 2 }',
        (None, (0, 0), [('a', [('INTEGER', 1)]), ('b', [('INTEGER', 2)])]),
        ['expected a property value']),
    ('@page { a:1; @top-left {} b: 2 }',
        (None, (0, 0), [('a', [('INTEGER', 1)]), ('b', [('INTEGER', 2)])]),
        ['unknown at-rule in @page context: @top-left']),
    ('@page { a:1; @top-left {}; b: 2 }',
        (None, (0, 0), [('a', [('INTEGER', 1)]), ('b', [('INTEGER', 2)])]),
        ['unknown at-rule in @page context: @top-left']),
])
def test_at_page(css, expected_result, expected_errors):
    stylesheet = CSS21Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    if expected_result is None:
        assert not stylesheet.rules
    else:
        assert len(stylesheet.rules) == 1
        rule = stylesheet.rules[0]
        assert rule.at_keyword == '@page'
        assert rule.at_rules == []  # in CSS 2.1
        result = (
            rule.selector,
            rule.specificity,
            [(decl.name, list(jsonify(decl.value)))
                for decl in rule.declarations],
        )
        assert result == expected_result


@pytest.mark.parametrize(('css_source', 'expected_rules', 'expected_errors'), [
    (' /* hey */\n', [], []),
    ('@media all {}', [(['all'], [])], []),
    ('@media screen, print {}', [(['screen', 'print'], [])], []),
    ('@media all;', [], ['invalid @media rule: missing block']),
    ('@media  {}', [], ['expected media types for @media']),
    ('@media 4 {}', [], ['expected a media type, got INTEGER']),
    ('@media , screen {}', [], ['expected a media type']),
    ('@media screen, {}', [], ['expected a media type']),
    ('@media screen print {}', [],
        ['expected a media type, got IDENT, IDENT']),

    ('@media all { @page { a: 1 } @media; @import; foo { a: 1 } }',
        [(['all'], [('foo', [('a', [('INTEGER', 1)])])])],
        ['@page rule not allowed in @media',
         '@media rule not allowed in @media',
         '@import rule not allowed in @media']),

])
def test_at_media(css_source, expected_rules, expected_errors):
    stylesheet = CSS21Parser().parse_stylesheet(css_source)
    assert_errors(stylesheet.errors, expected_errors)

    for rule in stylesheet.rules:
        assert rule.at_keyword == '@media'
    result = [
        (rule.media, [
            (sub_rule.selector.as_css(), [
                (decl.name, list(jsonify(decl.value)))
                for decl in sub_rule.declarations])
            for sub_rule in rule.rules
        ])
        for rule in stylesheet.rules
    ]
    assert result == expected_rules
