import enum
from enum import StrEnum


class DistributionColumn(StrEnum):
    QUANTILE = enum.auto()
    SEGMENT_TIME = enum.auto()
    NODE_WEIGHT = enum.auto()
    PRIOR_CUMULATIVE_WEIGHT = enum.auto()
