import enum
from enum import StrEnum


class IndexCategory(StrEnum):
    ATTEMPT = enum.auto()
    SEGMENT = enum.auto()
    STATISTIC = enum.auto()


class AttemptStat(StrEnum):
    START_OF_ATTEMPT = enum.auto()
    END_OF_ATTEMPT = enum.auto()
    RUN_TIME = enum.auto()
    CUMULATIVE_PLAYTIME = enum.auto()
    ATTEMPT_TIME = enum.auto()
    LAST_SPLIT = enum.auto()
    RESET_AT = enum.auto()
    TIME_UPON_RESET = enum.auto()

    SEGMENT_TIME = enum.auto()
    SPLIT_TIME = enum.auto()
    RESET_TIME = enum.auto()

    @classmethod
    @property
    def imported_attempt_stats(cls):
        return _STATS_GENERATED_UPON_IMPORT_ATTEMPTS


_STATS_GENERATED_UPON_IMPORT_ATTEMPTS = [
    AttemptStat.START_OF_ATTEMPT,
    AttemptStat.END_OF_ATTEMPT,
    AttemptStat.RUN_TIME,
    AttemptStat.ATTEMPT_TIME,
    AttemptStat.CUMULATIVE_PLAYTIME,
]