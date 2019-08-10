import datetime
import hashlib

from typing import List
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Station:
    """
    Tuple of a station and a given time.
    """
    station: str
    time: str

    def __repr__(self):
        return f'{self.station} ({self.time})'


@dataclass_json
@dataclass
class Incident:
    """
    Holds information about a single incident.
    """
    # what line is affected by the incident.
    line: int

    # information about the incident.
    what: str

    # list of stations that are affected. may be empty.
    stations: List[Station]

    # the same line goes in two directions, from a -> z and from z -> a. if there is information about affected
    # stations, a string is being built that indicates the direction of an incident. is empty if no stations
    # information is available.
    direction: str = field(init=False)

    # the hash is used by consuming clients to easily determine whether a message has been processed already.
    # it consists of a unix timestamp and a truncated sha256 hex-digested hash, in the format '<timestamp>-<hash>'.
    hash: str = ""

    def __post_init__(self):
        self.direction = self.__gen_direction()

        self.hash = self.__gen_hash()

    def __gen_direction(self):
        """
        Generates the directions string.
        :return: None if there are no stations, otherwise a string that denotes the direction.
        """
        if self.stations:
            return "{} -> {}".format(self.stations[0].station,
                                     self.stations[len(self.stations)-1].station)

        return None

    def __gen_hash(self):
        """
        Generates the hash for this object.
        :return: the hash
        """
        representation = str(self)
        sha256 = hashlib.sha256(representation.encode('utf-8')).hexdigest()[:15]

        return sha256

    def __repr__(self):
        return f'{self.line}: {self.direction}: {self.what}\n{self.stations}\n'


@dataclass
class Silence:
    until: datetime.datetime = None
    mute: bool = True

    def is_effective(self):
        if not self.until:
            return False

        now = datetime.datetime.utcnow()
        return self.until >= now
