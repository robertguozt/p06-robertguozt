# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def _binary_alpha_palette_gif():
    # 100x100 palette GIF: left half is palette entry 1, marked transparent,
    # right half is opaque red.
    img = Image.new("P", (100, 100), 0)
    img.putpalette([200, 30, 30, 0, 0, 0] + [0] * 762)
    for x in range(50):
        for y in range(100):
            img.putpixel((x, y), 1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=1)
    return buffer.getvalue()


def test_resized_gif_keeps_transparent_pixels():
    cfg = Config(PILLOW_PRESERVE_INDEXED_MODE=True)
    engine = Engine(Context(config=cfg))
    engine.load(_binary_alpha_palette_gif(), ".gif")
    assert engine.original_mode == "P"

    engine.resize(200, 150)
    gif = Image.open(BytesIO(engine.read(".gif")))

    assert gif.format == "GIF"
    assert "transparency" in gif.info
    transparent_pixels = gif.convert("RGBA").getchannel("A").histogram()[0]
    assert transparent_pixels > 10000
