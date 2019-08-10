from unittest import TestCase

from kfailbot import bla

class TestKFailBot(TestCase):
    def test_decode_empty(self):
        assert None is bla.KFailBot.decode("")

    def test_decode_nil(self):
        assert None is bla.KFailBot.decode(None)

    def test_decode_int(self):
        assert None is bla.KFailBot.decode(5)