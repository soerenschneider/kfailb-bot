import unittest
from unittest import TestCase

from kfailbot.db_backends import DbBackend


class TestDbBackend(TestCase):
    backend = DbBackend(host='localhost', user='kfailb', password='kfailb')

    def setUp(self):
        self.backend.delete_all_subscriptions()

    def test_subscribe_to_line_simple(self):
        subscriber = 1984
        line = 5

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)

        self.backend.subscribe_to_line(subscriber, line)

        subscribers = self.backend.get_subscribers(line)
        self.assertIn(subscriber, subscribers)

    def test_subscribe_to_line_idempotence(self):
        subscriber = 1984
        line = 5

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)
        self.assertEqual(0, len(subscribers))

        self.backend.subscribe_to_line(subscriber, line)
        self.backend.subscribe_to_line(subscriber, line)

        subscribers = self.backend.get_subscribers(line)
        self.assertIn(subscriber, subscribers)
        self.assertEqual(1, len(subscribers))

    def test_unsubscribe_from_line(self):
        subscriber = 1984
        line = 5

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)
        self.assertEqual(0, len(subscribers))

        self.backend.subscribe_to_line(subscriber, line)

        subscribers = self.backend.get_subscribers(line)
        self.assertIn(subscriber, subscribers)

        self.backend.unsubscribe_from_line(subscriber, line)

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)

    def test_unsubscribe_from_line_empty(self):
        subscriber = 1984
        line = 5

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)
        self.assertEqual(0, len(subscribers))

        self.backend.unsubscribe_from_line(subscriber, line)

    def test_unsubscribe_from_line_different_line(self):
        subscriber = 1984
        line = 5

        subscribers = self.backend.get_subscribers(line)
        self.assertNotIn(subscriber, subscribers)
        self.assertEqual(0, len(subscribers))

        self.backend.subscribe_to_line(subscriber, line)
        self.backend.unsubscribe_from_line(subscriber, line+1)

        subscribers = self.backend.get_subscribers(line)
        self.assertIn(subscriber, subscribers)
        self.assertEqual(1, len(subscribers))


if __name__ == '__main__':
    unittest.main()
