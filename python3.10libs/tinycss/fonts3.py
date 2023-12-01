# coding: utf-8
"""
    tinycss.colors3
    ---------------

    Parser for CSS 3 Fonts syntax:
    https://www.w3.org/TR/css-fonts-3/

    Adds support for font-face and font-feature-values rules.

    :copyright: (c) 2016 by Kozea.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import division, unicode_literals

from .css21 import CSS21Parser, ParseError


class FontFaceRule(object):
    """A parsed at-rule for font faces.

    .. attribute:: at_keyword

        Always ``'@font-face'``.

    .. attribute:: declarations

        A list of :class:`~.css21.Declaration` objects.

    .. attribute:: line

        Source line where this was read.

    .. attribute:: column

        Source column where this was read.

    """

    def __init__(self, at_keyword, declarations, line, column):
        assert at_keyword == '@font-face'
        self.at_keyword = at_keyword
        self.declarations = declarations
        self.line = line
        self.column = column


class FontFeatureValuesRule(object):
    """A parsed at-rule for font feature values.

    .. attribute:: at_keyword

        Always ``'@font-feature-values'``.

    .. attribute:: line

        Source line where this was read.

    .. attribute:: column

        Source column where this was read.

    .. attribute:: at_rules

        The list of parsed at-rules inside the @font-feature-values block, in
        source order.

    .. attribute:: family_names

        A list of strings representing font families.

    """

    def __init__(self, at_keyword, at_rules, family_names, line, column):
        assert at_keyword == '@font-feature-values'
        self.at_keyword = at_keyword
        self.family_names = family_names
        self.at_rules = at_rules
        self.line = line
        self.column = column


class FontFeatureRule(object):
    """A parsed at-rule for font features.

    .. attribute:: at_keyword

        One of the 16 following strings:

        * ``@stylistic``
        * ``@styleset``
        * ``@character-variant``
        * ``@swash``
        * ``@ornaments``
        * ``@annotation``

    .. attribute:: declarations

        A list of :class:`~.css21.Declaration` objects.

    .. attribute:: line

        Source line where this was read.

    .. attribute:: column

        Source column where this was read.

    """

    def __init__(self, at_keyword, declarations, line, column):
        self.at_keyword = at_keyword
        self.declarations = declarations
        self.line = line
        self.column = column


class CSSFonts3Parser(CSS21Parser):
    """Extend :class:`~.css21.CSS21Parser` for `CSS 3 Fonts`_ syntax.

    .. _CSS 3 Fonts: https://www.w3.org/TR/css-fonts-3/

    """

    FONT_FEATURE_VALUES_AT_KEYWORDS = [
        '@stylistic',
        '@styleset',
        '@character-variant',
        '@swash',
        '@ornaments',
        '@annotation',
    ]

    def parse_at_rule(self, rule, previous_rules, errors, context):
        if rule.at_keyword == '@font-face':
            if rule.head:
                raise ParseError(
                    rule.head[0],
                    'unexpected {0} token in {1} rule header'.format(
                        rule.head[0].type, rule.at_keyword))
            declarations, body_errors = self.parse_declaration_list(rule.body)
            errors.extend(body_errors)
            return FontFaceRule(
                rule.at_keyword, declarations, rule.line, rule.column)
        elif rule.at_keyword == '@font-feature-values':
            family_names = tuple(
                self.parse_font_feature_values_family_names(rule.head))
            at_rules, body_errors = (
                self.parse_rules(rule.body or [], '@font-feature-values'))
            errors.extend(body_errors)
            return FontFeatureValuesRule(
                rule.at_keyword, at_rules, family_names,
                rule.line, rule.column)
        elif rule.at_keyword in self.FONT_FEATURE_VALUES_AT_KEYWORDS:
            if context != '@font-feature-values':
                raise ParseError(
                    rule, '{0} rule not allowed in {1}'.format(
                        rule.at_keyword, context))
            declarations, body_errors = self.parse_declaration_list(rule.body)
            errors.extend(body_errors)
            return FontFeatureRule(
                rule.at_keyword, declarations, rule.line, rule.column)
        return super(CSSFonts3Parser, self).parse_at_rule(
            rule, previous_rules, errors, context)

    def parse_font_feature_values_family_names(self, tokens):
        """Parse an @font-feature-values selector.

        :param tokens:
            An iterable of token, typically from the  ``head`` attribute of
            an unparsed :class:`AtRule`.
        :returns:
            A generator of strings representing font families.
        :raises:
            :class:`~.parsing.ParseError` on invalid selectors

        """
        family = ''
        current_string = False
        for token in tokens:
            if token.type == 'DELIM' and token.value == ',' and family:
                yield family
                family = ''
                current_string = False
            elif token.type == 'STRING' and not family and (
                    current_string is False):
                family = token.value
                current_string = True
            elif token.type == 'IDENT' and not current_string:
                if family:
                    family += ' '
                family += token.value
            elif token.type != 'S':
                family = ''
                break
        if family:
            yield family
        else:
            raise ParseError(token, 'invalid @font-feature-values selector')
