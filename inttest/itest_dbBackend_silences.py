from unittest import TestCase

from datetime import datetime
from datetime import timedelta

from kfailbot import db_backends
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
            with open('postgres/01-init.sql','r') as sql_file:
                cursor.execute(sql_file.read())
        db.commit()
        db.close()

        self._db = db_backends.DbBackend(host=host, user=user, password=pw)

    def test_read_silence_empty(self):
        subscriber = 2121421

        # make sure silences are gone
        self._db.delete_all_silences()

        # try to read subscriber
        ret = self._db.read_silence(subscriber)

        assert ret.until is None
        assert ret.is_effective() is False

    def test_read_silence_empty(self):
        subscriber = 2121421
        until = datetime.utcnow() + timedelta(minutes=30)

        # make sure silences are gone
        self._db.delete_all_silences()

        # create new silence
        self._db.new_silence(subscriber, until, True)

        # read silence
        ret = self._db.read_silence(subscriber)

        assert ret is not None              # there is an object returned
        assert ret.until == until           # the end of the silence is identical
        assert ret.mute is True             # the silence is completely muted
        assert ret.is_effective() is True   # the silence is effective right now

    def test_read_silence_delete(self):
        subscriber = 2121421
        until = datetime.utcnow() + timedelta(minutes=30)

        # make sure silences are gone
        self._db.delete_all_silences()

        # create new silence
        self._db.new_silence(subscriber, until, True)

        # read silence
        ret = self._db.read_silence(subscriber)

        assert ret.until == until           # the end of the silence is identical

        # delete silence
        self._db.delete_silence(subscriber)

        # read silence
        ret = self._db.read_silence(subscriber)

        assert ret.until is None
        assert ret.is_effective() is False

    def test_read_silence_update(self):
        subscriber = 2121421
        until = datetime.utcnow() + timedelta(minutes=30)
        complete_silence = True

        # make sure silences are gone
        self._db.delete_all_silences()

        # create new silence
        self._db.new_silence(subscriber, until, complete_silence)

        # read silence
        ret = self._db.read_silence(subscriber)

        assert ret is not None                  # there is an object returned
        assert ret.until == until               # the end of the silence is identical
        assert ret.mute is complete_silence     # the silence is completely muted
        assert ret.is_effective() is True       # the silence is effective right now

        new_until = datetime.utcnow() - timedelta(minutes=5)
        new_complete_silence = False
        self._db.new_silence(subscriber, new_until, new_complete_silence)

        # read silence
        ret = self._db.read_silence(subscriber)

        assert ret is not None                  # there is an object returned
        assert ret.until == new_until           # the end of the silence is identical
        assert ret.mute is new_complete_silence # the silence is completely muted
        assert ret.is_effective() is False      # the silence is effective right now

