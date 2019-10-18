import logging
import time
import json


class ProcessedHashesRedisBackend:
    _key_all = "kfailb_all"

    def __init__(
        self, redis_client, key="kfailbot_processed_hashes", expire_time_seconds=3600
    ):
        self._redis = redis_client
        self._key = key
        self.expire_time_seconds = expire_time_seconds

    def read_processed_hashes(self):
        """ returns a list of hashes"""
        hashes = self._redis.get(self._key)
        if not hashes:
            logging.debug("No previously processed hashes found")
            return {}

        logging.debug("Read processed hashes: %s", hashes)
        return hashes.decode_incident("utf-8")

    def is_hash_processed(self, hash):
        """ checks whether a hash has been processed lately. """

        # if it has a score it has been processed, otherwise it hasn't
        score = self._redis.zscore(self._key, hash)
        return score is not None

    def write_processed_hashes(self, hashes):
        """ stores the processed hashes in the backend. """

        # the hashes are stored as a sorted set, the score is determined by the current unix timestamp
        rank = int(time.time())

        # we want to delete everything that's older than the timestamp one hour ago
        expire_date = rank - self.expire_time_seconds

        # add all the hashes in a pipe for more efficiency
        pipe = self._redis.pipeline()
        for h in hashes:
            pipe.zadd(self._key, {h: rank})
        pipe.zremrangebyscore(self._key, 0, expire_date)
        pipe.execute()

    def get_data(self):
        cache_data = self._redis.get(self._key_all)

        if cache_data:
            return json.loads(cache_data.decode_incident("utf-8"))

        return dict()
