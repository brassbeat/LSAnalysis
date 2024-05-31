"""
Created on 2024-05-25

@author: brassbeat
"""
import pandas as pd

from ls_analysis.data.enums import AttemptStat, IndexCategory


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


def add_reset_time_to_segment_data(segment_data: pd.DataFrame, attempt_data: pd.DataFrame) -> pd.DataFrame:
    attempt_contains_reset = attempt_data[AttemptStat.RESET_AT].notna()

    attempt_times_aligned_to_segments: pd.DataFrame = (
        attempt_data
        .loc[attempt_contains_reset, [AttemptStat.RESET_AT, AttemptStat.ATTEMPT_TIME]]
        .rename(
            columns={
                AttemptStat.RESET_AT: IndexCategory.SEGMENT,
                AttemptStat.ATTEMPT_TIME: AttemptStat.RESET_TIME,
            }
        )
        .pivot(columns=IndexCategory.SEGMENT)
    )
    reset_times = (
        attempt_times_aligned_to_segments
        .sub(
            segment_data
            .loc[:, AttemptStat.SPLIT_TIME]
            .rename(columns={AttemptStat.SPLIT_TIME: AttemptStat.RESET_TIME})
            .shift(periods=1, axis="columns", fill_value=pd.Timedelta(seconds=0))
        )
    )
    return pd.concat(
        [
            segment_data,
            reset_times,
        ],
        axis=1
    )

