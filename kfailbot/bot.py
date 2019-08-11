import json
import logging
import redis

import backoff


from kfailbot import ProcessedHashesRedisBackend

from kfailbot import DbBackend
from kfailbot import KFailBTelegramBot

from kfailbot import IncidentFormatter
from kfailbot import Incident

_last_messages = {}
_db_backend = None


class KFailBot:
    _hash_key = "kfailb_hashes_{}"

    def __init__(self, args):
        if not args:
            raise ValueError("No args provided")

        self._stream_name = args.stream_name
        self._redis = self.init(args.redis_host)
        self._hashes_backend = ProcessedHashesRedisBackend(self._redis)

        self._db_backend = DbBackend(host=args.pg_host, user=args.pg_user, password=args.pg_pw, db_name=args.pg_db)
        self._notifier = KFailBTelegramBot(args.token, self._db_backend)

    @backoff.on_exception(backoff.expo,
                          redis.exceptions.ConnectionError,
                          max_time=300)
    def init(self, host="localhost", port=6379, db=0):
        client = redis.Redis(host=host, port=port, db=db, charset="utf-8", decode_responses=True)
        client.get("x")
        logging.info("Successfully connected to redis")
        return client

    def notify_new_problems(self, incidents):
        for incident in incidents:
            message = IncidentFormatter.format_incident(incident)
            message = f"*{incident['line']}* {message}"
            self._notifier.send_message(text=message, line=incident['line'], is_markdown=True)

    def notify_solved_problems(self, diff):
        for line in diff:
            self._notifier.send_message(text=f"Problem mit Linie {line} behoben")

    @backoff.on_exception(backoff.expo,
                          redis.exceptions.ConnectionError,
                          max_time=3600)
    def read_stream(self, last_id=None):
        if last_id is None:
            last_id = '$'

        streams = {self._stream_name: last_id}
        incidents = self._redis.xread(streams, count=100, block=0)
        last_seen_id = None

        for incident in incidents:
            payload = incident[1][0]
            msg_id = payload[0]
            last_seen_id = msg_id
            try:
                data = payload[1]["data"]
                obj = self.decode(data)
                if obj is None:
                    continue

                if not self.is_already_processed(obj.hash):
                    logging.debug("Object not seen before: %s", str(obj))
                    msg = IncidentFormatter.format_incident(obj)
                    self._notifier.send_message(msg, obj.line)
                else:
                    logging.debug("Ignoring known object %s", obj.hash)

            except KeyError:
                logging.error("Missing 'data' attribute msg: %s", payload)
        return last_seen_id

    @staticmethod
    def decode(string):
        try:
            return Incident.from_json(string)
        except (json.decoder.JSONDecodeError, TypeError):
            return None

    def start(self):
        cont = True
        logging.info("Waiting for messages on stream")
        try:
            msg_id = None
            while cont:
                msg_id = self.read_stream(msg_id)
        except KeyboardInterrupt:
            cont = False

    def is_already_processed(self, obj_hash):
        if not obj_hash:
            raise ValueError("No object hash given. ")

        key = self._hash_key.format(obj_hash)
        reply = self._redis.get(key)
        # we're not interested in the reply
        processed = reply is not None
        # as we're only offering garbage
        self._redis.setex(name=key, time=600, value="x")
        return processed

    def filter_stale_data(self):
        """ Returns a subset of the list that has not been seen before. """
        processed_hashes = list()
        ret = list()

        cache_data = self._hashes_backend.get_data()
        for incident in cache_data['incidents']:
            hashed = incident.hash
            processed_hashes.append(hashed)

            if not self._hashes_backend.is_hash_processed(hashed):
                logging.debug(f'{hashed} [{incident}] not found in prev_processed_hashes')

                # attach timestamp from original object
                incident['timestamp'] = cache_data['time_stamp']
                ret.append(incident)

        self.hashes_backend.write_processed_hashes(processed_hashes)

        return ret, []
