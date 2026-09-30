# coding: utf-8
"""
    Tests for the tokenizer
    -----------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import os
import sys

import pytest
from tinycss.tokenizer import (
    cython_tokenize_flat, python_tokenize_flat, regroup)


def test_speedups():
    is_pypy = hasattr(sys, 'pypy_translation_info')
    env_skip_tests = os.environ.get('TINYCSS_SKIP_SPEEDUPS_TESTS')
    # pragma: no cover
    if is_pypy or env_skip_tests:
        return
    assert cython_tokenize_flat is not None, (
        'Cython speedups are not installed, related tests will '
        'be skipped. Set the TINYCSS_SKIP_SPEEDUPS_TESTS environment '
        'variable if this is expected.')


@pytest.mark.parametrize(('tokenize', 'css_source', 'expected_tokens'), [
    (tokenize,) + test_data
    for tokenize in (python_tokenize_flat, cython_tokenize_flat)
    for test_data in [
        ('', []),
        ('red -->', [('IDENT', 'red'), ('S', ' '), ('CDC', '-->')]),
        # Longest match rule: no CDC
        ('red-->', [('IDENT', 'red--'), ('DELIM', '>')]),
        (r'p[example="foo(int x) {    this.x = x;}"]', [
            ('IDENT', 'p'),
            ('[', '['),
            ('IDENT', 'example'),
            ('DELIM', '='),
            ('STRING', 'foo(int x) {    this.x = x;}'),
            (']', ']')]),

        # Numbers are parsed
        ('42 .5 -4pX 1.25em 30%', [
            ('INTEGER', 42), ('S', ' '),
            ('NUMBER', .5), ('S', ' '),
            # units are normalized to lower-case:
            ('DIMENSION', -4, 'px'), ('S', ' '),
            ('DIMENSION', 1.25, 'em'), ('S', ' '),
            ('PERCENTAGE', 30, '%')]),

        # URLs are extracted
        ('url(foo.png)', [('URI', 'foo.png')]),
        ('url("foo.png")', [('URI', 'foo.png')]),

        # Escaping

        (r'/* Comment with a \ backslash */', [
            ('COMMENT', '/* Comment with a \ backslash */')]),  # Unchanged

        # backslash followed by a newline in a string: ignored
        ('"Lorem\\\nIpsum"', [('STRING', 'LoremIpsum')]),

        # backslash followed by a newline outside a string: stands for itself
        ('Lorem\\\nIpsum', [
            ('IDENT', 'Lorem'), ('DELIM', '\\'),
            ('S', '\n'), ('IDENT', 'Ipsum')]),

        # Cancel the meaning of special characters
        (r'"Lore\m Ipsum"', [('STRING', 'Lorem Ipsum')]),  # or not specal
        (r'"Lorem \49psum"', [('STRING', 'Lorem Ipsum')]),
        (r'"Lorem \49 psum"', [('STRING', 'Lorem Ipsum')]),
        (r'"Lorem\"Ipsum"', [('STRING', 'Lorem"Ipsum')]),
        (r'"Lorem\\Ipsum"', [('STRING', r'Lorem\Ipsum')]),
        (r'"Lorem\5c Ipsum"', [('STRING', r'Lorem\Ipsum')]),
        (r'Lorem\+Ipsum', [('IDENT', 'Lorem+Ipsum')]),
        (r'Lorem+Ipsum', [
            ('IDENT', 'Lorem'), ('DELIM', '+'), ('IDENT', 'Ipsum')]),
        (r'url(foo\).png)', [('URI', 'foo).png')]),

        # Unicode and backslash escaping
        ('\\26 B', [('IDENT', '&B')]),
        ('\\&B', [('IDENT', '&B')]),
        ('@\\26\tB', [('ATKEYWORD', '@&B')]),
        ('@\\&B', [('ATKEYWORD', '@&B')]),
        ('#\\26\nB', [('HASH', '#&B')]),
        ('#\\&B', [('HASH', '#&B')]),
        ('\\26\r\nB(', [('FUNCTION', '&B(')]),
        ('\\&B(', [('FUNCTION', '&B(')]),
        (r'12.5\000026B', [('DIMENSION', 12.5, '&b')]),
        (r'12.5\0000263B', [('DIMENSION', 12.5, '&3b')]),  # max 6 digits
        (r'12.5\&B', [('DIMENSION', 12.5, '&b')]),
        (r'"\26 B"', [('STRING', '&B')]),
        (r"'\000026B'", [('STRING', '&B')]),
        (r'"\&B"', [('STRING', '&B')]),
        (r'url("\26 B")', [('URI', '&B')]),
        (r'url(\26 B)', [('URI', '&B')]),
        (r'url("\&B")', [('URI', '&B')]),
        (r'url(\&B)', [('URI', '&B')]),
        (r'Lorem\110000Ipsum', [('IDENT', 'Lorem\uFFFDIpsum')]),

        # Bad strings

        # String ends at EOF without closing: no error, parsed
        ('"Lorem\\26Ipsum', [('STRING', 'Lorem&Ipsum')]),
        # Unescaped newline: ends the string, error, unparsed
        ('"Lorem\\26Ipsum\n', [
            ('BAD_STRING', r'"Lorem\26Ipsum'), ('S', '\n')]),
        # Tokenization restarts after the newline, so the second " starts
        # a new string (which ends at EOF without errors, as above.)
        ('"Lorem\\26Ipsum\ndolor" sit', [
            ('BAD_STRING', r'"Lorem\26Ipsum'), ('S', '\n'),
            ('IDENT', 'dolor'), ('STRING', ' sit')]),

    ]])
def test_tokens(tokenize, css_source, expected_tokens):
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    sources = [css_source]
    if sys.version_info[0] < 3:
        # On Python 2.x, ASCII-only bytestrings can be used
        # where Unicode is expected.
        sources.append(css_source.encode('ascii'))
    for css_source in sources:
        tokens = tokenize(css_source, ignore_comments=False)
        result = [
            (token.type, token.value) + (
                () if token.unit is None else (token.unit,))
            for token in tokens
        ]
        assert result == expected_tokens


@pytest.mark.parametrize('tokenize', [
    python_tokenize_flat, cython_tokenize_flat])
def test_positions(tokenize):
    """Test the reported line/column position of each token."""
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    css = '/* Lorem\nipsum */\fa {\n    color: red;\tcontent: "dolor\\\fsit" }'
    tokens = tokenize(css, ignore_comments=False)
    result = [(token.type, token.line, token.column) for token in tokens]
    assert result == [
        ('COMMENT', 1, 1), ('S', 2, 9),
        ('IDENT', 3, 1), ('S', 3, 2), ('{', 3, 3),
        ('S', 3, 4), ('IDENT', 4, 5), (':', 4, 10),
        ('S', 4, 11), ('IDENT', 4, 12), (';', 4, 15), ('S', 4, 16),
        ('IDENT', 4, 17), (':', 4, 24), ('S', 4, 25), ('STRING', 4, 26),
        ('S', 5, 5), ('}', 5, 6)]


@pytest.mark.parametrize(('tokenize', 'css_source', 'expected_tokens'), [
    (tokenize,) + test_data
    for tokenize in (python_tokenize_flat, cython_tokenize_flat)
    for test_data in [
        ('', []),
        (r'Lorem\26 "i\psum"4px', [
            ('IDENT', 'Lorem&'), ('STRING', 'ipsum'), ('DIMENSION', 4)]),

        ('not([[lorem]]{ipsum (42)})', [
            ('FUNCTION', 'not', [
                ('[', [
                    ('[', [
                        ('IDENT', 'lorem'),
                    ]),
                ]),
                ('{', [
                    ('IDENT', 'ipsum'),
                    ('S', ' '),
                    ('(', [
                        ('INTEGER', 42),
                    ])
                ])
            ])]),

        # Close everything at EOF, no error
        ('a[b{"d', [
            ('IDENT', 'a'),
            ('[', [
                ('IDENT', 'b'),
                ('{', [
                    ('STRING', 'd'),
                ]),
            ]),
        ]),

        # Any remaining ), ] or } token is a nesting error
        ('a[b{d]e}', [
            ('IDENT', 'a'),
            ('[', [
                ('IDENT', 'b'),
                ('{', [
                    ('IDENT', 'd'),
                    (']', ']'),  # The error is visible here
                    ('IDENT', 'e'),
                ]),
            ]),
        ]),
        # ref:
        ('a[b{d}e]', [
            ('IDENT', 'a'),
            ('[', [
                ('IDENT', 'b'),
                ('{', [
                    ('IDENT', 'd'),
                ]),
                ('IDENT', 'e'),
            ]),
        ]),
    ]])
def test_token_grouping(tokenize, css_source, expected_tokens):
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    tokens = regroup(tokenize(css_source, ignore_comments=False))
    result = list(jsonify(tokens))
    assert result == expected_tokens


def jsonify(tokens):
    """Turn tokens into "JSON-compatible" data structures."""
    for token in tokens:
        if token.type == 'FUNCTION':
            yield (token.type, token.function_name,
                   list(jsonify(token.content)))
        elif token.is_container:
            yield token.type, list(jsonify(token.content))
        else:
            yield token.type, token.value


@pytest.mark.parametrize(('tokenize', 'ignore_comments', 'expected_tokens'), [
    (tokenize,) + test_data
    for tokenize in (python_tokenize_flat, cython_tokenize_flat)
    for test_data in [
        (False, [
            ('COMMENT', '/* lorem */'),
            ('S', ' '),
            ('IDENT', 'ipsum'),
            ('[', [
                ('IDENT', 'dolor'),
                ('COMMENT', '/* sit */'),
            ]),
            ('BAD_COMMENT', '/* amet')
        ]),
        (True, [
            ('S', ' '),
            ('IDENT', 'ipsum'),
            ('[', [
                ('IDENT', 'dolor'),
            ]),
        ]),
    ]])
def test_comments(tokenize, ignore_comments, expected_tokens):
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    css_source = '/* lorem */ ipsum[dolor/* sit */]/* amet'
    tokens = regroup(tokenize(css_source, ignore_comments))
    result = list(jsonify(tokens))
    assert result == expected_tokens


@pytest.mark.parametrize(('tokenize', 'css_source'), [
    (tokenize, test_data)
    for tokenize in (python_tokenize_flat, cython_tokenize_flat)
    for test_data in [
        r'p[example="foo(int x) {    this.x = x;}"]',
        '"Lorem\\26Ipsum\ndolor" sit',
        '/* Lorem\nipsum */\fa {\n    color: red;\tcontent: "dolor\\\fsit" }',
        'not([[lorem]]{ipsum (42)})',
        'a[b{d]e}',
        'a[b{"d',
    ]])
def test_token_serialize_css(tokenize, css_source):
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    for _regroup in [regroup, lambda x: x]:
        tokens = _regroup(tokenize(css_source, ignore_comments=False))
        result = ''.join(token.as_css() for token in tokens)
        assert result == css_source


@pytest.mark.parametrize(('tokenize', 'css_source'), [
    (tokenize, test_data)
    for tokenize in (python_tokenize_flat, cython_tokenize_flat)
    for test_data in [
        '(8, foo, [z])', '[8, foo, (z)]', '{8, foo, [z]}', 'func(8, foo, [z])'
    ]
])
def test_token_api(tokenize, css_source):
    if tokenize is None:  # pragma: no cover
        pytest.skip('Speedups not available')
    tokens = list(regroup(tokenize(css_source)))
    assert len(tokens) == 1
    token = tokens[0]
    expected_len = 7  # 2 spaces, 2 commas, 3 others.
    assert len(token.content) == expected_len
