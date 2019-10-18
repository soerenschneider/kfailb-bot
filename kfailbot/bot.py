import json
import logging
import redis

import backoff


from kfailbot import ProcessedHashesRedisBackend

from kfailbot import DbBackend
from kfailbot import KFailBTelegramBot

from kfailbot import IncidentFormatter
from kfailbot import Incident


class KFailBot:
    _hash_key = "kfailb_hashes_{}"

    def __init__(self, args):
        if not args:
            raise ValueError("No args provided")

        self._stream_name = args.stream_name
        self._redis = self._init_redis(args.redis_host)
        self._hashes_backend = ProcessedHashesRedisBackend(self._redis)

        self._db_backend = DbBackend(
            host=args.pg_host,
            user=args.pg_user,
            password=args.pg_pw,
            db_name=args.pg_db,
        )
        self._notifier = KFailBTelegramBot(args.token, self._db_backend)

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_time=300)
    def _init_redis(self, host="localhost", port=6379, db=0):
        """
        Initializes the redis client.
        :param host: string, the hostname of the redis instance to connect to.
        :param port: int, the port of the redis instance to connect to.
        :param db: int, the database of the redis instance to connect to.
        :return: redis.Redis, initialized redis client.
        """
        client = redis.Redis(
            host=host, port=port, db=db, charset="utf-8", decode_responses=True
        )
        client.get("x")
        logging.info("Successfully connected to redis")
        return client

    def _message_received(self, obj):
        """
        Called whenever a message is received. Formats the message and sends it away.
        :param obj: Incident object that has been taken from the stream.
        :return:
        """
        if obj is None:
            return

        if not self._is_already_processed(obj.hash):
            logging.debug("Object not seen before: %s", str(obj))
            msg = IncidentFormatter.format_incident(obj)
            self._notifier.send_message(msg, obj.line)
        else:
            logging.debug("Ignoring known object %s", obj.hash)

    @backoff.on_exception(backoff.expo, redis.exceptions.ConnectionError, max_time=3600)
    def read_stream(self, last_id=None):
        """
        Reads the stream and perfo
        :param last_id:
        :return:
        """
        if last_id is None:
            last_id = "$"

        streams = {self._stream_name: last_id}
        incidents = self._redis.xread(streams, count=100, block=0)
        last_seen_id = None

        for incident in incidents:
            payload = incident[1][0]
            msg_id = payload[0]
            last_seen_id = msg_id
            try:
                data = payload[1]["data"]
                obj = self.decode_incident(data)
                if obj is None:
                    continue

                self._message_received(obj)
            except KeyError:
                logging.error("Missing 'data' attribute msg: %s", payload)

        return last_seen_id

    @staticmethod
    def decode_incident(string):
        try:
            return Incident.from_json(string)
        except (json.decoder.JSONDecodeError, TypeError):
            return None

    def start(self):
        """
        Start listening for incident messages.
        :return: None
        """
        cont = True
        logging.info("Waiting for messages on stream")
        try:
            msg_id = None
            while cont:
                msg_id = self.read_stream(msg_id)
        except KeyboardInterrupt:
            cont = False

    def _is_already_processed(self, obj_hash):
        """
        Checks whether an object has already been processed in the last 10 minutes.
        :param obj_hash: string, the hash of the object.
        :return: True, if the object has been already seen in the last 10 minutes, otherwise
        False.
        """
        if not obj_hash:
            raise ValueError("No object hash given. ")

        key = self._hash_key.format(obj_hash)
        reply = self._redis.get(key)
        # we're not interested in the reply
        processed = reply is not None
        # as we're only offering garbage
        self._redis.setex(name=key, time=600, value="x")
        return processed
