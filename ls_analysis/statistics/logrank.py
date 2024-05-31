"""
Created on 2024-05-26

@author: brassbeat
"""
from collections.abc import Iterable

import attrs
import pandas as pd
from scipy import stats
from scipy.stats import CensoredData

from ls_analysis.data.livesplit_data import LivesplitData
from ls_analysis.statistics.core.censored_data import get_censored_segment_data


@attrs.define
class LogrankResult:
    left_uncensored: int
    left_censored: int
    right_uncensored: int
    right_censored: int
    test_statistic: float
    p_value: float


def apply_logrank(
        left: LivesplitData,
        right: LivesplitData,
        left_cutoff: pd.Timestamp = None,
        right_cutoff: pd.Timestamp = None,
):
    left_censored_data = get_censored_segment_data(left, left_cutoff)
    right_censored_data = get_censored_segment_data(right, right_cutoff)
    both_data = zip(left_censored_data, right_censored_data)
    for left_data, right_data in both_data:
        left_data: CensoredData
        right_data: CensoredData
        result = stats.logrank(left_data, right_data)

        # noinspection PyTypeChecker
        yield LogrankResult(
            left_uncensored=len(left_data) - left_data.num_censored(),
            left_censored=left_data.num_censored(),
            right_uncensored=len(right_data) - right_data.num_censored(),
            right_censored=right_data.num_censored(),
            test_statistic=result.statistic,
            p_value=result.pvalue,
        )
