"""
Created on 2024-05-26

@author: brassbeat
"""
from collections.abc import Iterator

import pandas as pd
from scipy.stats import CensoredData

from ls_analysis.data.livesplit_data import LivesplitData
from ls_analysis.data.enums import AttemptStat, IndexCategory


def _reshape_resets(segments_reset_on: pd.Series, times_upon_reset: pd.Series):
    return (
        pd.DataFrame(
            data={
                IndexCategory.SEGMENT: segments_reset_on,
                times_upon_reset.name: times_upon_reset
            }
            # [segments_reset_on, times_upon_reset],
            # columns=[IndexCategory.SEGMENT, times_upon_reset.name]
        )
        .pivot(columns=IndexCategory.SEGMENT)
        .droplevel(0, axis="columns")
    )


def get_censored_segment_data(data: LivesplitData, cutoff: pd.Timestamp = None) -> Iterator[CensoredData]:
    wide_resets, segment_times = _prepare_data(data, cutoff)

    for segment in segment_times.columns.get_level_values(IndexCategory.SEGMENT):
        yield _get_censored_segment(wide_resets, segment_times, segment)


def get_single_censored_segment(data: LivesplitData, segment: int, cutoff: pd.Timestamp = None) -> CensoredData:
    wide_resets, segment_times = _prepare_data(data, cutoff)
    return _get_censored_segment(wide_resets, segment_times, segment)


def _prepare_data(data: LivesplitData, cutoff: pd.Timestamp = None):
    if cutoff:
        attempt_is_included: pd.Series = data.data[AttemptStat.START_OF_ATTEMPT, -1] >= cutoff
    else:
        attempt_is_included: pd.Series = data.data[AttemptStat.START_OF_ATTEMPT, -1].apply(lambda _: True)

    segments_reset_on = data.data[AttemptStat.RESET_AT, -1][attempt_is_included]
    times_upon_reset = data.data[AttemptStat.TIME_UPON_RESET, -1][attempt_is_included]

    # noinspection PyTypeChecker
    wide_resets = _reshape_resets(segments_reset_on, times_upon_reset)

    segment_times: pd.DataFrame = data.segment_data.loc[attempt_is_included, :]
    return wide_resets, segment_times


def _get_censored_segment(wide_resets: pd.DataFrame, segment_times: pd.DataFrame, segment: int) -> CensoredData:
    uncensored_times = (
        segment_times
        .loc[:, segment]
        .map(pd.Timedelta.total_seconds)
        .dropna())
    # noinspection PyTypeChecker
    censored_times = (
        wide_resets
        .map(pd.Timedelta.total_seconds)
        .get(segment, pd.Series(dtype="float64"))
        .dropna()
    )
    return CensoredData(
        uncensored=uncensored_times,
        right=censored_times
    )
