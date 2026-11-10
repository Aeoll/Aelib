# coding: utf-8
"""
    Speed tests
    -----------

    Note: this file is not named test_*.py as it is not part of the
    test suite ran by pytest.

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import division, unicode_literals

import contextlib
import functools
import os.path
import sys
import timeit

from cssutils import parseString

from .. import tokenizer
from ..css21 import CSS21Parser
from ..parsing import remove_whitespace

CSS_REPEAT = 4
TIMEIT_REPEAT = 3
TIMEIT_NUMBER = 20


def load_css():
    filename = os.path.join(os.path.dirname(__file__),
                            '..', '..', 'docs', '_static', 'custom.css')
    with open(filename, 'rb') as fd:
        return b'\n'.join([fd.read()] * CSS_REPEAT)


# Pre-load so that I/O is not measured
CSS = load_css()


@contextlib.contextmanager
def install_tokenizer(name):
    original = tokenizer.tokenize_flat
    try:
        tokenizer.tokenize_flat = getattr(tokenizer, name)
        yield
    finally:
        tokenizer.tokenize_flat = original


def parse(tokenizer_name):
    with install_tokenizer(tokenizer_name):
        stylesheet = CSS21Parser().parse_stylesheet_bytes(CSS)
    result = []
    for rule in stylesheet.rules:
        selector = rule.selector.as_css()
        declarations = [
            (declaration.name, len(list(remove_whitespace(declaration.value))))
            for declaration in rule.declarations]
        result.append((selector, declarations))
    return result

parse_cython = functools.partial(parse, 'cython_tokenize_flat')
parse_python = functools.partial(parse, 'python_tokenize_flat')


def parse_cssutils():
    stylesheet = parseString(CSS)
    result = []
    for rule in stylesheet.cssRules:
        selector = rule.selectorText
        declarations = [
            (declaration.name, len(list(declaration.propertyValue)))
            for declaration in rule.style.getProperties(all=True)]
        result.append((selector, declarations))
    return result


def check_consistency():
    result = parse_python()
    assert len(result) > 0
    if tokenizer.cython_tokenize_flat:
        assert parse_cython() == result
    assert parse_cssutils() == result
    version = '.'.join(map(str, sys.version_info[:3]))
    print('Python {}, consistency OK.'.format(version))


def warm_up():
    is_pypy = hasattr(sys, 'pypy_translation_info')
    if is_pypy:
        print('Warming up for PyPy...')
        for i in range(80):
            for i in range(10):
                parse_python()
                parse_cssutils()
            sys.stdout.write('.')
            sys.stdout.flush()
        sys.stdout.write('\n')


def time(function):
    seconds = timeit.Timer(function).repeat(TIMEIT_REPEAT, TIMEIT_NUMBER)
    miliseconds = int(min(seconds) * 1000)
    return miliseconds


def run():
    if tokenizer.cython_tokenize_flat:
        data_set = [
            ('tinycss + speedups      ', parse_cython),
        ]
    else:
        print('Speedups are NOT available.')
        data_set = []
    data_set += [
        ('tinycss WITHOUT speedups', parse_python),
        ('cssutils                ', parse_cssutils),
    ]
    label, function = data_set.pop(0)
    ref = time(function)
    print('{}  {} ms'.format(label, ref))
    for label, function in data_set:
        result = time(function)
        print('{}  {} ms  {:.2f}x'.format(label, result, result / ref))


if __name__ == '__main__':
    check_consistency()
    warm_up()
    run()
