# coding: utf-8
"""
    Tests for the Fonts 3 parser
    ----------------------------

    :copyright: (c) 2016 by Kozea.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import pytest
from tinycss.fonts3 import CSSFonts3Parser

from . import assert_errors
from .test_tokenizer import jsonify


@pytest.mark.parametrize(('css', 'expected_family_names', 'expected_errors'), [
    ('@font-feature-values foo {}', ('foo',), []),
    ('@font-feature-values Foo Test {}', ('Foo Test',), []),
    ('@font-feature-values \'Foo Test\' {}', ('Foo Test',), []),
    ('@font-feature-values Foo Test, Foo Lol, "Foo tooo"', (
        'Foo Test', 'Foo Lol', 'Foo tooo'), []),
    ('@font-feature-values Foo    , Foo    lol   {}', ('Foo', 'Foo lol'), []),
    ('@font-feature-values Foo , "Foobar" , Lol   {}', (
        'Foo', 'Foobar', 'Lol'), []),
    ('@font-feature-values Foo, {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values ,Foo {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values Test,"Foo", {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values Test "Foo" {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values Test Foo, Test "bar", "foo" {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values Test/Foo {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values /Foo {}', None, [
        'invalid @font-feature-values selector']),
    ('@font-feature-values #Foo {}', None, [
        'invalid @font-feature-values selector']),
    # TODO: this currently works but should not work
    # ('@font-feature-values test@foo {}', None, [
    #     'invalid @font-feature-values selector']),
    ('@font-feature-values Hawaii 5-0 {}', None, [
        'invalid @font-feature-values selector']),
])
def test_font_feature_values_selectors(css, expected_family_names,
                                       expected_errors):
    stylesheet = CSSFonts3Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    if stylesheet.rules:
        assert len(stylesheet.rules) == 1
        rule = stylesheet.rules[0]
        assert rule.at_keyword == '@font-feature-values'
        assert rule.family_names == expected_family_names


@pytest.mark.parametrize(('css', 'expected_declarations', 'expected_errors'), [
    ('@font-face {}', [], []),
    ('@font-face test { src: "lol"; font-family: "bar" }', None, [
        'unexpected IDENT token in @font-face rule header']),
    ('@font-face { src: "lol"; font-family: "bar" }', [
        ('src', [('STRING', 'lol')]),
        ('font-family', [('STRING', 'bar')])], []),
    ('@font-face { src: "lol"; font-family: "bar"; src: "baz" }', [
        ('src', [('STRING', 'lol')]),
        ('font-family', [('STRING', 'bar')]),
        ('src', [('STRING', 'baz')])], []),
])
def test_font_face_content(css, expected_declarations, expected_errors):
    stylesheet = CSSFonts3Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    def declarations(rule):
        return [(decl.name, list(jsonify(decl.value)))
                for decl in rule.declarations]

    if expected_declarations is None:
        assert stylesheet.rules == []
        assert expected_errors
    else:
        assert len(stylesheet.rules) == 1
        rule = stylesheet.rules[0]
        assert rule.at_keyword == '@font-face'
        assert declarations(rule) == expected_declarations


@pytest.mark.parametrize(
    ('css', 'expected_rules', 'expected_errors'), [
        ('''@annotation{}''', None, [
            '@annotation rule not allowed in stylesheet']),
        ('''@font-feature-values foo {}''', None, []),
        ('''@font-feature-values foo {
                @swash { ornate: 1; }
                @styleset { double-W: 14; sharp-terminals: 16 1; }
        }''', [
            ('@swash', [('ornate', [('INTEGER', 1)])]),
            ('@styleset', [
                ('double-w', [('INTEGER', 14)]),
                ('sharp-terminals', [
                    ('INTEGER', 16), ('S', ' '), ('INTEGER', 1)])])], []),
        ('''@font-feature-values foo {
                @swash { ornate: 14; }
                @unknown { test: 1; }
        }''', [('@swash', [('ornate', [('INTEGER', 14)])])], [
            'unknown at-rule in @font-feature-values context: @unknown']),
        ('''@font-feature-values foo {
                @annotation{boxed:1}
                bad: 2;
                @brokenstylesetbecauseofbadabove  { sharp: 1}
                @styleset  { sharp-terminals: 16 1; @bad {}}
                @styleset  { @bad {} top-ignored: 3; top: 9000}
                really-bad
        }''', [
            ('@annotation', [('boxed', [('INTEGER', 1)])]),
            ('@styleset', [
                ('sharp-terminals', [
                    ('INTEGER', 16), ('S', ' '), ('INTEGER', 1)])]),
            ('@styleset', [('top', [('INTEGER', 9000)])])], [
                'unexpected ; token in selector',
                'expected a property name, got ATKEYWORD',
                'expected a property name, got ATKEYWORD',
                'no declaration block found for ruleset']),
    ])
def test_font_feature_values_content(css, expected_rules, expected_errors):
    stylesheet = CSSFonts3Parser().parse_stylesheet(css)
    assert_errors(stylesheet.errors, expected_errors)

    if expected_rules is not None:
        assert len(stylesheet.rules) == 1
        rule = stylesheet.rules[0]
        assert rule.at_keyword == '@font-feature-values'

        rules = [
            (at_rule.at_keyword, [
                (decl.name, list(jsonify(decl.value)))
                for decl in at_rule.declarations])
            for at_rule in rule.at_rules] if rule.at_rules else None
        assert rules == expected_rules
