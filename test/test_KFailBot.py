from unittest import TestCase

from kfailbot import bot

class TestKFailBot(TestCase):
    def test_decode_empty(self):
        assert None is bot.KFailBot.decode_incident("")

    def test_decode_nil(self):
        assert None is bot.KFailBot.decode_incident(None)

    def test_decode_int(self):
        assert None is bot.KFailBot.decode_incident(5)