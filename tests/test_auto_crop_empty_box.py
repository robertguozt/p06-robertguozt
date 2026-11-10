# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.base import TestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

COURSE_IMAGES_PATH = abspath(join(dirname(__file__), "../course/images/"))


class IssueAutoCropPipelineTestCase(TestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES_PATH
        cfg.STORAGE = "thumbor.storages.no_storage"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_wide_resize_of_transparent_image_is_not_blank(self):
        response = await self.async_fetch("/unsafe/800x20/rainbow.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body)).convert("RGBA")
        assert image.size == (800, 20)
        # A blank result has every alpha value at 0
        assert image.getchannel("A").getextrema()[1] > 0

    @gen_test
    async def test_fit_in_1x1_returns_1x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/1x1/940x2.png")
        assert response.code == 200
        assert Image.open(BytesIO(response.body)).size == (1, 1)

    @gen_test
    async def test_fit_in_width_only_returns_100x1_image(self):
        response = await self.async_fetch("/unsafe/fit-in/100x0/940x2.png")
        assert response.code == 200
        assert Image.open(BytesIO(response.body)).size == (100, 1)
