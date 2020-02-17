import logging

import psycopg2
import backoff
from kfailbot import kfailb_data


class DbBackend:
    """
    Database interaction happens solely here.
    """

    _reconnect_retries = 5
    _silence_table = "silence"

    def __init__(self, host, user, password, db_name=None, table_name=None):
        self._host = host
        self._user = user
        self._password= password

        if not db_name:
            db_name = "kfailbot"
        self._db_name = db_name

        if not table_name:
            table_name = "kfailbot"
        self._table_name = table_name

        logging.info(f"Trying to connect to database on {host}")
        self._connection_test()
        logging.info(f"Successfully connected to database")
        self._create_tables()

        self._db = self.__init_db()

    @backoff.on_exception(backoff.expo,
                      psycopg2.DatabaseError,
                      max_tries=15)
    def _connection_test(self):
        with psycopg2.connect(host=self._host, user=self._user, password=self._password, dbname=self._db_name) as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT 1")

    @backoff.on_exception(backoff.expo,
                      psycopg2.DatabaseError,
                      max_tries=15)
    def _create_tables(self):
        with psycopg2.connect(host=self._host, user=self._user, password=self._password, dbname=self._db_name) as db:
            with db.cursor() as cursor:
                with open('postgres/01-init.sql','r') as sql_file:
                    cursor.execute(sql_file.read())
            db.commit()

    @backoff.on_exception(backoff.expo, psycopg2.OperationalError, max_time=300)
    def __init_db(self):
        return psycopg2.connect(host=self._host, user=self._user, password=self._password, dbname=self._db_name)

    def unsubscribe_from_all_lines(self, subscriber):
        """
        Unsubscribes a subscriber from all lines.
        :param subscriber: The subscriber that wants to unsubscribe from all lines.
        :return:
        """
        if not isinstance(subscriber, int):
            raise Exception("You can only submit a single subscriber")

        with self._db.cursor() as cursor:
            sql = f"UPDATE {self._table_name} SET subscribers = array_remove(subscribers, %s)"
            cursor.execute(sql, (subscriber,))
        self._db.commit()

    def unsubscribe_from_line(self, subscriber, line):
        """
        Unsubscribes a subscriber from a given line.
        :param subscriber: The subscriber
        :param line: The line the subscriber wants to unregister from.
        :return:
        """
        if not isinstance(subscriber, int):
            raise Exception("You can only submit a single subscriber")

        with self._db.cursor() as cursor:
            sql = f"UPDATE {self._table_name} SET subscribers = array_remove(subscribers, %s) WHERE line = %s"
            cursor.execute(sql, (subscriber, line))
        self._db.commit()

    def subscribe_to_line(self, subscriber, line):
        """
        Subscribes the subscriber to a given line.
        :param subscriber: The subscriber
        :param line: The line the subscriber wants to subscribe to.
        :return:
        """
        if not isinstance(subscriber, int):
            raise Exception("You can only submit a single subscriber")

        sub_list = list()
        sub_list.append(subscriber)

        with self._db.cursor() as cursor:
            sql = f"INSERT INTO {self._table_name} VALUES(%s, %s) ON CONFLICT (line) DO UPDATE SET subscribers = array_cat({self._table_name}.subscribers, %s) WHERE {self._table_name}.line = %s AND %s <> ALL ({self._table_name}.subscribers);"
            cursor.execute(sql, (line, sub_list, sub_list, line, subscriber))
        self._db.commit()

    def get_subscriptions(self, subscriber):
        """
        Returns all subscriptions for a given subscriber.
        :param subscriber: The subscriber
        :return: A list of all subscriptions for the given subscriber.
        """
        with self._db.cursor() as cursor:
            sql = f"SELECT line FROM {self._table_name} WHERE %s = ANY(subscribers)"
            cursor.execute(sql, (subscriber,))
            return [r[0] for r in cursor.fetchall()]

    def get_subscribers(self, line):
        """
        Returns all subscribers that are subscribed to a given line.
        :param line: The line
        :return: A list of all the subscribers for the given line.
        """
        with self._db.cursor() as cursor:
            sql = f"SELECT subscribers FROM {self._table_name} WHERE line = %s"
            cursor.execute(sql, (line,))
            ret = cursor.fetchone()
            if ret:
                return ret[0]
            return []

    def delete_all_subscriptions(self):
        """
        This deletes all subscriptions in the database. Use with caution.
        :return:
        """
        with self._db.cursor() as cursor:
            sql = f"DELETE FROM {self._table_name}"
            cursor.execute(sql)
        self._db.commit()

    def new_silence(self, subscriber, until, mute=True):
        """
        Creates a new silence for a subscriber.
        :param subscriber: The subscriber.
        :param until: Datetime object that marks the point in time until the messages
         are being silenced.
        :param mute: A boolean that denotes whether there should be messages kept from
        sending or sending messages without displaying notifications in the client.
        :return:
        """
        if not isinstance(subscriber, int):
            raise Exception("You can only submit a single subscriber")

        with self._db.cursor() as cursor:
            sql = (
                f"INSERT INTO {self._silence_table} VALUES(%s, %s, %s)"
                f" ON CONFLICT (subscriber) DO UPDATE SET until = %s, mute = %s WHERE {self._silence_table}.subscriber = %s;"
            )
            cursor.execute(sql, (subscriber, until, mute, until, mute, subscriber))

        self._db.commit()

    def delete_silence(self, subscriber):
        """
        Deletes a silence for a given subscriber.
        :param subscriber: The subscriber that wants to get rid of the silence.
        :return:
        """
        if not isinstance(subscriber, int):
            raise Exception("You can only submit a single subscriber")

        with self._db.cursor() as cursor:
            sql = f"DELETE FROM {self._silence_table} WHERE subscriber = %s"
            cursor.execute(sql, (subscriber,))

        self._db.commit()

    def delete_all_silences(self):
        """
        Deletes all silences. Use with caution.
        :return:
        """
        with self._db.cursor() as cursor:
            sql = f"DELETE FROM {self._silence_table}"
            cursor.execute(sql)

        self._db.commit()

    def read_silence(self, subscriber):
        """
        Reads the silence information for a given subscriber.
        :param subscriber: The subscriber
        :return: A Subscription object for the given subscriber.
        """
        ret = None
        with self._db.cursor() as cursor:
            sql = f"SELECT until, mute FROM {self._silence_table} WHERE subscriber = %s"
            cursor.execute(sql, (subscriber,))
            ret = cursor.fetchone()

        if not ret:
            return kfailb_data.Silence()

        return kfailb_data.Silence(ret[0], ret[1])
