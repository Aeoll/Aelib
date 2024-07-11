# coding: utf-8
"""
    Tests for the CSS 3 color parser
    --------------------------------

    :copyright: (c) 2012 by Simon Sapin.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import unicode_literals

import pytest
from tinycss.color3 import hsl_to_rgb, parse_color_string


@pytest.mark.parametrize(('css_source', 'expected_result'), [
    ('', None),
    (' /* hey */\n', None),
    ('4', None),
    ('top', None),
    ('/**/transparent', (0, 0, 0, 0)),
    ('transparent', (0, 0, 0, 0)),
    (' transparent\n', (0, 0, 0, 0)),
    ('TransParent', (0, 0, 0, 0)),
    ('currentColor', 'currentColor'),
    ('CURRENTcolor', 'currentColor'),
    ('current_Color', None),

    ('black', (0, 0, 0, 1)),
    ('white', (1, 1, 1, 1)),
    ('fuchsia', (1, 0, 1, 1)),
    ('cyan', (0, 1, 1, 1)),
    ('CyAn', (0, 1, 1, 1)),
    ('darkkhaki', (189 / 255., 183 / 255., 107 / 255., 1)),

    ('#', None),
    ('#f', None),
    ('#ff', None),
    ('#fff', (1, 1, 1, 1)),
    ('#ffg', None),
    ('#ffff', None),
    ('#fffff', None),
    ('#ffffff', (1, 1, 1, 1)),
    ('#fffffg', None),
    ('#fffffff', None),
    ('#ffffffff', None),
    ('#fffffffff', None),

    ('#cba987', (203 / 255., 169 / 255., 135 / 255., 1)),
    ('#CbA987', (203 / 255., 169 / 255., 135 / 255., 1)),
    ('#1122aA', (17 / 255., 34 / 255., 170 / 255., 1)),
    ('#12a', (17 / 255., 34 / 255., 170 / 255., 1)),

    ('rgb(203, 169, 135)', (203 / 255., 169 / 255., 135 / 255., 1)),
    ('RGB(255, 255, 255)', (1, 1, 1, 1)),
    ('rgB(0, 0, 0)', (0, 0, 0, 1)),
    ('rgB(0, 51, 255)', (0, .2, 1, 1)),
    ('rgb(0,51,255)', (0, .2, 1, 1)),
    ('rgb(0\t,  51 ,255)', (0, .2, 1, 1)),
    ('rgb(/* R */0, /* G */51, /* B */255)', (0, .2, 1, 1)),
    ('rgb(-51, 306, 0)', (-.2, 1.2, 0, 1)),  # out of 0..1 is allowed

    ('rgb(42%, 3%, 50%)', (.42, .03, .5, 1)),
    ('RGB(100%, 100%, 100%)', (1, 1, 1, 1)),
    ('rgB(0%, 0%, 0%)', (0, 0, 0, 1)),
    ('rgB(10%, 20%, 30%)', (.1, .2, .3, 1)),
    ('rgb(10%,20%,30%)', (.1, .2, .3, 1)),
    ('rgb(10%\t,  20% ,30%)', (.1, .2, .3, 1)),
    ('rgb(/* R */10%, /* G */20%, /* B */30%)', (.1, .2, .3, 1)),
    ('rgb(-12%, 110%, 1400%)', (-.12, 1.1, 14, 1)),  # out of 0..1 is allowed

    ('rgb(10%, 50%, 0)', None),
    ('rgb(255, 50%, 0%)', None),
    ('rgb(0, 0 0)', None),
    ('rgb(0, 0, 0deg)', None),
    ('rgb(0, 0, light)', None),
    ('rgb()', None),
    ('rgb(0)', None),
    ('rgb(0, 0)', None),
    ('rgb(0, 0, 0, 0)', None),
    ('rgb(0%)', None),
    ('rgb(0%, 0%)', None),
    ('rgb(0%, 0%, 0%, 0%)', None),
    ('rgb(0%, 0%, 0%, 0)', None),

    ('rgba(0, 0, 0, 0)', (0, 0, 0, 0)),
    ('rgba(203, 169, 135, 0.3)', (203 / 255., 169 / 255., 135 / 255., 0.3)),
    ('RGBA(255, 255, 255, 0)', (1, 1, 1, 0)),
    ('rgBA(0, 51, 255, 1)', (0, 0.2, 1, 1)),
    ('rgba(0, 51, 255, 1.1)', (0, 0.2, 1, 1)),
    ('rgba(0, 51, 255, 37)', (0, 0.2, 1, 1)),
    ('rgba(0, 51, 255, 0.42)', (0, 0.2, 1, 0.42)),
    ('rgba(0, 51, 255, 0)', (0, 0.2, 1, 0)),
    ('rgba(0, 51, 255, -0.1)', (0, 0.2, 1, 0)),
    ('rgba(0, 51, 255, -139)', (0, 0.2, 1, 0)),

    ('rgba(42%, 3%, 50%, 0.3)', (.42, .03, .5, 0.3)),
    ('RGBA(100%, 100%, 100%, 0)', (1, 1, 1, 0)),
    ('rgBA(0%, 20%, 100%, 1)', (0, 0.2, 1, 1)),
    ('rgba(0%, 20%, 100%, 1.1)', (0, 0.2, 1, 1)),
    ('rgba(0%, 20%, 100%, 37)', (0, 0.2, 1, 1)),
    ('rgba(0%, 20%, 100%, 0.42)', (0, 0.2, 1, 0.42)),
    ('rgba(0%, 20%, 100%, 0)', (0, 0.2, 1, 0)),
    ('rgba(0%, 20%, 100%, -0.1)', (0, 0.2, 1, 0)),
    ('rgba(0%, 20%, 100%, -139)', (0, 0.2, 1, 0)),

    ('rgba(255, 255, 255, 0%)', None),
    ('rgba(10%, 50%, 0, 1)', None),
    ('rgba(255, 50%, 0%, 1)', None),
    ('rgba(0, 0, 0 0)', None),
    ('rgba(0, 0, 0, 0deg)', None),
    ('rgba(0, 0, 0, light)', None),
    ('rgba()', None),
    ('rgba(0)', None),
    ('rgba(0, 0, 0)', None),
    ('rgba(0, 0, 0, 0, 0)', None),
    ('rgba(0%)', None),
    ('rgba(0%, 0%)', None),
    ('rgba(0%, 0%, 0%)', None),
    ('rgba(0%, 0%, 0%, 0%)', None),
    ('rgba(0%, 0%, 0%, 0%, 0%)', None),

    ('HSL(0, 0%, 0%)', (0, 0, 0, 1)),
    ('hsL(0, 100%, 50%)', (1, 0, 0, 1)),
    ('hsl(60, 100%, 37.5%)', (0.75, 0.75, 0, 1)),
    ('hsl(780, 100%, 37.5%)', (0.75, 0.75, 0, 1)),
    ('hsl(-300, 100%, 37.5%)', (0.75, 0.75, 0, 1)),
    ('hsl(300, 50%, 50%)', (0.75, 0.25, 0.75, 1)),

    ('hsl(10, 50%, 0)', None),
    ('hsl(50%, 50%, 0%)', None),
    ('hsl(0, 0% 0%)', None),
    ('hsl(30deg, 100%, 100%)', None),
    ('hsl(0, 0%, light)', None),
    ('hsl()', None),
    ('hsl(0)', None),
    ('hsl(0, 0%)', None),
    ('hsl(0, 0%, 0%, 0%)', None),

    ('HSLA(-300, 100%, 37.5%, 1)', (0.75, 0.75, 0, 1)),
    ('hsLA(-300, 100%, 37.5%, 12)', (0.75, 0.75, 0, 1)),
    ('hsla(-300, 100%, 37.5%, 0.2)', (0.75, 0.75, 0, .2)),
    ('hsla(-300, 100%, 37.5%, 0)', (0.75, 0.75, 0, 0)),
    ('hsla(-300, 100%, 37.5%, -3)', (0.75, 0.75, 0, 0)),

    ('hsla(10, 50%, 0, 1)', None),
    ('hsla(50%, 50%, 0%, 1)', None),
    ('hsla(0, 0% 0%, 1)', None),
    ('hsla(30deg, 100%, 100%, 1)', None),
    ('hsla(0, 0%, light, 1)', None),
    ('hsla()', None),
    ('hsla(0)', None),
    ('hsla(0, 0%)', None),
    ('hsla(0, 0%, 0%, 50%)', None),
    ('hsla(0, 0%, 0%, 1, 0%)', None),

    ('cmyk(0, 0, 0, 0)', None),
])
def test_color(css_source, expected_result):
    result = parse_color_string(css_source)
    if isinstance(result, tuple):
        for got, expected in zip(result, expected_result):
            # Compensate for floating point errors:
            assert abs(got - expected) < 1e-10
        for i, attr in enumerate(['red', 'green', 'blue', 'alpha']):
            assert getattr(result, attr) == result[i]
    else:
        assert result == expected_result


@pytest.mark.parametrize(('hsl', 'expected_rgb'), [
    # http://en.wikipedia.org/wiki/HSL_and_HSV#Examples
    ((0,     0,    100 ), (1,     1,     1    )),  # noqa
    ((127,   0,    100 ), (1,     1,     1    )),  # noqa
    ((0,     0,    50  ), (0.5,   0.5,   0.5  )),  # noqa
    ((127,   0,    50  ), (0.5,   0.5,   0.5  )),  # noqa
    ((0,     0,    0   ), (0,     0,     0    )),  # noqa
    ((127,   0,    0   ), (0,     0,     0    )),  # noqa
    ((0,     100,  50  ), (1,     0,     0    )),  # noqa
    ((60,    100,  37.5), (0.75,  0.75,  0    )),  # noqa
    ((780,   100,  37.5), (0.75,  0.75,  0    )),  # noqa
    ((-300,  100,  37.5), (0.75,  0.75,  0    )),  # noqa
    ((120,   100,  25  ), (0,     0.5,   0    )),  # noqa
    ((180,   100,  75  ), (0.5,   1,     1    )),  # noqa
    ((240,   100,  75  ), (0.5,   0.5,   1    )),  # noqa
    ((300,   50,   50  ), (0.75,  0.25,  0.75 )),  # noqa
    ((61.8,  63.8, 39.3), (0.628, 0.643, 0.142)),  # noqa
    ((251.1, 83.2, 51.1), (0.255, 0.104, 0.918)),  # noqa
    ((134.9, 70.7, 39.6), (0.116, 0.675, 0.255)),  # noqa
    ((49.5,  89.3, 49.7), (0.941, 0.785, 0.053)),  # noqa
    ((283.7, 77.5, 54.2), (0.704, 0.187, 0.897)),  # noqa
    ((14.3,  81.7, 62.4), (0.931, 0.463, 0.316)),  # noqa
    ((56.9,  99.1, 76.5), (0.998, 0.974, 0.532)),  # noqa
    ((162.4, 77.9, 44.7), (0.099, 0.795, 0.591)),  # noqa
    ((248.3, 60.1, 37.3), (0.211, 0.149, 0.597)),  # noqa
    ((240.5, 29,   60.7), (0.495, 0.493, 0.721)),  # noqa
])
def test_hsl(hsl, expected_rgb):
    for got, expected in zip(hsl_to_rgb(*hsl), expected_rgb):
        # Compensate for floating point errors and Wikipedia’s rounding:
        assert abs(got - expected) < 0.001
