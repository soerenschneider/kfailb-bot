from unittest import TestCase

from kfailbot import db_backends
import psycopg2
import os

class TestDbBackend_lines(TestCase):
    def setUp(self):
        host=os.getenv("POSTGRES_HOST", "localhost")
        user=os.getenv("POSTGRES_USER", "kfailb")
        pw=os.getenv("POSTGRES_PASSWORD", "kfailb")
        db=os.getenv("POSTGRES_DB", "kfailbot")

        db = psycopg2.connect(host=host, user=user, password=pw, dbname=db)
        with db.cursor() as cursor:
            with open('postgres/01-init.sql','r') as sql_file:
                cursor.execute(sql_file.read())
        db.commit()
        db.close()

        self._db = db_backends.DbBackend(host=host, user=user, password=pw)

    def test_get_subscriptions(self):
        self._db.delete_all_subscriptions()

        subscriber = 8327432

        # read all subscriptions for subscriber
        subscriptions = self._db.get_subscriptions(subscriber)

        # make sure there are none
        assert len(subscriptions) == 0

    def test_subscribe(self):
        self._db.delete_all_subscriptions()

        subscriber = 8327432
        lines = [1, 12, 123]

        # subscribe to line 1
        self._db.subscribe_to_line(subscriber, lines[0])
        self._db.subscribe_to_line(subscriber, lines[1])

        # read all subscriptions for subscriber
        subscriptions = self._db.get_subscriptions(subscriber)

        # make sure there are two subscriptions
        assert len(subscriptions) == 2
        assert lines[0] in subscriptions
        assert lines[1] in subscriptions
        assert lines[2] not in subscriptions

    def test_subscribe_idempotency(self):
        self._db.delete_all_subscriptions()

        subscriber = 8327432
        lines = [1, 1, 1]

        # subscribe to the same line – twice
        self._db.subscribe_to_line(subscriber, lines[0])
        self._db.subscribe_to_line(subscriber, lines[1])

        # read all subscriptions for subscriber
        subscriptions = self._db.get_subscriptions(subscriber)

        # make sure there is only one instead of two subscriptions
        assert len(subscriptions) == 1
        assert lines[0] in subscriptions

    def test_subscribe_multiple_subscribers(self):
        self._db.delete_all_subscriptions()

        subscriber_1 = 8327432
        subscriber_2 = 2222222
        line = 1

        # subscribe to the same line – twice
        self._db.subscribe_to_line(subscriber_1, line)
        self._db.subscribe_to_line(subscriber_2, line)

        # make sure there are two subscribers for the line
        subscribers = self._db.get_subscribers(line)
        assert len(subscribers) == 2

    def test_subscribe_multiple_subscribers(self):
        self._db.delete_all_subscriptions()

        subscriber_1 = 8327432
        subscriber_2 = 2222222
        line = 1

        # subscribe to the same line – twice
        self._db.subscribe_to_line(subscriber_1, line)
        self._db.subscribe_to_line(subscriber_2, line)

        # unsubscribe right away
        self._db.unsubscribe_from_line(subscriber_1, line)

        subscribers = self._db.get_subscribers(line)
        assert len(subscribers) == 1
        assert subscriber_2 in subscribers

    def test_unsubscribe_from_all_lines(self):
        self._db.delete_all_subscriptions()

        subscriber = 8327432
        lines = [1, 2]

        # subscribe to the same line – twice
        self._db.subscribe_to_line(subscriber, lines[0])
        self._db.subscribe_to_line(subscriber, lines[1])

        # read subscriptions, check they're correct
        subscriptions = self._db.get_subscriptions(subscriber)
        assert len(subscriptions) == 2

        # unsubscribe from all lines
        self._db.unsubscribe_from_all_lines(subscriber)

        # re-read subscriptions, make sure there are non left
        subscriptions = self._db.get_subscriptions(subscriber)
        assert len(subscriptions) == 0
