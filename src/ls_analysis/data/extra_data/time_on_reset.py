"""
Created on 2024-05-25

@author: brassbeat
"""
import pandas as pd

from ls_analysis.data.enums import AttemptStat


def get_time_on_reset(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.Series:
    return (
        attempt_data
        [AttemptStat.ATTEMPT_TIME]
        .sub(
            segment_data
            [AttemptStat.SPLIT_TIME]
            .fillna(pd.Timedelta(seconds=0))
            .max(axis="columns")
        )
        .where(
            cond=attempt_data[AttemptStat.RUN_TIME].isna(),
            axis=0
        )
    )


def get_time_on_reset_with_last_reset(attempt_data: pd.DataFrame, segment_data: pd.DataFrame) -> pd.Series:
    def get_last_split_time(segment: int):
        try:
            return split_times.at[next(indices), segment]
        except KeyError:
            return None

    attempt_times: pd.Series = attempt_data[AttemptStat.ATTEMPT_TIME]
    segments_reset_on: pd.Series = attempt_data[AttemptStat.RESET_AT]

    possibly_last_timed_split = (
        segments_reset_on
        .sub(1)
        .mask(segments_reset_on == 1, None)
    )
    indices = iter(attempt_times.index)

    split_times: pd.DataFrame = segment_data[AttemptStat.SPLIT_TIME]
    last_recorded_splits = (
        possibly_last_timed_split
        .map(get_last_split_time)
    )
    return (
        attempt_times
        .sub(last_recorded_splits)
        .where(
            cond=attempt_times > last_recorded_splits
        )
    )

