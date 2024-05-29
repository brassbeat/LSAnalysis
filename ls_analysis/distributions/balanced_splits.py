# -*- coding: utf-8 -*-
"""
Created on 2024/05/29

@author: brassbeat
"""
import pandas as pd

from distributions.enums import DistributionColumn
from distributions.protocols import SegmentDistribution

_BINARY_SEARCH_TOLERANCE = 10 ** -6


def get_balanced_segments(data: SegmentDistribution, target_time: pd.Timedelta) -> pd.DataFrame:
    low_quantile, high_quantile = 0., 1.

    best_segments = data.get_quantile_times(low_quantile)[DistributionColumn.SEGMENT_TIME]
    worst_segments = data.get_quantile_times(high_quantile)[DistributionColumn.SEGMENT_TIME]

    if best_segments.sum() > target_time:
        return best_segments
    if worst_segments.sum() < target_time:
        return worst_segments

    mid_quantile = 0.5
    mid_segments = data.get_quantile_times(mid_quantile)
    mid_total_time = mid_segments[DistributionColumn.SEGMENT_TIME].sum()

    while (high_quantile - low_quantile) > _BINARY_SEARCH_TOLERANCE:
        if mid_total_time < target_time:
            low_quantile = mid_quantile
        else:
            high_quantile = mid_quantile

        mid_quantile = (high_quantile + low_quantile) / 2
        mid_segments = data.get_quantile_times(mid_quantile)
        mid_total_time = mid_segments[DistributionColumn.SEGMENT_TIME].sum()

    return mid_segments



