from unittest import TestCase

from kfailbot import kfailbot

class TestKFailBot(TestCase):
    def test_decode_empty(self):
        assert None is kfailbot.KFailBot.decode("")

    def test_decode_nil(self):
        assert None is kfailbot.KFailBot.decode(None)

    def test_decode_int(self):
        assert None is kfailbot.KFailBot.decode(5)