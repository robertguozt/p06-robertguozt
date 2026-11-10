# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from thumbor.ext.filters import _round_corner


def test_transparent_round_corner_has_no_dark_ring():
    width = 100
    height = 100
    radius = 30
    # Solid white RGBA source, fully opaque.
    source = bytes([255, 255, 255, 255]) * (width * height)

    out = _round_corner.apply(
        1,
        "RGBA",
        radius,
        radius,
        255,
        255,
        255,
        width,
        height,
        source,
        1,
    )

    # Every pixel in the top-left corner box that is still fully opaque
    # must keep the source color. A dark ring shows up as opaque pixels
    # whose color was scaled toward black.
    for y in range(radius):
        for x in range(radius):
            idx = (y * width + x) * 4
            alpha = out[idx + 3]
            if alpha == 255:
                assert out[idx:idx + 3] == b"\xff\xff\xff", (
                    f"opaque pixel at ({x}, {y}) is darkened: "
                    f"{tuple(out[idx:idx + 4])}"
                )
