import unittest
from unittest import TestCase

from kfailbot.db_backends import DbBackend
import psycopg2
import os


class TestDbBackend(TestCase):
    
    def setUp(self):
        host=os.getenv("POSTGRES_HOST", "localhost")
        user=os.getenv("POSTGRES_USER", "kfailb")
        pw=os.getenv("POSTGRES_PASSWORD", "kfailb")
        db=os.getenv("POSTGRES_DB", "kfailbot")

        db = psycopg2.connect(host=host, user=user, password=pw, dbname=db)
        with db.cursor() as cursor:
            with open('postgres/init.sql','r') as sql_file:
                cursor.execute(sql_file.read())
        db.commit()
        db.close()

        self.backend = DbBackend(host=host, user=user, password=pw)
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
